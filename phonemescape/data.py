"""
IPA segment inventory, chart geometry and symbol tables.

Source of truth: the International Phonetic Alphabet chart (IPA, 2020
revision): pulmonic consonants, non-pulmonic consonants, other symbols,
vowels, diacritics, suprasegmentals and tones & word accents.

A note on terminology
---------------------
IPA symbols denote *phones* (speech sounds); a *phoneme* is a contrastive
unit of one particular language, written between slashes (/t/), while a
phone is written in square brackets ([tʰ]).  This library works with the
language-independent IPA segments; the public API keeps the historical name
"phoneme" for backwards compatibility.

Chart geometry
--------------
Vowels and consonants live on SEPARATE display planes.

VOWEL PLANE (the IPA trapezoid)
    y: height, 0 = close (top) ... 3 = open (bottom)
    x: backness.  The back edge is vertical at x = 2; the front edge slopes
       from x = 0 at close to x = 1 at open, so the open row is half the
       width of the close row, exactly as on the official chart.  Central
       and near-front/near-back positions are interpolated proportionally
       between the two edges *at each height*, so the central line slopes
       too.  Where the chart prints a pair of symbols beside a dot, the
       unrounded member sits left of the dot and the rounded one right.

CONSONANT PLANE (the pulmonic grid)
    x: place of articulation, 0 = bilabial ... 10 = glottal
    y: manner of articulation, 0 = plosive (top row) ... 7 = lateral
       approximant (bottom row)
    In each cell the voiceless member sits left and the voiced member
    right.  Voiced-only sonorants therefore sit on the right half, as on
    the chart.  Non-pulmonic consonants and the "other symbols" are given
    display positions outside / between the pulmonic cells; they are not
    part of the pulmonic chart.

The legacy dictionaries ``IPA_VOWELS`` and ``IPA_CONSONANTS`` keep their
original 6-tuple format ``(x, y, feature1, feature2, feature3, description)``.
"""

from typing import Dict, List, Optional, Tuple

# =============================================================================
# VOWEL GEOMETRY
# =============================================================================

VOWEL_HEIGHTS: List[str] = [
    'close', 'near-close', 'close-mid', 'mid', 'open-mid', 'near-open', 'open'
]
VOWEL_BACKNESSES: List[str] = ['front', 'near-front', 'central', 'near-back', 'back']

#: y coordinate of each height (rows are equidistant, as on the chart).
HEIGHT_Y: Dict[str, float] = {
    'close': 0.0, 'near-close': 0.5, 'close-mid': 1.0, 'mid': 1.5,
    'open-mid': 2.0, 'near-open': 2.5, 'open': 3.0,
}

#: Proportional position between the front edge (0) and the back edge (1).
BACKNESS_FRACTION: Dict[str, float] = {
    'front': 0.0, 'near-front': 0.25, 'central': 0.5, 'near-back': 0.75, 'back': 1.0,
}

VOWEL_MAX_Y = 3.0
VOWEL_BACK_X = 2.0
VOWEL_FRONT_OPEN_X = 1.0
#: Horizontal offset of the symbols of a rounding pair from their shared dot.
ROUNDING_OFFSET = 0.08


def vowel_front_edge(y: float) -> float:
    """x coordinate of the trapezoid's (sloping) front edge at height y."""
    return VOWEL_FRONT_OPEN_X * (y / VOWEL_MAX_Y)


def vowel_back_edge(y: float) -> float:
    """x coordinate of the trapezoid's (vertical) back edge at height y."""
    return VOWEL_BACK_X


def vowel_point(height: str, backness: str) -> Tuple[float, float]:
    """Articulatory point (the chart's 'dot') for a height/backness pair."""
    y = HEIGHT_Y[height]
    left, right = vowel_front_edge(y), vowel_back_edge(y)
    return (round(left + BACKNESS_FRACTION[backness] * (right - left), 4), y)


def vowel_central_x(y: float) -> float:
    """x coordinate of the central line at height y."""
    return (vowel_front_edge(y) + vowel_back_edge(y)) / 2


#: Corner points of the trapezoid outline (close-front, close-back,
#: open-back, open-front).
VOWEL_TRAPEZOID: List[Tuple[float, float]] = [
    (vowel_front_edge(0.0), 0.0), (vowel_back_edge(0.0), 0.0),
    (vowel_back_edge(VOWEL_MAX_Y), VOWEL_MAX_Y), (vowel_front_edge(VOWEL_MAX_Y), VOWEL_MAX_Y),
]

