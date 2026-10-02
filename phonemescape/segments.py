"""
IPA tokenizer and segment resolver.

``tokenize`` splits an IPA transcription into tokens: segments (a base
symbol plus its diacritics, tones and any tie-barred partners),
suprasegmentals (stress, length-independent prosodic marks, breaks), tone
letters, word boundaries and unknown characters.

``get_segment`` resolves one transcribed segment - e.g. ``'tʰ'``, ``'ã'``,
``'t͡ʃ'``, ``'n̩'``, ``'kʷʼ'`` - to a :class:`Segment` carrying its chart
attributes, distinctive features, chart position and an IPA-style
description.

Unicode handling: input is normalised (NFC), common look-alike and
withdrawn symbols are mapped to their IPA equivalents (``SYMBOL_ALIASES``,
e.g. ASCII ``g`` -> ``ɡ``, ``ʧ`` -> ``t͡ʃ``, ``:`` -> ``ː``), and the result is
decomposed (NFD) so that precomposed letters such as ``ã`` or ``é`` are read
as a base symbol plus a diacritic or tone mark.
"""

import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np

from .data import (
    AIRSTREAM, ALL_CONSONANT_SPECS, DELIMITERS, DIACRITICS, MANNER_Y, OTHER_SPECS,
    OTHER_SYMBOL_OFFSET, PLACE_X, ROUNDING_OFFSET, SPACING_DIACRITICS,
    SUPRASEGMENTALS, SYMBOL_ALIASES, TIE_BARS, TONE_DIACRITICS, TONE_LETTERS,
    VOICING_OFFSET, VOWEL_SPECS, IPA_VOWELS, ALL_CONSONANTS, consonant_category,
    consonant_point, segment_name, vowel_central_x, vowel_point, HEIGHT_Y,
)
from .features import (
    FEATURE_NAMES, FeatureBundle, affricate_features, consonant_features,
    merge_articulators, normalize, vowel_features,
)

#: Spacing letters that, before a consonant, mark prenasalization (ⁿd, ᵐb, ᵑɡ).
PRENASAL_MARKS = frozenset('ⁿᵐᵑᶬ')
#: Spacing letters that, before a consonant, mark pre-aspiration (ʰt).
PREASPIRATION_MARKS = frozenset('ʰ')


@dataclass(frozen=True)
class Segment:
    """One IPA segment, possibly modified by diacritics or tied to another."""

    symbol: str
    kind: str                                  # 'vowel' or 'consonant'
    base: str                                  # first base symbol
    parts: Tuple[str, ...]                     # base symbols of tied components
    modifiers: Tuple[str, ...]                 # names of applied diacritics
    tones: Tuple[str, ...]
    features: Tuple[int, ...]                  # values in FEATURE_NAMES order
    position: Tuple[float, float]              # articulatory point on its plane
    coordinates: Tuple[float, float]           # display point on its plane
    attributes: Tuple[Tuple[str, str], ...]
    description: str

    @property
    def feature_dict(self) -> Dict[str, int]:
        return dict(zip(FEATURE_NAMES, self.features))

    @property
    def feature_vector(self) -> np.ndarray:
        return np.array(self.features, dtype=float)

    @property
    def attribute_dict(self) -> Dict[str, str]:
        return dict(self.attributes)

    def __getitem__(self, name: str) -> int:
        return self.feature_dict[name]


@dataclass(frozen=True)
class Token:
    """A unit of an IPA transcription."""

    text: str
    kind: str          # 'segment', 'suprasegmental', 'tone', 'boundary', 'unknown'
    description: str
    segment: Optional[Segment] = field(default=None, compare=False)


# =============================================================================
# Normalisation and base-symbol lookup
# =============================================================================

def normalize_ipa(text: str) -> str:
    """NFC-normalise, map aliases, then decompose (NFD)."""
    text = unicodedata.normalize('NFC', text)
    text = ''.join(SYMBOL_ALIASES.get(ch, ch) for ch in text)
    return unicodedata.normalize('NFD', text)


_BASES: Dict[str, str] = {
    unicodedata.normalize('NFD', s): s for s in list(VOWEL_SPECS) + list(ALL_CONSONANT_SPECS)
}
_MAX_BASE_LEN = max(len(k) for k in _BASES)


def _match_base(text: str, i: int) -> Optional[Tuple[str, int]]:
    """Longest inventory symbol starting at position i -> (symbol, length)."""
    for length in range(_MAX_BASE_LEN, 0, -1):
        chunk = text[i:i + length]
        if chunk in _BASES:
            return _BASES[chunk], length
    return None


