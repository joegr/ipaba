import json

import numpy as np
import pytest

import phonemescape as pm
from phonemescape.data import (
    IPA_CONSONANTS, IPA_VOWELS, VOWEL_TRAPEZOID, vowel_back_edge, vowel_front_edge,
)
from phonemescape.segments import get_segment, tokenize


@pytest.fixture(scope='module')
def ipa():
    return pm.Phonemescape()


# --- inventory ---------------------------------------------------------------

def test_chart_counts():
    assert len(IPA_VOWELS) == 28
    assert len(IPA_CONSONANTS) == 59
    assert len(pm.IPA_OTHER_CONSONANTS) == 10
    assert len(pm.IPA_NON_PULMONIC) == 10


def test_ipa_script_g():
    assert 'ɡ' in IPA_CONSONANTS and 'g' not in IPA_CONSONANTS
    assert get_segment('g').symbol == 'ɡ'


def test_vowels_inside_trapezoid():
    for symbol, (x, y, *_rest) in IPA_VOWELS.items():
        assert 0 <= y <= 3
        assert vowel_front_edge(y) - 0.1 <= x <= vowel_back_edge(y) + 0.1, symbol


def test_trapezoid_shape():
    (x0, _), (x1, _), (x2, _), (x3, _) = VOWEL_TRAPEZOID
    assert x2 == x1                                   # vertical back edge
    assert (x2 - x3) == pytest.approx((x1 - x0) / 2)  # open row half as wide


def test_rounding_pairs_unrounded_left():
    for u, r in [('i', 'y'), ('e', 'ø'), ('ɛ', 'œ'), ('a', 'ɶ'), ('ɯ', 'u'),
                 ('ɤ', 'o'), ('ʌ', 'ɔ'), ('ɑ', 'ɒ'), ('ɨ', 'ʉ'), ('ɪ', 'ʏ')]:
        assert IPA_VOWELS[u][0] < IPA_VOWELS[r][0]
        assert IPA_VOWELS[u][1] == IPA_VOWELS[r][1]


def test_voiced_right_of_voiceless():
    for vl, vd in [('p', 'b'), ('s', 'z'), ('x', 'ɣ'), ('ɬ', 'ɮ')]:
        assert IPA_CONSONANTS[vl][0] < IPA_CONSONANTS[vd][0]
    assert IPA_CONSONANTS['m'][0] == IPA_CONSONANTS['b'][0]  # voiced sonorant: right half


def test_back_vowels_share_column():
    assert IPA_VOWELS['ʌ'][0] == IPA_VOWELS['ɤ'][0] == IPA_VOWELS['ɑ'][0] == IPA_VOWELS['ɯ'][0]


# --- tokenizer ----------------------------------------------------------------

@pytest.mark.parametrize('text,expected', [
    ('kæt', ['k', 'æ', 't']),
    ('/ˈhjuːmən/', ['h', 'j', 'uː', 'm', 'ə', 'n']),
    ('[kʰæt]', ['kʰ', 'æ', 't']),
    ('t͡ʃiːz', ['t͡ʃ', 'iː', 'z']),
    ('ʧiz', ['t͡ʃ', 'i', 'z']),
    ('bɝd', ['b', 'ɜ˞', 'd']),
    ('ⁿdaba', ['ⁿd', 'a', 'b', 'a']),
    ('ɡɪ:v', ['ɡ', 'ɪː', 'v']),
    ('fɑ̃', ['f', 'ɑ̃']),
    ('ç', ['ç']),
    ('k͡pa', ['k͡p', 'a']),
])
def test_tokenize_segments(text, expected):
    assert [s.symbol for s in pm.segments(text)] == expected


def test_prosodic_tokens():
    kinds = [(t.text, t.kind) for t in tokenize('ˈma˥˩ ta.ka')]
    assert ('ˈ', 'suprasegmental') in kinds
    assert ('˥˩', 'tone') in kinds
    assert (' ', 'boundary') in kinds
    assert ('.', 'suprasegmental') in kinds


def test_unknown_characters(ipa):
    assert ipa.analyze_word('ka?')['invalid_phonemes'] == ['?']


# --- segments & features ------------------------------------------------------

def test_modified_descriptions():
    assert get_segment('tʰ').description == 'Voiceless alveolar plosive, aspirated'
    assert get_segment('ŋ̊').description == 'Voiceless velar nasal'
    assert get_segment('t͡s').description == 'Voiceless alveolar sibilant affricate'
    assert get_segment('k͡p').attribute_dict['place'] == 'labial-velar'
    assert get_segment('kʼ').attribute_dict['airstream'] == 'glottalic egressive'


