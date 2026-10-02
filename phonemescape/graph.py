"""
Neo4j graph store for phoneme samples - LOCAL ONLY.

Every transcribed sample is stored as a node connected to the segments it
contains; segments connect to their distinctive features, to the chart
symbol they modify, and to articulatorily similar segments; samples connect
to phonetically similar samples.  The result is one graph of all samples.

Graph model
-----------
    (:Sample {id, transcription, segments, language, gloss, source, created_at})
    (:Segment {symbol, kind, base, description, modifiers, tones, features, ...})
    (:Feature {id: '+voice', name: 'voice', value: '+'})
    (:Language {code})

    (:Sample)-[:HAS_SEGMENT {index}]->(:Segment)     ordered realisation
    (:Sample)-[:IN_LANGUAGE]->(:Language)
    (:Segment)-[:HAS_FEATURE]->(:Feature)            only specified (+/-) values
    (:Segment)-[:VARIANT_OF]->(:Segment)             tʰ -> t, ã -> a, t͡ʃ -> t, ʃ
    (:Segment)-[:SIMILAR_TO {score}]->(:Segment)     score >= segment_threshold
    (:Sample)-[:SIMILAR_TO {score}]->(:Sample)       alignment score >= sample_threshold

Local only
----------
The connection URI must point at a loopback host (localhost, 127.0.0.1,
::1); anything else is refused before a connection is attempted.  Settings
come from arguments or the environment:

    NEO4J_URI       default bolt://localhost:7687
    NEO4J_USER      default neo4j
    NEO4J_PASSWORD  default phonemescape-local (matches docker-compose.yml)
    NEO4J_DATABASE  default neo4j

Requires the optional dependency: ``pip install phonemescape[graph]``.
"""

import ipaddress
import os
import uuid
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

from .features import FEATURE_NAMES, parse_value
from .segments import Segment, get_segment, inventory, tokenize
from .similarity import MouthShapeSimilarity

DEFAULT_URI = 'bolt://localhost:7687'
DEFAULT_USER = 'neo4j'
DEFAULT_PASSWORD = 'phonemescape-local'
DEFAULT_DATABASE = 'neo4j'
ALLOWED_SCHEMES = ('bolt', 'neo4j')

SCHEMA = (
    'CREATE CONSTRAINT sample_id IF NOT EXISTS FOR (s:Sample) REQUIRE s.id IS UNIQUE',
    'CREATE CONSTRAINT segment_symbol IF NOT EXISTS FOR (s:Segment) REQUIRE s.symbol IS UNIQUE',
    'CREATE CONSTRAINT feature_id IF NOT EXISTS FOR (f:Feature) REQUIRE f.id IS UNIQUE',
    'CREATE CONSTRAINT language_code IF NOT EXISTS FOR (l:Language) REQUIRE l.code IS UNIQUE',
)


def ensure_local_uri(uri: str) -> str:
    """Return ``uri`` if it targets a loopback host; raise ValueError otherwise."""
    parsed = urlparse(uri)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Unsupported scheme {parsed.scheme!r}: use bolt:// or neo4j:// "
                         "(unencrypted local connection)")
    host = parsed.hostname or ''
    if host == 'localhost':
        return uri
    try:
        if ipaddress.ip_address(host).is_loopback:
            return uri
    except ValueError:
        pass
    raise ValueError(f"Refusing non-local Neo4j host {host!r}: Phonemescape's graph store "
                     "runs against a local database only (localhost / 127.0.0.1 / ::1)")


def _segment_row(seg: Segment) -> Dict[str, Any]:
    attrs = seg.attribute_dict
    return {
        'symbol': seg.symbol,
        'props': {
            'kind': seg.kind,
            'base': seg.base,
            'parts': list(seg.parts),
            'description': seg.description,
            'modifiers': list(seg.modifiers),
            'tones': list(seg.tones),
            'features': list(seg.features),
            'x': seg.coordinates[0],
            'y': seg.coordinates[1],
            **attrs,
        },
        'features': [{'id': f"{'+' if v > 0 else '-'}{name}", 'name': name,
                      'value': '+' if v > 0 else '-'}
                     for name, v in zip(FEATURE_NAMES, seg.features) if v != 0],
        'bases': sorted({p for p in seg.parts if p != seg.symbol}),
    }


