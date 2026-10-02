"""
Core functionality for the Phonemescape IPA library.
"""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from .data import (
    ALL_CONSONANTS, DIACRITICS, IPA_CONSONANTS, IPA_VOWELS, SUPRASEGMENTALS,
    TONE_DIACRITICS, TONE_LETTERS,
)
from .features import FEATURE_NAMES, parse_value, to_symbols
from .plotting import IPAPlotter
from .segments import Token, get_segment, tokenize
from .similarity import MouthShapeSimilarity

#: Chart attributes that ``find_phonemes_by_features`` understands.
CHART_ATTRIBUTES = ('type', 'height', 'backness', 'roundedness', 'manner', 'place',
                    'voicing', 'airstream', 'category')


class Phonemescape:
    """
    Main class for IPA segment analysis and visualization.

    - Access the IPA chart: vowels, pulmonic / other / non-pulmonic consonants
    - Tokenize transcriptions (diacritics, ties, length, stress, tone)
    - Distinctive features and natural classes
    - Articulatory similarity and clustering
    - 2D chart visualizations
    """

    def __init__(self) -> None:
        self.vowels = IPA_VOWELS
        #: All consonant symbols of the chart (pulmonic + other + non-pulmonic).
        self.consonants = ALL_CONSONANTS
        self.pulmonic_consonants = IPA_CONSONANTS
        self.plotter = IPAPlotter()
        self.similarity_calculator = MouthShapeSimilarity()
        self.graph = None

    # ------------------------------------------------------------------
    # sample graph (local Neo4j)
    # ------------------------------------------------------------------

    def connect_graph(self, **kwargs) -> 'PhonemeGraph':
        """
        Connect to the local Neo4j sample graph (see ``phonemescape.graph``).
        Keyword arguments go to :class:`PhonemeGraph` (uri, user, password,
        database, segment_threshold, sample_threshold); defaults come from
        the NEO4J_* environment variables.  Only loopback hosts are accepted.
        """
        from .graph import PhonemeGraph

        kwargs.setdefault('similarity', self.similarity_calculator)
        self.graph = PhonemeGraph(**kwargs)
        self.graph.verify()
        self.graph.setup_schema()
        return self.graph

    def add_sample(self, transcription: str, **kwargs) -> str:
        """Store a transcribed sample in the connected graph; returns its id."""
        if self.graph is None:
            raise RuntimeError("No graph connected: call connect_graph() first")
        return self.graph.add_sample(transcription, **kwargs)

    def sample_similarity(self, transcription1: str, transcription2: str) -> float:
        """Phonetic alignment similarity (0..1) of two transcriptions."""
        from .segments import segments as _segments

        a = [s.symbol for s in _segments(transcription1)]
        b = [s.symbol for s in _segments(transcription2)]
        return self.similarity_calculator.sequence_similarity(a, b)

    # ------------------------------------------------------------------
    # inventory
    # ------------------------------------------------------------------

    def get_all_phonemes(self) -> List[str]:
        """Every base symbol of the IPA chart."""
        return list(self.vowels) + list(self.consonants)

    def get_vowels(self) -> Dict[str, Tuple]:
        return self.vowels

    def get_consonants(self) -> Dict[str, Tuple]:
        return self.consonants

    def is_vowel(self, phoneme: str) -> bool:
        """True for any vowel segment, including modified ones ('aː', 'ã')."""
        return self.similarity_calculator.is_vowel(phoneme)

    def is_consonant(self, phoneme: str) -> bool:
        """True for any consonant segment, including modified ones ('tʰ', 't͡s')."""
        return self.similarity_calculator.is_consonant(phoneme)

    def get_phoneme_info(self, phoneme: str) -> Dict:
        """
        Detailed information about one segment.  Works for chart symbols and
        modified segments ('tʰ', 'ã', 't͡ʃ', 'n̩').
        """
        try:
            seg = get_segment(phoneme)
        except ValueError:
            raise ValueError(f"Phoneme '{phoneme}' not found") from None
        attrs = seg.attribute_dict
        info: Dict = {
            'symbol': seg.symbol,
            'type': seg.kind,
            'coordinates': seg.coordinates,
        }
        keys = ['height', 'backness', 'roundedness', 'diphthong'] if seg.kind == 'vowel' \
            else ['manner', 'place', 'voicing', 'airstream', 'category']
        info.update({k: attrs[k] for k in keys if k in attrs})
        info.update({
            'description': seg.description,
            'base': seg.base,
            'modifiers': list(seg.modifiers),
            'tones': list(seg.tones),
            'features': to_symbols(seg.feature_dict),
        })
        return info

    def get_distinctive_features(self, phoneme: str) -> Dict[str, str]:
        """Distinctive features of a segment as '+', '-', '0'."""
        return to_symbols(get_segment(phoneme).feature_dict)

    # ------------------------------------------------------------------
    # similarity
    # ------------------------------------------------------------------

    def find_similar_phonemes(self, target_phoneme: str,
                              phoneme_type: str = 'both',
                              top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Segments most similar to a target.

        Args:
            target_phoneme: the segment to compare against
            phoneme_type: 'vowel', 'consonant', or 'both'
            top_k: number of results
        """
        if phoneme_type == 'vowel':
            search = list(self.vowels)
        elif phoneme_type == 'consonant':
            search = list(self.consonants)
        elif phoneme_type == 'both':
            search = self.get_all_phonemes()
        else:
            raise ValueError("phoneme_type must be 'vowel', 'consonant' or 'both'")
        return self.similarity_calculator.most_similar_phonemes(target_phoneme, search, top_k)

    def calculate_similarity(self, phoneme1: str, phoneme2: str) -> float:
        return self.similarity_calculator.phoneme_similarity(phoneme1, phoneme2)

    def get_similarity_matrix(self, phonemes: List[str]) -> np.ndarray:
        return self.similarity_calculator.similarity_matrix(phonemes)

    def differing_features(self, phoneme1: str, phoneme2: str) -> Dict[str, Tuple[str, str]]:
        """The distinctive features on which two segments differ."""
        return self.similarity_calculator.differing_features(phoneme1, phoneme2)

    def get_phoneme_clusters(self, phonemes: List[str], n_clusters: int = 3) -> Dict[int, List[str]]:
        return self.similarity_calculator.cluster_phonemes(phonemes, n_clusters)

    # ------------------------------------------------------------------
    # plotting
    # ------------------------------------------------------------------

    def plot_vowel_chart(self, highlight: Optional[List[str]] = None, **kwargs) -> 'plt.Figure':
        return self.plotter.plot_vowel_chart(highlight_phonemes=highlight, **kwargs)

    def plot_consonant_chart(self, highlight: Optional[List[str]] = None, **kwargs) -> 'plt.Figure':
        return self.plotter.plot_consonant_chart(highlight_phonemes=highlight, **kwargs)

    def plot_combined_chart(self,
                            highlight_vowels: Optional[List[str]] = None,
                            highlight_consonants: Optional[List[str]] = None,
                            **kwargs) -> 'plt.Figure':
        return self.plotter.plot_combined_chart(
            highlight_vowels=highlight_vowels,
            highlight_consonants=highlight_consonants,
            **kwargs
        )

    def plot_similarity_network(self, phonemes: List[str], threshold: float = 0.5,
                                **kwargs) -> 'plt.Figure':
        matrix = self.get_similarity_matrix(phonemes)
        return self.plotter.plot_similarity_network(phonemes, matrix, threshold, **kwargs)

    # ------------------------------------------------------------------
    # transcriptions
    # ------------------------------------------------------------------

    def tokenize(self, transcription: str) -> List[Token]:
        """Split an IPA transcription into segment / prosodic / unknown tokens."""
        return tokenize(transcription)

    def analyze_word(self, word: str) -> Dict:
        """
        Analyse an IPA transcription.  Delimiters (/ / [ ] ⟨ ⟩) are ignored;
        diacritics, tie bars, length, stress, tone marks and boundaries are
        recognised.

        Returns a dict with the segments, unrecognised characters, prosodic
        tokens, counts and the mean pairwise similarity of the segments.
        """
        tokens = tokenize(word)
        segs = [t.segment for t in tokens if t.segment is not None]
        phonemes = [s.symbol for s in segs]
        invalid = [t.text for t in tokens if t.kind == 'unknown']
        prosodic = [{'symbol': t.text, 'type': t.kind, 'description': t.description}
                    for t in tokens if t.kind in ('suprasegmental', 'tone')]

        if len(phonemes) > 1:
            matrix = self.get_similarity_matrix(phonemes)
            avg = float(np.mean(matrix[np.triu_indices_from(matrix, k=1)]))
        else:
            avg = 1.0

        syllabic = [s for s in segs if s['syllabic'] == 1]
        return {
            'word': word,
            'phonemes': phonemes,
            'invalid_phonemes': invalid,
            'suprasegmentals': prosodic,
            'n_phonemes': len(phonemes),
            'n_vowels': sum(s.kind == 'vowel' for s in segs),
            'n_consonants': sum(s.kind == 'consonant' for s in segs),
            'n_syllabic': len(syllabic),
            'average_similarity': avg,
            'phoneme_details': [self.get_phoneme_info(p) for p in phonemes],
        }

    # ------------------------------------------------------------------
    # feature queries
    # ------------------------------------------------------------------

    def find_phonemes_by_features(self, **features) -> List[str]:
        """
        Chart symbols matching every given criterion.

        Criteria may be chart attributes (``type``, ``height``, ``backness``,
        ``roundedness``, ``manner``, ``place``, ``voicing``, ``airstream``,
        ``category``) and/or distinctive features with '+', '-' or '0'
        values (``sonorant='+'``, ``high='+'``).  A segment that lacks an
        attribute (e.g. ``backness`` for a consonant) does not match.
        """
        unknown = set(features) - set(CHART_ATTRIBUTES) - set(FEATURE_NAMES)
        if unknown:
            raise ValueError(f"Unknown criteria: {sorted(unknown)}")
        wanted_feats = {k: parse_value(v) for k, v in features.items() if k in FEATURE_NAMES}
        wanted_attrs = {k: v for k, v in features.items() if k in CHART_ATTRIBUTES}

        matches = []
        for symbol in self.get_all_phonemes():
            seg = get_segment(symbol)
            attrs = {'type': seg.kind, **seg.attribute_dict}
            if any(attrs.get(k) != v for k, v in wanted_attrs.items()):
                continue
            if any(seg[k] != v for k, v in wanted_feats.items()):
                continue
            matches.append(symbol)
        return matches

    def natural_class(self, **features) -> List[str]:
        """Chart symbols sharing the given distinctive-feature values,
        e.g. ``natural_class(sonorant='-', continuant='+')``."""
        bad = set(features) - set(FEATURE_NAMES)
        if bad:
            raise ValueError(f"Not distinctive features: {sorted(bad)}")
        return self.find_phonemes_by_features(**features)

    # ------------------------------------------------------------------
    # export
    # ------------------------------------------------------------------

    def export_data(self, format: str = 'dict') -> Union[Dict, str]:
        """
        Export the inventory as 'dict', 'json' or 'csv'.  The CSV holds one
        row per symbol with its chart attributes and every distinctive
        feature.
        """
        data = {
            'vowels': self.vowels,
            'consonants': self.consonants,
            'features': {s: self.get_distinctive_features(s) for s in self.get_all_phonemes()},
            'diacritics': {k: v['name'] for k, v in DIACRITICS.items()},
            'tone_diacritics': dict(TONE_DIACRITICS),
            'tone_letters': dict(TONE_LETTERS),
            'suprasegmentals': dict(SUPRASEGMENTALS),
        }
        if format == 'dict':
            return data
        if format == 'json':
            import json
            return json.dumps(data, indent=2, ensure_ascii=False)
        if format == 'csv':
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Type', 'Symbol', 'X', 'Y', 'Feature1', 'Feature2', 'Feature3',
                             'Description', *FEATURE_NAMES])
            for kind, table in (('vowel', self.vowels), ('consonant', self.consonants)):
                for symbol, (x, y, f1, f2, f3, desc) in table.items():
                    feats = data['features'][symbol]
                    writer.writerow([kind, symbol, x, y, f1, f2, f3, desc,
                                     *(feats[f] for f in FEATURE_NAMES)])
            return output.getvalue()
        raise ValueError(f"Unsupported format: {format}")