def test_feature_values():
    f = get_segment
    assert f('n̩')['syllabic'] == 1
    assert f('ã')['nasal'] == 1
    assert f('ɹ̝')['sonorant'] == -1          # raised approximant -> fricative
    assert f('β̞')['sonorant'] == 1           # lowered fricative -> approximant
    assert f('s')['strident'] == 1 and f('θ')['strident'] == -1
    assert f('h')['consonantal'] == -1 and f('h')['spread_glottis'] == 1
    assert f('ʔ')['constricted_glottis'] == 1
    assert f('ǃ')['velaric'] == 1
    assert f('j')['consonantal'] == -1 and f('ɹ')['consonantal'] == 1


def test_glides_and_vowels_differ_in_syllabic_only(ipa):
    for v, g in [('i', 'j'), ('u', 'w'), ('y', 'ɥ'), ('ɯ', 'ɰ')]:
        diff = ipa.differing_features(v, g)
        assert 'syllabic' in diff
        assert set(diff) <= {'syllabic', 'tense'}


# --- similarity ---------------------------------------------------------------

def test_similarity_properties(ipa):
    phones = ['p', 'b', 'm', 'i', 'j', 'a', 'tʰ']
    m = ipa.get_similarity_matrix(phones)
    assert np.allclose(m, m.T)
    assert np.allclose(np.diag(m), 1)
    assert ((m >= 0) & (m <= 1)).all()


def test_similarity_ordering(ipa):
    s = ipa.calculate_similarity
    assert s('p', 'b') > s('p', 'm') > s('p', 'l')
    assert s('i', 'e') > s('i', 'a')
    assert s('i', 'j') > s('i', 'p')
    assert s('t', 'tʰ') > s('t', 'd') * 0.9


def test_cross_plane_distance(ipa):
    sim = ipa.similarity_calculator
    assert sim.mouth_shape_distance('i', 'p') == float('inf')
    assert sim.articulatory_feature_distance('i', 'j') < sim.articulatory_feature_distance('i', 'p')


def test_sequence_similarity(ipa):
    assert ipa.sample_similarity('kæt', 'kæt') == 1
    assert ipa.sample_similarity('kæt', 'bæt') > ipa.sample_similarity('kæt', 'ʃuː')


def test_unknown_raises(ipa):
    with pytest.raises(ValueError):
        ipa.calculate_similarity('p', '?')


# --- queries ------------------------------------------------------------------

def test_find_by_features_is_strict(ipa):
    front = ipa.find_phonemes_by_features(backness='front')
    assert front and all(ipa.is_vowel(p) for p in front)
    assert ipa.find_phonemes_by_features(manner='plosive', voicing='voiceless') == \
        ['p', 't', 'ʈ', 'c', 'k', 'q', 'ʔ', 'ʡ']


def test_natural_class(ipa):
    assert ipa.natural_class(nasal='+', syllabic='-') == ['m', 'ɱ', 'n', 'ɳ', 'ɲ', 'ŋ', 'ɴ']
    sibilants = ipa.natural_class(strident='+')
    assert {'s', 'z', 'ʃ', 'ʒ'} <= set(sibilants) and 'θ' not in sibilants


def test_clusters(ipa):
    clusters = ipa.get_phoneme_clusters(['i', 'e', 'u', 'o', 'p', 't', 'k'], 2)
    groups = sorted(sorted(v) for v in clusters.values())
    assert groups == [['e', 'i', 'o', 'u'], ['k', 'p', 't']]


def test_phoneme_info(ipa):
    info = ipa.get_phoneme_info('i')
    assert info['description'] == 'Close front unrounded vowel'
    assert info['coordinates'] == IPA_VOWELS['i'][:2]
    assert info['features']['high'] == '+'
    with pytest.raises(ValueError):
        ipa.get_phoneme_info('?')


def test_export(ipa):
    data = json.loads(ipa.export_data('json'))
    assert data['features']['p']['voice'] == '-'
    assert ipa.export_data('csv').splitlines()[0].startswith('Type,Symbol')


def test_cli(capsys):
    from phonemescape.cli import main
    assert main(['compare', 'p', 'b']) == 0
    assert '"voice"' in capsys.readouterr().out
    assert main(['info', '?']) == 1