# =============================================================================
# VOWELS - official IPA chart (2020), all 28 symbols
# =============================================================================
# symbol: (height, backness, roundedness)
# 'unspecified' roundedness: the chart prints ə and ɐ alone, without a
# rounding value (their official names carry none).

VOWEL_SPECS: Dict[str, Tuple[str, str, str]] = {
    # Close
    'i': ('close', 'front', 'unrounded'),
    'y': ('close', 'front', 'rounded'),
    'ɨ': ('close', 'central', 'unrounded'),
    'ʉ': ('close', 'central', 'rounded'),
    'ɯ': ('close', 'back', 'unrounded'),
    'u': ('close', 'back', 'rounded'),
    # Near-close
    'ɪ': ('near-close', 'near-front', 'unrounded'),
    'ʏ': ('near-close', 'near-front', 'rounded'),
    'ʊ': ('near-close', 'near-back', 'rounded'),
    # Close-mid
    'e': ('close-mid', 'front', 'unrounded'),
    'ø': ('close-mid', 'front', 'rounded'),
    'ɘ': ('close-mid', 'central', 'unrounded'),
    'ɵ': ('close-mid', 'central', 'rounded'),
    'ɤ': ('close-mid', 'back', 'unrounded'),
    'o': ('close-mid', 'back', 'rounded'),
    # Mid
    'ə': ('mid', 'central', 'unspecified'),
    # Open-mid
    'ɛ': ('open-mid', 'front', 'unrounded'),
    'œ': ('open-mid', 'front', 'rounded'),
    'ɜ': ('open-mid', 'central', 'unrounded'),
    'ɞ': ('open-mid', 'central', 'rounded'),
    'ʌ': ('open-mid', 'back', 'unrounded'),
    'ɔ': ('open-mid', 'back', 'rounded'),
    # Near-open
    'æ': ('near-open', 'front', 'unrounded'),
    'ɐ': ('near-open', 'central', 'unspecified'),
    # Open
    'a': ('open', 'front', 'unrounded'),
    'ɶ': ('open', 'front', 'rounded'),
    'ɑ': ('open', 'back', 'unrounded'),
    'ɒ': ('open', 'back', 'rounded'),
}

# =============================================================================
# CONSONANT GEOMETRY
# =============================================================================

#: Columns of the pulmonic chart (x coordinate = index).
CONSONANT_PLACES: List[str] = [
    'bilabial', 'labiodental', 'dental', 'alveolar', 'postalveolar',
    'retroflex', 'palatal', 'velar', 'uvular', 'pharyngeal', 'glottal',
]
#: Rows of the pulmonic chart (y coordinate = index).
CONSONANT_MANNERS: List[str] = [
    'plosive', 'nasal', 'trill', 'tap', 'fricative', 'lateral-fricative',
    'approximant', 'lateral-approximant',
]

#: x coordinate of every place used anywhere in the inventory.  Places that
#: are not pulmonic-chart columns are interpolated between their neighbours.
PLACE_X: Dict[str, float] = {p: float(i) for i, p in enumerate(CONSONANT_PLACES)}
PLACE_X.update({
    'linguolabial': 1.5,
    'palatoalveolar': 4.0,      # click ǂ (IPA: "palatoalveolar")
    'alveolo-palatal': 5.5,     # ɕ ʑ: laminal post-alveolar with palatal raising
    'epiglottal': 9.5,          # ʜ ʢ ʡ: between pharyngeal and glottal
    'labial-velar': 7.0,        # doubly articulated; plotted at the dorsal column
    'labial-palatal': 6.0,
    'postalveolar-velar': 5.5,  # ɧ
})

#: y coordinate of every manner.  Non-pulmonic manners get rows of their own
#: below the pulmonic grid; ``lateral-tap`` shares the tap row.
MANNER_Y: Dict[str, float] = {m: float(i) for i, m in enumerate(CONSONANT_MANNERS)}
MANNER_Y.update({
    'lateral-tap': 3.0,
    'affricate': 0.5,           # between the plosive and nasal rows
    'implosive': 8.0,
    'click': 9.0,
    'lateral-click': 9.0,
})