def _is_diacritic(ch: str) -> bool:
    return ch in DIACRITICS or ch in TONE_DIACRITICS


# =============================================================================
# Units: base symbol + its own marks
# =============================================================================

@dataclass
class _Unit:
    base: str
    marks: List[str] = field(default_factory=list)
    tones: List[str] = field(default_factory=list)
    prefixes: List[str] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return 'vowel' if self.base in VOWEL_SPECS else 'consonant'

    @property
    def manner(self) -> Optional[str]:
        return ALL_CONSONANT_SPECS[self.base][0] if self.kind == 'consonant' else None


def _read_unit(text: str, i: int, prefixes: List[str]) -> Tuple[_Unit, int]:
    base, length = _match_base(text, i)  # type: ignore[misc]
    unit = _Unit(base, prefixes=list(prefixes))
    i += length
    while i < len(text) and _is_diacritic(text[i]):
        ch = text[i]
        if ch in SPACING_DIACRITICS and _starts_prefix(unit, text, i):
            break
        if ch in TONE_DIACRITICS:
            unit.tones.append(ch)
        else:
            unit.marks.append(ch)
        i += 1
    return unit, i


def _starts_prefix(unit: _Unit, text: str, i: int) -> bool:
    """
    Decide whether a spacing mark after ``unit`` belongs to the NEXT
    consonant instead: ⁿ/ᵐ/ᵑ after a non-stop and before a consonant is
    prenasalization, ʰ after a vowel and before a consonant is
    pre-aspiration.  Otherwise it modifies ``unit`` (nasal release,
    aspiration).
    """
    ch = text[i]
    nxt = _match_base(text, i + 1)
    if nxt is None or nxt[0] not in ALL_CONSONANT_SPECS:
        return False
    if ch in PRENASAL_MARKS:
        return unit.manner not in ('plosive', 'implosive')
    if ch in PREASPIRATION_MARKS:
        return unit.kind == 'vowel'
    return False


# =============================================================================
# Feature and position computation
# =============================================================================

def _base_features(symbol: str) -> FeatureBundle:
    if symbol in VOWEL_SPECS:
        return vowel_features(*VOWEL_SPECS[symbol])
    return consonant_features(*ALL_CONSONANT_SPECS[symbol])


def _base_position(symbol: str) -> Tuple[float, float]:
    if symbol in VOWEL_SPECS:
        height, backness, _ = VOWEL_SPECS[symbol]
        return vowel_point(height, backness)
    manner, place, _ = ALL_CONSONANT_SPECS[symbol]
    return consonant_point(manner, place)


def _apply_marks(unit: _Unit) -> Tuple[FeatureBundle, Tuple[float, float], List[str], Dict[str, str]]:
    """Apply a unit's prefixes and diacritics.  Returns features, position,
    modifier names and attribute overrides."""
    feats = _base_features(unit.base)
    x, y = _base_position(unit.base)
    names: List[str] = []
    attrs: Dict[str, str] = {}

    for p in unit.prefixes:
        if p in PRENASAL_MARKS:
            names.append('prenasalized')
        elif p in PREASPIRATION_MARKS:
            names.append('pre-aspirated')
            feats['spread_glottis'] = 1

    for mark in unit.marks:
        spec = DIACRITICS[mark]
        had_labial, had_coronal = feats['labial'] == 1, feats['coronal'] == 1
        feats.update(spec['features'])
        if feats['labial'] == 1 and not had_labial and feats['labiodental'] == 0:
            feats['labiodental'] = -1
        if feats['coronal'] == 1 and not had_coronal and feats['distributed'] == 0:
            feats['distributed'] = -1
        dx, dy = spec.get('shift', (0.0, 0.0))
        x, y = x + dx, y + dy
        effect = spec.get('effect')
        if effect == 'ejective':
            attrs['airstream'] = 'glottalic egressive'
            attrs['category'] = 'non-pulmonic'
        elif effect == 'centralize' and unit.kind == 'vowel':
            x += 0.5 * (vowel_central_x(y) - x)
        elif effect == 'mid-centralize' and unit.kind == 'vowel':
            cy = HEIGHT_Y['mid']
            x, y = x + 0.5 * (vowel_central_x(cy) - x), y + 0.5 * (cy - y)
        elif effect == 'raise' and unit.kind == 'consonant':
            # Raised approximant = fricative (ɹ̝, ɾ̝)
            if feats['approximant'] == 1 and feats['syllabic'] != 1:
                feats.update(sonorant=-1, approximant=-1, consonantal=1, tap=-1, trill=-1)
        elif effect == 'lower' and unit.kind == 'consonant':
            # Lowered fricative = approximant (β̞, ð̞, ɣ̞)
            if feats['continuant'] == 1 and feats['sonorant'] == -1:
                feats.update(sonorant=1, approximant=1)
                if feats['coronal'] != 1:
                    feats['consonantal'] = -1
                feats['strident'] = 0
        elif effect == 'dental':
            if feats['coronal'] == 1:
                feats.update(anterior=1, distributed=1)
            elif feats['labial'] == 1:
                feats['labiodental'] = 1          # p̪ b̪ = labiodental stops
        if spec['name'] not in names:
            names.append(spec['name'])

    feats = normalize(feats)
    if unit.kind == 'consonant':
        attrs['voicing'] = 'voiced' if feats['voice'] == 1 else 'voiceless'
    return feats, (round(x, 4), round(y, 4)), names, attrs


