"""Integration tests against a LOCAL Neo4j (docker compose up -d).
Skipped when no database is reachable.  Only touches samples it creates."""

import uuid

import pytest

neo4j = pytest.importorskip('neo4j')

from phonemescape.graph import PhonemeGraph, ensure_local_uri  # noqa: E402

pytestmark = pytest.mark.neo4j


def test_local_only_guard():
    assert ensure_local_uri('bolt://localhost:7687')
    assert ensure_local_uri('bolt://127.0.0.1:7687')
    assert ensure_local_uri('neo4j://[::1]:7687')
    for uri in ('bolt://example.com:7687', 'neo4j+s://x.databases.neo4j.io',
                'bolt://10.0.0.5:7687', 'http://localhost:7474'):
        with pytest.raises(ValueError):
            ensure_local_uri(uri)


@pytest.fixture(scope='module')
def graph():
    try:
        g = PhonemeGraph(sample_threshold=0.5)
        g.verify()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f'no local Neo4j: {exc}')
    g.setup_schema()
    yield g
    g.close()


@pytest.fixture
def ids(graph):
    prefix = f'test-{uuid.uuid4().hex[:8]}-'
    made = []

    def add(transcription, **kw):
        sid = graph.add_sample(transcription, sample_id=prefix + str(len(made)), **kw)
        made.append(sid)
        return sid

    yield add
    for sid in made:
        graph.delete_sample(sid)


def test_sample_roundtrip(graph, ids):
    a = ids('/kʰæt/', language='en', gloss='cat')
    b = ids('/bæt/', language='en', gloss='bat')
    sample = graph.get_sample(a)
    assert sample['segments'] == ['kʰ', 'æ', 't']
    assert any(r['id'] == b for r in graph.similar_samples(a))
    with_k = {r['id'] for r in graph.samples_with_segment('k')}
    assert a in with_k                                  # via VARIANT_OF kʰ -> k
    assert a not in {r['id'] for r in graph.samples_with_segment('k', include_variants=False)}


def test_natural_class_query(graph, ids):
    a = ids('/ma/')
    b = ids('/pa/')
    found = {r['id'] for r in graph.samples_in_natural_class(nasal='+')}
    assert a in found and b not in found


def test_rejects_unknown_symbols(graph):
    with pytest.raises(ValueError):
        graph.add_sample('ka?')