#: Horizontal offset of the voiceless (-) / voiced (+) member within a cell.
VOICING_OFFSET = 0.2

#: Vertical offset that separates an "other symbol" from a pulmonic symbol
#: sharing its place and manner (w vs ɰ, ɥ vs j, ...).
OTHER_SYMBOL_OFFSET = 0.35


def consonant_point(manner: str, place: str) -> Tuple[float, float]:
    """Articulatory point of a consonant (cell centre, no voicing offset)."""
    return (PLACE_X[place], MANNER_Y[manner])


# =============================================================================
# CONSONANTS
# =============================================================================
# symbol: (manner, place, voicing)

#: Pulmonic consonants - the full 2020 chart (59 symbols).  The chart prints
#: t d n r ɾ ɬ ɮ ɹ l in a cell spanning dental/alveolar/postalveolar; they are
#: placed in the alveolar column.
PULMONIC_SPECS: Dict[str, Tuple[str, str, str]] = {
    # Plosive
    'p': ('plosive', 'bilabial', 'voiceless'),
    'b': ('plosive', 'bilabial', 'voiced'),
    't': ('plosive', 'alveolar', 'voiceless'),
    'd': ('plosive', 'alveolar', 'voiced'),
    'ʈ': ('plosive', 'retroflex', 'voiceless'),
    'ɖ': ('plosive', 'retroflex', 'voiced'),
    'c': ('plosive', 'palatal', 'voiceless'),
    'ɟ': ('plosive', 'palatal', 'voiced'),
    'k': ('plosive', 'velar', 'voiceless'),
    'ɡ': ('plosive', 'velar', 'voiced'),     # U+0261 LATIN SMALL LETTER SCRIPT G
    'q': ('plosive', 'uvular', 'voiceless'),
    'ɢ': ('plosive', 'uvular', 'voiced'),
    'ʔ': ('plosive', 'glottal', 'voiceless'),
    # Nasal
    'm': ('nasal', 'bilabial', 'voiced'),
    'ɱ': ('nasal', 'labiodental', 'voiced'),
    'n': ('nasal', 'alveolar', 'voiced'),
    'ɳ': ('nasal', 'retroflex', 'voiced'),
    'ɲ': ('nasal', 'palatal', 'voiced'),
    'ŋ': ('nasal', 'velar', 'voiced'),
    'ɴ': ('nasal', 'uvular', 'voiced'),
    # Trill
    'ʙ': ('trill', 'bilabial', 'voiced'),
    'r': ('trill', 'alveolar', 'voiced'),
    'ʀ': ('trill', 'uvular', 'voiced'),
    # Tap or flap
    'ⱱ': ('tap', 'labiodental', 'voiced'),
    'ɾ': ('tap', 'alveolar', 'voiced'),
    'ɽ': ('tap', 'retroflex', 'voiced'),
    # Fricative
    'ɸ': ('fricative', 'bilabial', 'voiceless'),
    'β': ('fricative', 'bilabial', 'voiced'),
    'f': ('fricative', 'labiodental', 'voiceless'),
    'v': ('fricative', 'labiodental', 'voiced'),
    'θ': ('fricative', 'dental', 'voiceless'),
    'ð': ('fricative', 'dental', 'voiced'),
    's': ('fricative', 'alveolar', 'voiceless'),
    'z': ('fricative', 'alveolar', 'voiced'),
    'ʃ': ('fricative', 'postalveolar', 'voiceless'),
    'ʒ': ('fricative', 'postalveolar', 'voiced'),
    'ʂ': ('fricative', 'retroflex', 'voiceless'),
    'ʐ': ('fricative', 'retroflex', 'voiced'),
    'ç': ('fricative', 'palatal', 'voiceless'),
    'ʝ': ('fricative', 'palatal', 'voiced'),
    'x': ('fricative', 'velar', 'voiceless'),
    'ɣ': ('fricative', 'velar', 'voiced'),
    'χ': ('fricative', 'uvular', 'voiceless'),
    'ʁ': ('fricative', 'uvular', 'voiced'),
    'ħ': ('fricative', 'pharyngeal', 'voiceless'),
    'ʕ': ('fricative', 'pharyngeal', 'voiced'),
    'h': ('fricative', 'glottal', 'voiceless'),
    'ɦ': ('fricative', 'glottal', 'voiced'),
    # Lateral fricative
    'ɬ': ('lateral-fricative', 'alveolar', 'voiceless'),
    'ɮ': ('lateral-fricative', 'alveolar', 'voiced'),
    # Approximant
    'ʋ': ('approximant', 'labiodental', 'voiced'),
    'ɹ': ('approximant', 'alveolar', 'voiced'),
    'ɻ': ('approximant', 'retroflex', 'voiced'),
    'j': ('approximant', 'palatal', 'voiced'),
    'ɰ': ('approximant', 'velar', 'voiced'),
    # Lateral approximant
    'l': ('lateral-approximant', 'alveolar', 'voiced'),
    'ɭ': ('lateral-approximant', 'retroflex', 'voiced'),
    'ʎ': ('lateral-approximant', 'palatal', 'voiced'),
    'ʟ': ('lateral-approximant', 'velar', 'voiced'),
}

