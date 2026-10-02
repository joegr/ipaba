"""
Distinctive features for IPA segments.

The feature set follows the binary system of Hayes (2009, *Introductory
Phonology*, ch. 4), itself descended from Chomsky & Halle (1968), with
[velaric] for clicks (as in PanPhon, Mortensen et al. 2016) and [long] for
quantity.  Values: +1 (+), -1 (-), 0 (unspecified / not applicable).

Features are *derived* from each symbol's chart description (height,
backness, rounding; manner, place, voicing) by explicit rules rather than
typed in by hand, so every segment is specified consistently and every
value can be traced to a rule below.

Conventions worth knowing:

* Place is organised by articulator (feature geometry): [labial],
  [coronal] and [dorsal] are the articulator features; [round] and
  [labiodental] depend on [labial]; [anterior], [distributed] depend on
  [coronal]; [high], [low], [front], [back] depend on [dorsal] (vowels
  are [+dorsal]).  Dependents are 0 when their articulator is absent, except
  [round], which is specified for every segment.
* Palatals are dorsal ([+high, +front]), the analysis of Hayes (2009).
* Laryngeals (h ɦ ʔ) are [-consonantal]: they have no oral constriction.
* [delayed release] is specified only for non-continuant obstruents
  (stops - affricates); [strident] only for coronal obstruents;
  [tense] only for vowels.
* Vowels and consonants share ONE feature space, so natural classes and
  similarity cross the vowel/consonant divide (i ~ j, u ~ w, y ~ ɥ, ɯ ~ ɰ
  differ only in [syllabic]).
"""

from typing import Dict, Tuple

FEATURE_NAMES: Tuple[str, ...] = (
    # Major class
    'syllabic', 'consonantal', 'sonorant',
    # Manner
    'continuant', 'delayed_release', 'approximant', 'tap', 'trill',
    'nasal', 'lateral', 'strident',
    # Laryngeal
    'voice', 'spread_glottis', 'constricted_glottis',
    # Place: labial
    'labial', 'round', 'labiodental',
    # Place: coronal
    'coronal', 'anterior', 'distributed',
    # Place: dorsal
    'dorsal', 'high', 'low', 'front', 'back', 'tense',
    # Other
    'long', 'velaric',
)

#: Short labels for compact tables (Hayes / PanPhon abbreviations).
FEATURE_ABBREVIATIONS: Dict[str, str] = {
    'syllabic': 'syl', 'consonantal': 'cons', 'sonorant': 'son',
    'continuant': 'cont', 'delayed_release': 'delrel', 'approximant': 'approx',
    'tap': 'tap', 'trill': 'trill', 'nasal': 'nas', 'lateral': 'lat',
    'strident': 'strid', 'voice': 'voi', 'spread_glottis': 'sg',
    'constricted_glottis': 'cg', 'labial': 'lab', 'round': 'round',
    'labiodental': 'labdent', 'coronal': 'cor', 'anterior': 'ant',
    'distributed': 'distr', 'dorsal': 'dor', 'high': 'hi', 'low': 'lo',
    'front': 'front', 'back': 'back', 'tense': 'tense', 'long': 'long',
    'velaric': 'velaric',
}

FeatureBundle = Dict[str, int]

LABIAL_DEPENDENTS = ('labiodental',)
CORONAL_DEPENDENTS = ('anterior', 'distributed')
DORSAL_DEPENDENTS = ('high', 'low', 'front', 'back')

#: Coronal places whose fricatives/affricates are sibilant ([+strident]).
SIBILANT_PLACES = frozenset({
    'alveolar', 'postalveolar', 'palatoalveolar', 'retroflex',
    'alveolo-palatal', 'postalveolar-velar',
})


def blank() -> FeatureBundle:
    """A bundle with every feature unspecified."""
    return {name: 0 for name in FEATURE_NAMES}


def to_symbols(bundle: FeatureBundle) -> Dict[str, str]:
    """Render a bundle as '+', '-', '0' strings."""
    return {k: {1: '+', -1: '-', 0: '0'}[bundle[k]] for k in FEATURE_NAMES}