class PhonemeGraph:
    """Store phoneme samples in a local Neo4j database as one connected graph."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None,
                 password: Optional[str] = None, database: Optional[str] = None,
                 similarity: Optional[MouthShapeSimilarity] = None,
                 segment_threshold: float = 0.85, sample_threshold: float = 0.6):
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise ImportError("The graph store needs the neo4j driver: "
                              "pip install 'phonemescape[graph]'") from exc
        self.uri = ensure_local_uri(uri or os.environ.get('NEO4J_URI', DEFAULT_URI))
        self.database = database or os.environ.get('NEO4J_DATABASE', DEFAULT_DATABASE)
        auth = (user or os.environ.get('NEO4J_USER', DEFAULT_USER),
                password or os.environ.get('NEO4J_PASSWORD', DEFAULT_PASSWORD))
        self.similarity = similarity or MouthShapeSimilarity()
        self.segment_threshold = segment_threshold
        self.sample_threshold = sample_threshold
        self._driver = GraphDatabase.driver(self.uri, auth=auth)

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._driver.close()

    def __enter__(self) -> 'PhonemeGraph':
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _run(self, query: str, **params: Any) -> List[Dict[str, Any]]:
        records, _, _ = self._driver.execute_query(query, params, database_=self.database)
        return [r.data() for r in records]

    def verify(self) -> None:
        """Raise if the local database is unreachable."""
        self._driver.verify_connectivity()

    def setup_schema(self) -> None:
        """Create uniqueness constraints (idempotent)."""
        for statement in SCHEMA:
            self._run(statement)

    # ------------------------------------------------------------------
    # segments
    # ------------------------------------------------------------------

    def _merge_segments(self, segs: Iterable[Segment]) -> List[str]:
        """MERGE segments (with features, base links and similarity edges).
        Returns the symbols that were new to the graph."""
        unique = {s.symbol: s for s in segs}
        # Base chart symbols of modified segments must exist for VARIANT_OF.
        for seg in list(unique.values()):
            for part in seg.parts:
                if part not in unique:
                    unique[part] = get_segment(part)
        existing = {r['symbol'] for r in self._run(
            'MATCH (s:Segment) WHERE s.symbol IN $symbols RETURN s.symbol AS symbol',
            symbols=list(unique))}
        new = [s for s in unique.values() if s.symbol not in existing]
        if not new:
            return []
        self._run("""
            UNWIND $rows AS row
            MERGE (s:Segment {symbol: row.symbol})
            SET s += row.props
            WITH s, row
            UNWIND row.features AS f
            MERGE (feat:Feature {id: f.id}) SET feat.name = f.name, feat.value = f.value
            MERGE (s)-[:HAS_FEATURE]->(feat)
        """, rows=[_segment_row(s) for s in new])
        self._run("""
            UNWIND $rows AS row
            MATCH (s:Segment {symbol: row.symbol})
            UNWIND row.bases AS b
            MATCH (base:Segment {symbol: b})
            MERGE (s)-[:VARIANT_OF]->(base)
        """, rows=[_segment_row(s) for s in new])

        # Similarity edges: new x (all segments in the graph).
        all_symbols = [r['symbol'] for r in self._run(
            'MATCH (s:Segment) RETURN s.symbol AS symbol')]
        new_symbols = {s.symbol for s in new}
        pairs = []
        for a in new_symbols:
            for b in all_symbols:
                if a == b or (b in new_symbols and b < a):
                    continue
                score = self.similarity.phoneme_similarity(a, b)
                if score >= self.segment_threshold:
                    pairs.append({'a': a, 'b': b, 'score': round(score, 4)})
        if pairs:
            self._run("""
                UNWIND $pairs AS p
                MATCH (a:Segment {symbol: p.a}), (b:Segment {symbol: p.b})
                MERGE (a)-[r:SIMILAR_TO]-(b)
                SET r.score = p.score
            """, pairs=pairs)
        return sorted(new_symbols)

    def load_inventory(self) -> int:
        """Add every IPA chart symbol as a Segment node.  Returns how many were new."""
        self.setup_schema()
        return len(self._merge_segments(inventory().values()))

    # ------------------------------------------------------------------
    # samples
    # ------------------------------------------------------------------

    def add_sample(self, transcription: str, sample_id: Optional[str] = None,
                   language: Optional[str] = None, gloss: Optional[str] = None,
                   source: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Tokenize a transcription and store it as a Sample connected to its
        segments and to every similar existing sample.  Returns the sample id.
        Raises ValueError if the transcription contains unrecognised symbols.
        """
        tokens = tokenize(transcription)
        unknown = [t.text for t in tokens if t.kind == 'unknown']
        if unknown:
            raise ValueError(f"Unrecognised symbols in {transcription!r}: {unknown}")
        segs = [t.segment for t in tokens if t.segment is not None]
        if not segs:
            raise ValueError(f"No segments in {transcription!r}")
        sample_id = sample_id or str(uuid.uuid4())
        symbols = [s.symbol for s in segs]

        self.setup_schema()
        self._merge_segments(segs)
        props = {
            'transcription': transcription,
            'segments': symbols,
            'prosody': [t.text for t in tokens if t.kind in ('suprasegmental', 'tone')],
            'created_at': datetime.now(timezone.utc).isoformat(),
            **{k: v for k, v in (('language', language), ('gloss', gloss),
                                 ('source', source)) if v is not None},
            **(metadata or {}),
        }
        self._run("""
            CREATE (s:Sample {id: $id}) SET s += $props
            WITH s
            UNWIND range(0, size($symbols) - 1) AS i
            MATCH (seg:Segment {symbol: $symbols[i]})
            CREATE (s)-[:HAS_SEGMENT {index: i}]->(seg)
        """, id=sample_id, props=props, symbols=symbols)
        if language:
            self._run("""
                MATCH (s:Sample {id: $id})
                MERGE (l:Language {code: $language})
                MERGE (s)-[:IN_LANGUAGE]->(l)
            """, id=sample_id, language=language)
        self._link_similar_samples(sample_id, symbols)
        return sample_id

    def add_samples(self, samples: Iterable[Any]) -> List[str]:
        """Add many samples: strings or dicts of ``add_sample`` keyword args."""
        ids = []
        for sample in samples:
            if isinstance(sample, str):
                ids.append(self.add_sample(sample))
            else:
                ids.append(self.add_sample(**sample))
        return ids

    def _link_similar_samples(self, sample_id: str, symbols: List[str]) -> None:
        others = self._run('MATCH (s:Sample) WHERE s.id <> $id '
                           'RETURN s.id AS id, s.segments AS segments', id=sample_id)
        links = []
        for other in others:
            score = self.similarity.sequence_similarity(symbols, other['segments'])
            if score >= self.sample_threshold:
                links.append({'other': other['id'], 'score': round(score, 4)})
        if links:
            self._run("""
                MATCH (s:Sample {id: $id})
                UNWIND $links AS l
                MATCH (o:Sample {id: l.other})
                MERGE (s)-[r:SIMILAR_TO]-(o)
                SET r.score = l.score
            """, id=sample_id, links=links)

    def relink_samples(self) -> int:
        """Recompute every Sample-Sample similarity edge (e.g. after changing
        ``sample_threshold``).  Returns the number of edges."""
        self._run('MATCH (:Sample)-[r:SIMILAR_TO]-(:Sample) DELETE r')
        rows = self._run('MATCH (s:Sample) RETURN s.id AS id, s.segments AS segments')
        links = []
        for a, b in combinations(rows, 2):
            score = self.similarity.sequence_similarity(a['segments'], b['segments'])
            if score >= self.sample_threshold:
                links.append({'a': a['id'], 'b': b['id'], 'score': round(score, 4)})
        if links:
            self._run("""
                UNWIND $links AS l
                MATCH (a:Sample {id: l.a}), (b:Sample {id: l.b})
                MERGE (a)-[r:SIMILAR_TO]-(b) SET r.score = l.score
            """, links=links)
        return len(links)

    def delete_sample(self, sample_id: str) -> None:
        """Delete one sample and its relationships (segments are kept)."""
        self._run('MATCH (s:Sample {id: $id}) DETACH DELETE s', id=sample_id)

    def delete_all(self) -> None:
        """Delete EVERY node and relationship in the configured database."""
        self._run('MATCH (n) DETACH DELETE n')

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------

    def get_sample(self, sample_id: str) -> Optional[Dict[str, Any]]:
        rows = self._run('MATCH (s:Sample {id: $id}) RETURN properties(s) AS sample',
                         id=sample_id)
        return rows[0]['sample'] if rows else None

    def similar_samples(self, sample_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Samples linked to ``sample_id`` by SIMILAR_TO, best first."""
        return self._run("""
            MATCH (:Sample {id: $id})-[r:SIMILAR_TO]-(o:Sample)
            RETURN o.id AS id, o.transcription AS transcription, r.score AS score
            ORDER BY score DESC LIMIT $limit
        """, id=sample_id, limit=limit)

    def samples_with_segment(self, symbol: str, include_variants: bool = True) -> List[Dict[str, Any]]:
        """Samples containing a segment (and, by default, its modified variants:
        searching 't' also finds 'tʰ')."""
        seg = get_segment(symbol)
        query = """
            MATCH (target:Segment {symbol: $symbol})
            MATCH (s:Sample)-[:HAS_SEGMENT]->(seg:Segment)
            WHERE seg = target OR ($variants AND (seg)-[:VARIANT_OF]->(target))
            RETURN DISTINCT s.id AS id, s.transcription AS transcription
            ORDER BY id
        """
        return self._run(query, symbol=seg.symbol, variants=include_variants)

    def samples_in_natural_class(self, **features: Any) -> List[Dict[str, Any]]:
        """Samples containing at least one segment with all the given
        feature values, e.g. ``samples_in_natural_class(nasal='+', voice='-')``."""
        bad = set(features) - set(FEATURE_NAMES)
        if bad:
            raise ValueError(f"Not distinctive features: {sorted(bad)}")
        ids = []
        for name, value in features.items():
            v = parse_value(value)
            if v == 0:
                raise ValueError("Query specified values ('+' or '-') only")
            ids.append(f"{'+' if v > 0 else '-'}{name}")
        return self._run("""
            MATCH (s:Sample)-[:HAS_SEGMENT]->(seg:Segment)
            WHERE all(fid IN $ids WHERE (seg)-[:HAS_FEATURE]->(:Feature {id: fid}))
            RETURN s.id AS id, s.transcription AS transcription,
                   collect(DISTINCT seg.symbol) AS matching_segments
            ORDER BY id
        """, ids=ids)

    def segment_frequencies(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Occurrences of each segment across samples (optionally one language)."""
        return self._run("""
            MATCH (s:Sample)-[:HAS_SEGMENT]->(seg:Segment)
            WHERE $language IS NULL OR s.language = $language
            RETURN seg.symbol AS symbol, count(*) AS count
            ORDER BY count DESC, symbol
        """, language=language)

    def stats(self) -> Dict[str, int]:
        """Node and relationship counts."""
        row = self._run("""
            CALL () { MATCH (n:Sample) RETURN count(n) AS samples }
            CALL () { MATCH (n:Segment) RETURN count(n) AS segments }
            CALL () { MATCH (n:Feature) RETURN count(n) AS features }
            CALL () { MATCH (n:Language) RETURN count(n) AS languages }
            CALL () { MATCH ()-[r:HAS_SEGMENT]->() RETURN count(r) AS occurrences }
            CALL () { MATCH (:Sample)-[r:SIMILAR_TO]-(:Sample) RETURN count(r) / 2 AS sample_links }
            CALL () { MATCH (:Segment)-[r:SIMILAR_TO]-(:Segment) RETURN count(r) / 2 AS segment_links }
            RETURN samples, segments, features, languages, occurrences, sample_links, segment_links
        """)[0]
        return {k: int(v) for k, v in row.items()}