#: "Other symbols" box of the 2020 chart.
OTHER_SPECS: Dict[str, Tuple[str, str, str]] = {
    'ʍ': ('fricative', 'labial-velar', 'voiceless'),
    'w': ('approximant', 'labial-velar', 'voiced'),
    'ɥ': ('approximant', 'labial-palatal', 'voiced'),
    'ʜ': ('fricative', 'epiglottal', 'voiceless'),
    'ʢ': ('fricative', 'epiglottal', 'voiced'),
    'ʡ': ('plosive', 'epiglottal', 'voiceless'),
    'ɕ': ('fricative', 'alveolo-palatal', 'voiceless'),
    'ʑ': ('fricative', 'alveolo-palatal', 'voiced'),
    'ɺ': ('lateral-tap', 'alveolar', 'voiced'),
    'ɧ': ('fricative', 'postalveolar-velar', 'voiceless'),
}

#: Non-pulmonic consonants box of the 2020 chart (clicks and voiced
#: implosives).  Ejectives are formed with the ʼ diacritic on any symbol.
#: A bare click symbol denotes the tenuis (voiceless) click.
NON_PULMONIC_SPECS: Dict[str, Tuple[str, str, str]] = {
    # Clicks
    'ʘ': ('click', 'bilabial', 'voiceless'),
    'ǀ': ('click', 'dental', 'voiceless'),
    'ǃ': ('click', 'alveolar', 'voiceless'),       # IPA: "(post)alveolar"
    'ǂ': ('click', 'palatoalveolar', 'voiceless'),
    'ǁ': ('lateral-click', 'alveolar', 'voiceless'),
    # Voiced implosives
    'ɓ': ('implosive', 'bilabial', 'voiced'),
    'ɗ': ('implosive', 'alveolar', 'voiced'),      # IPA: "dental/alveolar"
    'ʄ': ('implosive', 'palatal', 'voiced'),
    'ɠ': ('implosive', 'velar', 'voiced'),
    'ʛ': ('implosive', 'uvular', 'voiced'),
}

AIRSTREAM: Dict[str, str] = {
    'click': 'velaric ingressive',
    'lateral-click': 'velaric ingressive',
    'implosive': 'glottalic ingressive',
}

#: Official names that do not follow the "<voicing> <place> <manner>" pattern.
NAME_OVERRIDES: Dict[str, str] = {
    'ʔ': 'Glottal plosive (glottal stop)',
    'ʡ': 'Epiglottal plosive',
    'ⱱ': 'Voiced labiodental flap',
    'ɽ': 'Voiced retroflex flap',
    'ɺ': 'Voiced alveolar lateral flap',
    'ɧ': "Simultaneous ʃ and x (Swedish 'sj' sound)",
    'ə': 'Mid central vowel (schwa)',
    'ʘ': 'Bilabial click',
    'ǀ': 'Dental click',
    'ǃ': '(Post)alveolar click',
    'ǂ': 'Palatoalveolar click',
    'ǁ': 'Alveolar lateral click',
    'ɗ': 'Voiced dental/alveolar implosive',
}


def _vowel_name(height: str, backness: str, roundedness: str) -> str:
    parts = [height, backness] + ([] if roundedness == 'unspecified' else [roundedness])
    return (' '.join(parts) + ' vowel').capitalize()


def _consonant_name(manner: str, place: str, voicing: str) -> str:
    manner_name = manner.replace('-', ' ')
    return f"{voicing} {place} {manner_name}".capitalize()