def parse_value(value) -> int:
    """Accept '+', '-', '0', True, False, 1, -1, 0."""
    if isinstance(value, bool):
        return 1 if value else -1
    if isinstance(value, (int, float)):
        return int(value > 0) - int(value < 0)
    mapping = {'+': 1, '-': -1, '−': -1, '0': 0}
    if value in mapping:
        return mapping[value]
    raise ValueError(f"Invalid feature value {value!r}; use '+', '-' or '0'")


# =============================================================================
# VOWELS
# =============================================================================

def vowel_features(height: str, backness: str, roundedness: str) -> FeatureBundle:
    f = blank()
    f.update(syllabic=1, consonantal=-1, sonorant=1, continuant=1, approximant=1,
             tap=-1, trill=-1, nasal=-1, lateral=-1, voice=1, spread_glottis=-1,
             constricted_glottis=-1, coronal=-1, dorsal=1, long=-1, velaric=-1)
    if roundedness == 'rounded':
        f.update(labial=1, round=1, labiodental=-1)
    elif roundedness == 'unrounded':
        f.update(labial=-1, round=-1)
    else:  # unspecified on the chart (ə, ɐ)
        f.update(labial=-1, round=0)
    f['high'] = 1 if height in ('close', 'near-close') else -1
    f['low'] = 1 if height in ('near-open', 'open') else -1
    f['front'] = 1 if backness in ('front', 'near-front') else -1
    f['back'] = 1 if backness in ('back', 'near-back') else -1
    # Tense/lax (~ATR): peripheral close and close-mid vowels are tense; the
    # near-close, mid, open-mid and near-open vowels are lax; [tense] is not
    # defined for fully open vowels.
    if height in ('close', 'close-mid'):
        f['tense'] = 1
    elif height == 'open':
        f['tense'] = 0
    else:
        f['tense'] = -1
    return f


# =============================================================================
# CONSONANTS
# =============================================================================

def _place_features(place: str) -> FeatureBundle:
    """Articulator features for a place of articulation."""
    f: FeatureBundle = {'labial': -1, 'round': -1, 'coronal': -1, 'dorsal': -1}

    def dorsal(high: int, low: int, front: int, back: int) -> None:
        f.update(dorsal=1, high=high, low=low, front=front, back=back)

    if place in ('bilabial', 'labiodental', 'linguolabial'):
        f.update(labial=1, labiodental=1 if place == 'labiodental' else -1)
        if place == 'linguolabial':
            f.update(coronal=1, anterior=1, distributed=-1)
    elif place == 'dental':
        f.update(coronal=1, anterior=1, distributed=1)
    elif place == 'alveolar':
        f.update(coronal=1, anterior=1, distributed=-1)
    elif place in ('postalveolar', 'palatoalveolar'):
        f.update(coronal=1, anterior=-1, distributed=1)
    elif place == 'retroflex':
        f.update(coronal=1, anterior=-1, distributed=-1)
    elif place == 'alveolo-palatal':
        f.update(coronal=1, anterior=-1, distributed=1)
        dorsal(1, -1, 1, -1)
    elif place == 'palatal':
        dorsal(1, -1, 1, -1)
    elif place == 'velar':
        dorsal(1, -1, -1, 1)
    elif place == 'uvular':
        dorsal(-1, -1, -1, 1)
    elif place in ('pharyngeal', 'epiglottal'):
        dorsal(-1, 1, -1, 1)
    elif place == 'glottal':
        pass
    elif place == 'labial-velar':
        f.update(labial=1, round=1, labiodental=-1)
        dorsal(1, -1, -1, 1)
    elif place == 'labial-palatal':
        f.update(labial=1, round=1, labiodental=-1)
        dorsal(1, -1, 1, -1)
    elif place == 'postalveolar-velar':
        f.update(coronal=1, anterior=-1, distributed=1)
        dorsal(1, -1, -1, 1)
    else:
        raise ValueError(f"Unknown place of articulation: {place}")
    return f