def _display_point(kind: str, base: str, position: Tuple[float, float],
                   voice: int) -> Tuple[float, float]:
    x, y = position
    if kind == 'vowel':
        bx, by = _base_position(base)
        dx = IPA_VOWELS[base][0] - bx
        return (round(x + dx, 4), y)
    x += VOICING_OFFSET if voice == 1 else -VOICING_OFFSET
    if base in OTHER_SPECS:
        y += OTHER_SYMBOL_OFFSET
    return (round(x, 4), round(y, 4))


def _base_attributes(symbol: str) -> Dict[str, str]:
    if symbol in VOWEL_SPECS:
        height, backness, roundedness = VOWEL_SPECS[symbol]
        return {'height': height, 'backness': backness, 'roundedness': roundedness}
    manner, place, voicing = ALL_CONSONANT_SPECS[symbol]
    return {'manner': manner, 'place': place, 'voicing': voicing,
            'airstream': AIRSTREAM.get(manner, 'pulmonic'),
            'category': consonant_category(symbol)}


def _combined_place(p1: str, p2: str) -> str:
    a, b = sorted((p1, p2), key=lambda p: PLACE_X[p])
    a = 'labial' if a == 'bilabial' else a
    return f"{a}-{b}"


def _build_segment(units: List[_Unit], symbol: str) -> Segment:
    processed = [_apply_marks(u) for u in units]
    first = units[0]
    feats, position, modifiers, overrides = processed[0]
    attrs = _base_attributes(first.base)
    attrs.update(overrides)
    name = segment_name(first.base)
    kind = first.kind

    for unit, (f2, pos2, mods2, ov2) in zip(units[1:], processed[1:]):
        a2 = _base_attributes(unit.base)
        a2.update(ov2)
        modifiers += [m for m in mods2 if m not in modifiers]
        m1, m2 = attrs.get('manner', ''), a2.get('manner', '')
        if kind == 'consonant' and unit.kind == 'consonant':
            if m1 in ('plosive',) and m2 in ('fricative', 'lateral-fricative'):
                feats = affricate_features(feats, f2)
                lateral = m2.startswith('lateral')
                attrs.update(manner='lateral-affricate' if lateral else 'affricate',
                             place=a2['place'])
                strid = 'sibilant ' if feats['strident'] == 1 else ''
                lat = 'lateral ' if lateral else ''
                voicing = 'voiced' if feats['voice'] == 1 else 'voiceless'
                name = f"{voicing} {a2['place']} {strid}{lat}affricate".capitalize()
                position = (pos2[0], MANNER_Y['affricate'])
            else:
                feats = merge_articulators(feats, f2)
                place = _combined_place(attrs['place'], a2['place'])
                voicing = 'voiced' if feats['voice'] == 1 else 'voiceless'
                if m1 == m2:
                    attrs['place'] = place
                    name = f"{voicing} {place} {m1.replace('-', ' ')}".capitalize()
                else:
                    name = f"{name} with {segment_name(unit.base).lower()}"
                if pos2[0] > position[0]:
                    position = (pos2[0], position[1])
            attrs['voicing'] = 'voiced' if feats['voice'] == 1 else 'voiceless'
        elif kind == 'vowel' and unit.kind == 'vowel':
            attrs['diphthong'] = f"{first.base}→{unit.base}"
            name = (f"Diphthong from {segment_name(first.base).lower()} "
                    f"to {segment_name(unit.base).lower()}")
        else:
            name = f"{name} tied to {segment_name(unit.base).lower()}"

    # A voicing diacritic that flips the base's voicing is folded into the
    # name (n̥ -> "Voiceless alveolar nasal") rather than listed after it.
    if kind == 'consonant':
        final = 'Voiced' if feats['voice'] == 1 else 'Voiceless'
        for old in ('Voiceless', 'Voiced'):
            if name.startswith(old + ' ') and old != final:
                name = final + name[len(old):]
                modifiers = [m for m in modifiers if m not in ('voiced', 'voiceless')]
                break

    tones = tuple(TONE_DIACRITICS[t] for u in units for t in u.tones)
    description = name
    if modifiers:
        description += ', ' + ', '.join(modifiers)
    if tones:
        description += ' (' + ', '.join(tones) + ')'

    display = _display_point(kind, first.base, position, feats['voice'])
    return Segment(
        symbol=unicodedata.normalize('NFC', symbol),
        kind=kind,
        base=first.base,
        parts=tuple(u.base for u in units),
        modifiers=tuple(modifiers),
        tones=tones,
        features=tuple(feats[k] for k in FEATURE_NAMES),
        position=position,
        coordinates=display,
        attributes=tuple(attrs.items()),
        description=description,
    )