def segment_name(symbol: str) -> str:
    """Official descriptive name of an inventory symbol."""
    if symbol in NAME_OVERRIDES:
        return NAME_OVERRIDES[symbol]
    if symbol in VOWEL_SPECS:
        return _vowel_name(*VOWEL_SPECS[symbol])
    return _consonant_name(*ALL_CONSONANT_SPECS[symbol])


ALL_CONSONANT_SPECS: Dict[str, Tuple[str, str, str]] = {
    **PULMONIC_SPECS, **OTHER_SPECS, **NON_PULMONIC_SPECS,
}


def consonant_category(symbol: str) -> str:
    """'pulmonic', 'other' or 'non-pulmonic'."""
    if symbol in PULMONIC_SPECS:
        return 'pulmonic'
    if symbol in OTHER_SPECS:
        return 'other'
    return 'non-pulmonic'


# =============================================================================
# DISPLAY COORDINATES
# =============================================================================

def _vowel_display_xy(symbol: str) -> Tuple[float, float]:
    height, backness, roundedness = VOWEL_SPECS[symbol]
    x, y = vowel_point(height, backness)
    has_partner = any(
        s != symbol and h == height and b == backness
        for s, (h, b, _) in VOWEL_SPECS.items()
    )
    if has_partner:
        x += -ROUNDING_OFFSET if roundedness == 'unrounded' else ROUNDING_OFFSET
    return (round(x, 4), y)


def _consonant_display_xy(symbol: str) -> Tuple[float, float]:
    manner, place, voicing = ALL_CONSONANT_SPECS[symbol]
    x, y = consonant_point(manner, place)
    x += -VOICING_OFFSET if voicing == 'voiceless' else VOICING_OFFSET
    if symbol in OTHER_SPECS:
        y += OTHER_SYMBOL_OFFSET
    return (round(x, 4), y)


# =============================================================================
# LEGACY TABLES: symbol -> (x, y, f1, f2, f3, description)
# =============================================================================

IPA_VOWELS: Dict[str, Tuple] = {
    s: (*_vowel_display_xy(s), *VOWEL_SPECS[s], segment_name(s)) for s in VOWEL_SPECS
}
#: Pulmonic consonant chart (what ``plot_consonant_chart`` draws).
IPA_CONSONANTS: Dict[str, Tuple] = {
    s: (*_consonant_display_xy(s), *PULMONIC_SPECS[s], segment_name(s)) for s in PULMONIC_SPECS
}
IPA_OTHER_CONSONANTS: Dict[str, Tuple] = {
    s: (*_consonant_display_xy(s), *OTHER_SPECS[s], segment_name(s)) for s in OTHER_SPECS
}
IPA_NON_PULMONIC: Dict[str, Tuple] = {
    s: (*_consonant_display_xy(s), *NON_PULMONIC_SPECS[s], segment_name(s))
    for s in NON_PULMONIC_SPECS
}
#: Every consonant symbol of the chart (pulmonic + other + non-pulmonic).
ALL_CONSONANTS: Dict[str, Tuple] = {**IPA_CONSONANTS, **IPA_OTHER_CONSONANTS, **IPA_NON_PULMONIC}

# =============================================================================
# DIACRITICS, SUPRASEGMENTALS, TONES (IPA 2020)
# =============================================================================
# Each diacritic: name, distinctive-feature changes, and optional special
# handling ('effect') applied in ``features.py``.  Feature values: +1 / -1 / 0.