def consonant_features(manner: str, place: str, voicing: str) -> FeatureBundle:
    f = blank()
    f.update(syllabic=-1, consonantal=1, sonorant=-1, continuant=-1, approximant=-1,
             tap=-1, trill=-1, nasal=-1, lateral=-1, spread_glottis=-1,
             constricted_glottis=-1, long=-1, velaric=-1)
    f['voice'] = 1 if voicing == 'voiced' else -1

    lateral = manner.startswith('lateral-')
    base_manner = manner[len('lateral-'):] if lateral else manner
    f['lateral'] = 1 if lateral else -1

    if base_manner == 'plosive':
        f['delayed_release'] = -1
    elif base_manner == 'affricate':
        f['delayed_release'] = 1
    elif base_manner == 'nasal':
        f.update(sonorant=1, nasal=1)
    elif base_manner == 'trill':
        f.update(sonorant=1, continuant=1, approximant=1, trill=1)
    elif base_manner == 'tap':
        f.update(sonorant=1, continuant=1, approximant=1, tap=1)
    elif base_manner == 'fricative':
        f['continuant'] = 1
    elif base_manner == 'approximant':
        f.update(sonorant=1, continuant=1, approximant=1)
    elif base_manner == 'implosive':
        f.update(delayed_release=-1, constricted_glottis=1)
    elif base_manner == 'click':
        f.update(delayed_release=-1, velaric=1)
    else:
        raise ValueError(f"Unknown manner of articulation: {manner}")

    f.update(_place_features(place))

    if base_manner == 'click':
        # Every click has a dorsal (velar/uvular) rear closure.
        f.update(dorsal=1, high=1, low=-1, front=-1, back=1)

    # Central approximants without a coronal constriction are glides:
    # [-consonantal] (j ɰ w ɥ ʋ).  Coronal approximants (ɹ ɻ) are liquids.
    if base_manner == 'approximant' and not lateral and f['coronal'] != 1:
        f['consonantal'] = -1

    # Laryngeals have no oral constriction.
    if place == 'glottal':
        f['consonantal'] = -1
        if base_manner == 'plosive':
            f['constricted_glottis'] = 1          # ʔ
        else:
            f['spread_glottis'] = 1               # h ɦ

    # [strident] is defined only for coronal obstruent continuants/affricates.
    obstruent = f['sonorant'] == -1
    if f['coronal'] == 1 and obstruent:
        sibilant = (place in SIBILANT_PLACES and not lateral
                    and (f['continuant'] == 1 or f['delayed_release'] == 1))
        f['strident'] = 1 if sibilant else -1

    return normalize(f)


def normalize(f: FeatureBundle) -> FeatureBundle:
    """Zero out dependents whose articulator is absent (feature geometry)."""
    if f['labial'] != 1:
        for k in LABIAL_DEPENDENTS:
            f[k] = 0
    if f['coronal'] != 1:
        for k in CORONAL_DEPENDENTS:
            f[k] = 0
    if f['dorsal'] != 1:
        for k in DORSAL_DEPENDENTS:
            f[k] = 0
    if f['sonorant'] == 1 or f['syllabic'] == 1:
        f['delayed_release'] = 0
    elif f['continuant'] == 1:
        f['delayed_release'] = 0
    if f['syllabic'] != 1:
        f['tense'] = 0
    return f


# =============================================================================
# COMPLEX SEGMENTS (tie bars)
# =============================================================================

def merge_articulators(first: FeatureBundle, second: FeatureBundle) -> FeatureBundle:
    """
    Combine the place features of a doubly articulated segment (k͡p, ŋ͡m):
    each articulator present in either part is kept with its dependents.
    """
    f = dict(first)
    groups = (('labial', ('round',) + LABIAL_DEPENDENTS),
              ('coronal', CORONAL_DEPENDENTS),
              ('dorsal', DORSAL_DEPENDENTS))
    for articulator, dependents in groups:
        if second[articulator] == 1 and first[articulator] != 1:
            f[articulator] = 1
            for k in dependents:
                f[k] = second[k]
    return normalize(f)


def affricate_features(stop: FeatureBundle, fricative: FeatureBundle) -> FeatureBundle:
    """A stop + fricative contour: the fricative's place/laryngeal features
    with [-continuant, +delayed release]."""
    f = dict(fricative)
    f.update(continuant=-1, delayed_release=1)
    if stop['voice'] != fricative['voice']:
        f['voice'] = stop['voice']
    for k in ('spread_glottis', 'constricted_glottis'):
        f[k] = max(stop[k], fricative[k])
    if f['coronal'] == 1:
        f['strident'] = fricative['strident']
    return normalize(f)