# =============================================================================
# Public API
# =============================================================================

def tokenize(text: str) -> List[Token]:
    """Split an IPA transcription into tokens."""
    s = normalize_ipa(text)
    tokens: List[Token] = []
    i = 0
    pending_prefixes: List[str] = []
    while i < len(s):
        ch = s[i]
        if ch in DELIMITERS:
            i += 1
            continue
        if ch.isspace():
            j = i
            while j < len(s) and s[j].isspace():
                j += 1
            if tokens and tokens[-1].kind != 'boundary':
                tokens.append(Token(' ', 'boundary', 'word boundary'))
            i = j
            continue
        if ch in SUPRASEGMENTALS:
            tokens.append(Token(ch, 'suprasegmental', SUPRASEGMENTALS[ch]))
            i += 1
            continue
        if ch in TONE_LETTERS:
            j = i
            while j < len(s) and s[j] in TONE_LETTERS:
                j += 1
            run = s[i:j]
            levels = ' '.join(TONE_LETTERS[c] for c in run)
            label = 'level tone' if len(set(run)) == 1 else 'contour tone'
            tokens.append(Token(run, 'tone', f"{label}: {levels}"))
            i = j
            continue
        if _match_base(s, i) is not None:
            start = i
            units: List[_Unit] = []
            unit, i = _read_unit(s, i, pending_prefixes)
            pending_prefixes = []
            units.append(unit)
            while (i + 1 < len(s) and s[i] in TIE_BARS
                   and _match_base(s, i + 1) is not None):
                unit, i = _read_unit(s, i + 1, [])
                units.append(unit)
            raw = ''.join(units[0].prefixes) + s[start:i] if units[0].prefixes else s[start:i]
            seg = _build_segment(units, raw)
            tokens.append(Token(seg.symbol, 'segment', seg.description, seg))
            continue
        if (ch in PRENASAL_MARKS or ch in PREASPIRATION_MARKS) and \
                _match_base(s, i + 1) is not None:
            pending_prefixes.append(ch)
            i += 1
            continue
        name = unicodedata.name(ch, 'UNKNOWN CHARACTER')
        tokens.append(Token(unicodedata.normalize('NFC', ch), 'unknown', name.lower()))
        i += 1
    if tokens and tokens[-1].kind == 'boundary':
        tokens.pop()
    return tokens


def segments(text: str) -> List[Segment]:
    """The segments of a transcription, ignoring prosodic tokens."""
    return [t.segment for t in tokenize(text) if t.segment is not None]


@lru_cache(maxsize=4096)
def get_segment(symbol: str) -> Segment:
    """Resolve a single transcribed segment; raise ValueError otherwise."""
    tokens = tokenize(symbol)
    segs = [t for t in tokens if t.kind == 'segment']
    others = [t for t in tokens if t.kind != 'segment']
    if len(segs) != 1 or others:
        raise ValueError(f"'{symbol}' is not a single IPA segment")
    return segs[0].segment  # type: ignore[return-value]


def is_segment(symbol: str) -> bool:
    try:
        get_segment(symbol)
        return True
    except ValueError:
        return False


def inventory() -> Dict[str, Segment]:
    """Every base symbol of the chart, resolved."""
    return {s: get_segment(s) for s in list(IPA_VOWELS) + list(ALL_CONSONANTS)}