DIACRITICS: Dict[str, Dict] = {
    # Phonation
    '̥': {'name': 'voiceless', 'features': {'voice': -1}},
    '̊': {'name': 'voiceless', 'features': {'voice': -1}},   # ring above (for descenders: ŋ̊)
    '̬': {'name': 'voiced', 'features': {'voice': +1}},
    'ʰ': {'name': 'aspirated', 'features': {'spread_glottis': +1}},
    'ʱ': {'name': 'breathy-voiced aspirated', 'features': {'spread_glottis': +1, 'voice': +1}},
    '̤': {'name': 'breathy voiced', 'features': {'voice': +1, 'spread_glottis': +1}},
    '̰': {'name': 'creaky voiced', 'features': {'voice': +1, 'constricted_glottis': +1}},
    'ʼ': {'name': 'ejective', 'features': {'constricted_glottis': +1, 'voice': -1},
          'effect': 'ejective'},
    # Rounding
    '̹': {'name': 'more rounded', 'features': {}},
    '̜': {'name': 'less rounded', 'features': {}},
    # Tongue position
    '̟': {'name': 'advanced', 'features': {}, 'shift': (-0.15, 0.0)},
    '̠': {'name': 'retracted', 'features': {}, 'shift': (0.15, 0.0)},
    '̈': {'name': 'centralized', 'features': {}, 'effect': 'centralize'},
    '̽': {'name': 'mid-centralized', 'features': {}, 'effect': 'mid-centralize'},
    '̝': {'name': 'raised', 'features': {}, 'shift': (0.0, -0.15), 'effect': 'raise'},
    '̞': {'name': 'lowered', 'features': {}, 'shift': (0.0, 0.15), 'effect': 'lower'},
    '̘': {'name': 'advanced tongue root', 'features': {'tense': +1}},
    '̙': {'name': 'retracted tongue root', 'features': {'tense': -1}},
    # Syllabicity
    '̩': {'name': 'syllabic', 'features': {'syllabic': +1}},
    '̍': {'name': 'syllabic', 'features': {'syllabic': +1}},  # above, for descenders
    '̯': {'name': 'non-syllabic', 'features': {'syllabic': -1}},
    '̑': {'name': 'non-syllabic', 'features': {'syllabic': -1}},
    # Secondary articulation
    'ʷ': {'name': 'labialized', 'features': {'labial': +1, 'round': +1}},
    'ʲ': {'name': 'palatalized', 'features': {'dorsal': +1, 'high': +1, 'low': -1,
                                               'front': +1, 'back': -1}},
    'ˠ': {'name': 'velarized', 'features': {'dorsal': +1, 'high': +1, 'low': -1,
                                             'front': -1, 'back': +1}},
    'ˤ': {'name': 'pharyngealized', 'features': {'dorsal': +1, 'high': -1, 'low': +1,
                                                  'front': -1, 'back': +1}},
    '̴': {'name': 'velarized or pharyngealized', 'features': {'dorsal': +1, 'front': -1,
                                                                    'back': +1}},
    '˞': {'name': 'rhotacized', 'features': {'coronal': +1, 'anterior': -1,
                                              'distributed': -1}},
    # Place refinements
    '̪': {'name': 'dental', 'features': {}, 'effect': 'dental'},
    '̺': {'name': 'apical', 'features': {'distributed': -1}},
    '̻': {'name': 'laminal', 'features': {'distributed': +1}},
    '̼': {'name': 'linguolabial', 'features': {'labial': +1, 'coronal': +1,
                                                     'anterior': +1}},
    # Nasality and release
    '̃': {'name': 'nasalized', 'features': {'nasal': +1}},
    'ⁿ': {'name': 'nasal release', 'features': {}},
    'ˡ': {'name': 'lateral release', 'features': {}},
    '̚': {'name': 'no audible release', 'features': {}},
    # Length (segmental, so attached to the segment)
    'ː': {'name': 'long', 'features': {'long': +1}},
    'ˑ': {'name': 'half-long', 'features': {'long': 0}},
    '̆': {'name': 'extra-short', 'features': {'long': -1}},
}

#: Tone diacritics: recorded on the segment, no segmental feature change.
TONE_DIACRITICS: Dict[str, str] = {
    '̋': 'extra high tone',
    '́': 'high tone',
    '̄': 'mid tone',
    '̀': 'low tone',
    '̏': 'extra low tone',
    '̌': 'rising tone',
    '̂': 'falling tone',
    '᷄': 'high rising tone',
    '᷅': 'low rising tone',
    '᷈': 'rising-falling tone',
}

#: Tone letters (Chao letters).  Consecutive letters form one contour token.
TONE_LETTERS: Dict[str, str] = {
    '˥': 'extra high', '˦': 'high', '˧': 'mid', '˨': 'low', '˩': 'extra low',
}

#: Free-standing prosodic symbols.
SUPRASEGMENTALS: Dict[str, str] = {
    'ˈ': 'primary stress',
    'ˌ': 'secondary stress',
    '|': 'minor (foot) group',
    '‖': 'major (intonation) group',
    '.': 'syllable break',
    '‿': 'linking (absence of a break)',
    'ꜜ': 'downstep',
    'ꜛ': 'upstep',
    '↗': 'global rise',
    '↘': 'global fall',
}

#: Ties: join two symbols into one segment (affricate, double articulation,
#: diphthong).
TIE_BARS = ('͡', '͜')

#: Transcription delimiters that carry no segmental content.
DELIMITERS = frozenset('/[]⟨⟩')

#: Diacritics written as spacing modifier letters (they follow the base).
SPACING_DIACRITICS = frozenset(c for c in DIACRITICS if len(c) == 1 and not
                               (0x0300 <= ord(c) <= 0x036F))

#: Common non-standard, obsolete or look-alike characters and their IPA
#: equivalents.  Applied before tokenizing.
SYMBOL_ALIASES: Dict[str, str] = {
    'g': 'ɡ',           # ASCII g -> IPA script g (U+0261)
    ':': 'ː',           # ASCII colon -> length mark
    'ɚ': 'ə˞',          # r-coloured schwa
    'ɝ': 'ɜ˞',          # r-coloured open-mid central vowel
    'ɫ': 'lˠ',          # velarized alveolar lateral ("dark l")
    'ʦ': 't͡s', 'ʣ': 'd͡z', 'ʧ': 't͡ʃ', 'ʤ': 'd͡ʒ', 'ʨ': 't͡ɕ', 'ʥ': 'd͡ʑ',  # withdrawn ligatures
    'ʇ': 'ǀ', 'ʗ': 'ǃ', 'ʖ': 'ǁ',   # withdrawn click letters
    'ɩ': 'ɪ', 'ɷ': 'ʊ',            # withdrawn vowel letters
    'ǝ': 'ə',           # U+01DD turned e -> schwa
    'ε': 'ɛ',           # Greek epsilon
    'α': 'ɑ',           # Greek alpha
    'ɼ': 'r̝',           # withdrawn: raised alveolar trill
    'ʿ': 'ʕ', 'ʾ': 'ʔ',  # Semitist half rings
    '’': 'ʼ',           # right single quotation mark used as ejective
    'ˁ': 'ˤ',      # modifier reversed glottal stop -> pharyngealized
}

# =============================================================================
# CATEGORICAL FEATURE SCALES (legacy, used by the chart-distance component)
# =============================================================================

ARTICULATORY_FEATURES = {
    'vowel_height': dict(HEIGHT_Y),
    'vowel_backness': {b: 2 * f for b, f in BACKNESS_FRACTION.items()},
    'vowel_roundedness': {'unrounded': 0, 'unspecified': 0.5, 'rounded': 1},
    'consonant_place': dict(PLACE_X),
    'consonant_manner': dict(MANNER_Y),
    'consonant_voicing': {'voiceless': 0, 'voiced': 1},
}

# =============================================================================
# COORDINATE SYSTEM METADATA
# =============================================================================

VOWEL_COORD_INFO = {
    'x_label': 'Backness',
    'y_label': 'Height',
    'x_range': (-0.2, 2.3),
    'y_range': (-0.3, 3.3),   # displayed inverted: close at the top
    'shape': 'trapezoid',
    'x_ticks': [(0, 'Front'), (1, 'Central'), (2, 'Back')],
    'y_ticks': [(0, 'Close'), (1, 'Close-mid'), (2, 'Open-mid'), (3, 'Open')],
}

CONSONANT_COORD_INFO = {
    'x_label': 'Place of Articulation',
    'y_label': 'Manner of Articulation',
    'x_range': (-0.5, 10.5),
    'y_range': (-0.5, 7.5),   # displayed inverted: plosive row at the top
    'shape': 'grid',
    'x_ticks': [(i, p.capitalize()) for i, p in enumerate(CONSONANT_PLACES)],
    'y_ticks': [
        (0, 'Plosive'), (1, 'Nasal'), (2, 'Trill'), (3, 'Tap or Flap'),
        (4, 'Fricative'), (5, 'Lateral fricative'), (6, 'Approximant'),
        (7, 'Lateral approximant'),
    ],
}


def symbol_kind(symbol: str) -> Optional[str]:
    """'vowel', 'consonant' or None for a bare inventory symbol."""
    if symbol in VOWEL_SPECS:
        return 'vowel'
    if symbol in ALL_CONSONANT_SPECS:
        return 'consonant'
    return None
