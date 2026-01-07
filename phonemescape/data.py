"""
IPA phoneme data with coordinates for visualization and similarity analysis.
Coordinates are based on official IPA chart (2020 revision).

VOWEL COORDINATE SYSTEM (Trapezoid):
- X-axis: Backness (0=Front, 1=Central, 2=Back) - note trapezoid shape
- Y-axis: Height (0=Close, 1=Close-mid, 2=Open-mid, 3=Open)
- The trapezoid narrows toward the top (close vowels)

CONSONANT COORDINATE SYSTEM (Grid):
- X-axis: Place of articulation (0-10)
- Y-axis: Manner of articulation (0-7)

These are SEPARATE coordinate planes - vowels and consonants should
NEVER be compared directly on the same plane.
"""

# =============================================================================
# VOWEL DATA - Based on official IPA vowel trapezoid (2020)
# =============================================================================
# Format: symbol -> (x, y, height, backness, roundedness, description)
# 
# Trapezoid coordinates (matching the visual chart):
#   - X: 0.0 = Front, 1.0 = Central, 2.0 = Back
#   - Y: 0.0 = Close (top), 1.0 = Close-mid, 2.0 = Open-mid, 3.0 = Open (bottom)
#   - Trapezoid effect: Front vowels shift right as height decreases
#
# Pairs: unrounded • rounded (left • right in each position)

IPA_VOWELS = {
    # Close (Y=0) - Top row of trapezoid
    'i': (0.0, 0.0, 'close', 'front', 'unrounded', 'Close front unrounded vowel'),
    'y': (0.1, 0.0, 'close', 'front', 'rounded', 'Close front rounded vowel'),
    'ɨ': (1.0, 0.0, 'close', 'central', 'unrounded', 'Close central unrounded vowel'),
    'ʉ': (1.1, 0.0, 'close', 'central', 'rounded', 'Close central rounded vowel'),
    'ɯ': (2.0, 0.0, 'close', 'back', 'unrounded', 'Close back unrounded vowel'),
    'u': (2.1, 0.0, 'close', 'back', 'rounded', 'Close back rounded vowel'),
    
    # Near-close (Y=0.5) - Between Close and Close-mid
    'ɪ': (0.3, 0.5, 'near-close', 'near-front', 'unrounded', 'Near-close near-front unrounded vowel'),
    'ʏ': (0.4, 0.5, 'near-close', 'near-front', 'rounded', 'Near-close near-front rounded vowel'),
    'ʊ': (1.8, 0.5, 'near-close', 'near-back', 'rounded', 'Near-close near-back rounded vowel'),
    
    # Close-mid (Y=1)
    'e': (0.2, 1.0, 'close-mid', 'front', 'unrounded', 'Close-mid front unrounded vowel'),
    'ø': (0.3, 1.0, 'close-mid', 'front', 'rounded', 'Close-mid front rounded vowel'),
    'ɘ': (1.0, 1.0, 'close-mid', 'central', 'unrounded', 'Close-mid central unrounded vowel'),
    'ɵ': (1.1, 1.0, 'close-mid', 'central', 'rounded', 'Close-mid central rounded vowel'),
    'ɤ': (2.0, 1.0, 'close-mid', 'back', 'unrounded', 'Close-mid back unrounded vowel'),
    'o': (2.1, 1.0, 'close-mid', 'back', 'rounded', 'Close-mid back rounded vowel'),
    
    # Mid (Y=1.5) - Schwa position
    'ə': (1.0, 1.5, 'mid', 'central', 'unrounded', 'Mid central vowel (schwa)'),
    
    # Open-mid (Y=2)
    'ɛ': (0.4, 2.0, 'open-mid', 'front', 'unrounded', 'Open-mid front unrounded vowel'),
    'œ': (0.5, 2.0, 'open-mid', 'front', 'rounded', 'Open-mid front rounded vowel'),
    'ɜ': (1.0, 2.0, 'open-mid', 'central', 'unrounded', 'Open-mid central unrounded vowel'),
    'ɞ': (1.1, 2.0, 'open-mid', 'central', 'rounded', 'Open-mid central rounded vowel'),
    'ʌ': (1.8, 2.0, 'open-mid', 'back', 'unrounded', 'Open-mid back unrounded vowel'),
    'ɔ': (2.1, 2.0, 'open-mid', 'back', 'rounded', 'Open-mid back rounded vowel'),
    
    # Near-open (Y=2.5)
    'æ': (0.5, 2.5, 'near-open', 'front', 'unrounded', 'Near-open front unrounded vowel'),
    'ɐ': (1.2, 2.5, 'near-open', 'central', 'unrounded', 'Near-open central vowel'),
    
    # Open (Y=3) - Bottom row of trapezoid
    'a': (0.6, 3.0, 'open', 'front', 'unrounded', 'Open front unrounded vowel'),
    'ɶ': (0.7, 3.0, 'open', 'front', 'rounded', 'Open front rounded vowel'),
    'ɑ': (2.0, 3.0, 'open', 'back', 'unrounded', 'Open back unrounded vowel'),
    'ɒ': (2.1, 3.0, 'open', 'back', 'rounded', 'Open back rounded vowel'),
}

# =============================================================================
# CONSONANT DATA - Based on official IPA pulmonic consonant chart (2020)
# =============================================================================
# Format: symbol -> (x, y, manner, place, voicing, description)
#
# Grid coordinates (matching the visual chart):
#   X-axis (Place of articulation):
#     0 = Bilabial
#     1 = Labiodental  
#     2 = Dental
#     3 = Alveolar
#     4 = Postalveolar
#     5 = Retroflex
#     6 = Palatal
#     7 = Velar
#     8 = Uvular
#     9 = Pharyngeal
#     10 = Glottal
#
#   Y-axis (Manner of articulation):
#     0 = Plosive
#     1 = Nasal
#     2 = Trill
#     3 = Tap or Flap
#     4 = Fricative
#     5 = Lateral fricative
#     6 = Approximant
#     7 = Lateral approximant
#
# Voicing: In each cell, voiceless is left, voiced is right
# Shaded cells = articulation judged impossible

IPA_CONSONANTS = {
    # ===================
    # PLOSIVES (Y=0)
    # ===================
    'p': (0, 0, 'plosive', 'bilabial', 'voiceless', 'Voiceless bilabial plosive'),
    'b': (0.1, 0, 'plosive', 'bilabial', 'voiced', 'Voiced bilabial plosive'),
    't': (3, 0, 'plosive', 'alveolar', 'voiceless', 'Voiceless alveolar plosive'),
    'd': (3.1, 0, 'plosive', 'alveolar', 'voiced', 'Voiced alveolar plosive'),
    'ʈ': (5, 0, 'plosive', 'retroflex', 'voiceless', 'Voiceless retroflex plosive'),
    'ɖ': (5.1, 0, 'plosive', 'retroflex', 'voiced', 'Voiced retroflex plosive'),
    'c': (6, 0, 'plosive', 'palatal', 'voiceless', 'Voiceless palatal plosive'),
    'ɟ': (6.1, 0, 'plosive', 'palatal', 'voiced', 'Voiced palatal plosive'),
    'k': (7, 0, 'plosive', 'velar', 'voiceless', 'Voiceless velar plosive'),
    'g': (7.1, 0, 'plosive', 'velar', 'voiced', 'Voiced velar plosive'),
    'q': (8, 0, 'plosive', 'uvular', 'voiceless', 'Voiceless uvular plosive'),
    'ɢ': (8.1, 0, 'plosive', 'uvular', 'voiced', 'Voiced uvular plosive'),
    'ʔ': (10, 0, 'plosive', 'glottal', 'voiceless', 'Glottal stop'),
    
    # ===================
    # NASALS (Y=1)
    # ===================
    'm': (0, 1, 'nasal', 'bilabial', 'voiced', 'Voiced bilabial nasal'),
    'ɱ': (1, 1, 'nasal', 'labiodental', 'voiced', 'Voiced labiodental nasal'),
    'n': (3, 1, 'nasal', 'alveolar', 'voiced', 'Voiced alveolar nasal'),
    'ɳ': (5, 1, 'nasal', 'retroflex', 'voiced', 'Voiced retroflex nasal'),
    'ɲ': (6, 1, 'nasal', 'palatal', 'voiced', 'Voiced palatal nasal'),
    'ŋ': (7, 1, 'nasal', 'velar', 'voiced', 'Voiced velar nasal'),
    'ɴ': (8, 1, 'nasal', 'uvular', 'voiced', 'Voiced uvular nasal'),
    
    # ===================
    # TRILLS (Y=2)
    # ===================
    'ʙ': (0, 2, 'trill', 'bilabial', 'voiced', 'Voiced bilabial trill'),
    'r': (3, 2, 'trill', 'alveolar', 'voiced', 'Voiced alveolar trill'),
    'ʀ': (8, 2, 'trill', 'uvular', 'voiced', 'Voiced uvular trill'),
    
    # ===================
    # TAPS/FLAPS (Y=3)
    # ===================
    'ⱱ': (1, 3, 'tap', 'labiodental', 'voiced', 'Voiced labiodental flap'),
    'ɾ': (3, 3, 'tap', 'alveolar', 'voiced', 'Voiced alveolar tap'),
    'ɽ': (5, 3, 'tap', 'retroflex', 'voiced', 'Voiced retroflex flap'),
    
    # ===================
    # FRICATIVES (Y=4)
    # ===================
    'ɸ': (0, 4, 'fricative', 'bilabial', 'voiceless', 'Voiceless bilabial fricative'),
    'β': (0.1, 4, 'fricative', 'bilabial', 'voiced', 'Voiced bilabial fricative'),
    'f': (1, 4, 'fricative', 'labiodental', 'voiceless', 'Voiceless labiodental fricative'),
    'v': (1.1, 4, 'fricative', 'labiodental', 'voiced', 'Voiced labiodental fricative'),
    'θ': (2, 4, 'fricative', 'dental', 'voiceless', 'Voiceless dental fricative'),
    'ð': (2.1, 4, 'fricative', 'dental', 'voiced', 'Voiced dental fricative'),
    's': (3, 4, 'fricative', 'alveolar', 'voiceless', 'Voiceless alveolar fricative'),
    'z': (3.1, 4, 'fricative', 'alveolar', 'voiced', 'Voiced alveolar fricative'),
    'ʃ': (4, 4, 'fricative', 'postalveolar', 'voiceless', 'Voiceless postalveolar fricative'),
    'ʒ': (4.1, 4, 'fricative', 'postalveolar', 'voiced', 'Voiced postalveolar fricative'),
    'ʂ': (5, 4, 'fricative', 'retroflex', 'voiceless', 'Voiceless retroflex fricative'),
    'ʐ': (5.1, 4, 'fricative', 'retroflex', 'voiced', 'Voiced retroflex fricative'),
    'ç': (6, 4, 'fricative', 'palatal', 'voiceless', 'Voiceless palatal fricative'),
    'ʝ': (6.1, 4, 'fricative', 'palatal', 'voiced', 'Voiced palatal fricative'),
    'x': (7, 4, 'fricative', 'velar', 'voiceless', 'Voiceless velar fricative'),
    'ɣ': (7.1, 4, 'fricative', 'velar', 'voiced', 'Voiced velar fricative'),
    'χ': (8, 4, 'fricative', 'uvular', 'voiceless', 'Voiceless uvular fricative'),
    'ʁ': (8.1, 4, 'fricative', 'uvular', 'voiced', 'Voiced uvular fricative'),
    'ħ': (9, 4, 'fricative', 'pharyngeal', 'voiceless', 'Voiceless pharyngeal fricative'),
    'ʕ': (9.1, 4, 'fricative', 'pharyngeal', 'voiced', 'Voiced pharyngeal fricative'),
    'h': (10, 4, 'fricative', 'glottal', 'voiceless', 'Voiceless glottal fricative'),
    'ɦ': (10.1, 4, 'fricative', 'glottal', 'voiced', 'Voiced glottal fricative'),
    
    # ===================
    # LATERAL FRICATIVES (Y=5)
    # ===================
    'ɬ': (3, 5, 'lateral-fricative', 'alveolar', 'voiceless', 'Voiceless alveolar lateral fricative'),
    'ɮ': (3.1, 5, 'lateral-fricative', 'alveolar', 'voiced', 'Voiced alveolar lateral fricative'),
    
    # ===================
    # APPROXIMANTS (Y=6)
    # ===================
    'ʋ': (1, 6, 'approximant', 'labiodental', 'voiced', 'Voiced labiodental approximant'),
    'ɹ': (3, 6, 'approximant', 'alveolar', 'voiced', 'Voiced alveolar approximant'),
    'ɻ': (5, 6, 'approximant', 'retroflex', 'voiced', 'Voiced retroflex approximant'),
    'j': (6, 6, 'approximant', 'palatal', 'voiced', 'Voiced palatal approximant'),
    'ɰ': (7, 6, 'approximant', 'velar', 'voiced', 'Voiced velar approximant'),
    
    # ===================
    # LATERAL APPROXIMANTS (Y=7)
    # ===================
    'l': (3, 7, 'lateral-approximant', 'alveolar', 'voiced', 'Voiced alveolar lateral approximant'),
    'ɭ': (5, 7, 'lateral-approximant', 'retroflex', 'voiced', 'Voiced retroflex lateral approximant'),
    'ʎ': (6, 7, 'lateral-approximant', 'palatal', 'voiced', 'Voiced palatal lateral approximant'),
    'ʟ': (7, 7, 'lateral-approximant', 'velar', 'voiced', 'Voiced velar lateral approximant'),
}

# =============================================================================
# ARTICULATORY FEATURE MAPPINGS
# =============================================================================
# These map categorical features to numerical values for similarity calculations
# IMPORTANT: Vowels and consonants use SEPARATE coordinate systems

ARTICULATORY_FEATURES = {
    # Vowel features (trapezoid coordinate system)
    'vowel_height': {
        'close': 0.0,
        'near-close': 0.5,
        'close-mid': 1.0,
        'mid': 1.5,
        'open-mid': 2.0,
        'near-open': 2.5,
        'open': 3.0
    },
    'vowel_backness': {
        'front': 0.0,
        'near-front': 0.3,
        'central': 1.0,
        'near-back': 1.7,
        'back': 2.0
    },
    'vowel_roundedness': {
        'unrounded': 0,
        'rounded': 1
    },
    
    # Consonant features (grid coordinate system)
    'consonant_place': {
        'bilabial': 0,
        'labiodental': 1,
        'dental': 2,
        'alveolar': 3,
        'postalveolar': 4,
        'retroflex': 5,
        'palatal': 6,
        'velar': 7,
        'uvular': 8,
        'pharyngeal': 9,
        'glottal': 10
    },
    'consonant_manner': {
        'plosive': 0,
        'nasal': 1,
        'trill': 2,
        'tap': 3,
        'fricative': 4,
        'lateral-fricative': 5,
        'approximant': 6,
        'lateral-approximant': 7
    },
    'consonant_voicing': {
        'voiceless': 0,
        'voiced': 1
    }
}

# =============================================================================
# COORDINATE SYSTEM METADATA
# =============================================================================
# Information about the coordinate systems for proper scaling and visualization

VOWEL_COORD_INFO = {
    'x_label': 'Backness',
    'y_label': 'Height',
    'x_range': (0, 2.2),  # Front to Back
    'y_range': (0, 3.2),  # Close to Open (inverted for display)
    'shape': 'trapezoid',
    'x_ticks': [(0, 'Front'), (1, 'Central'), (2, 'Back')],
    'y_ticks': [(0, 'Close'), (1, 'Close-mid'), (2, 'Open-mid'), (3, 'Open')]
}

CONSONANT_COORD_INFO = {
    'x_label': 'Place of Articulation',
    'y_label': 'Manner of Articulation',
    'x_range': (-0.5, 10.5),
    'y_range': (-0.5, 7.5),
    'shape': 'grid',
    'x_ticks': [
        (0, 'Bilabial'), (1, 'Labiodental'), (2, 'Dental'), (3, 'Alveolar'),
        (4, 'Postalveolar'), (5, 'Retroflex'), (6, 'Palatal'), (7, 'Velar'),
        (8, 'Uvular'), (9, 'Pharyngeal'), (10, 'Glottal')
    ],
    'y_ticks': [
        (0, 'Plosive'), (1, 'Nasal'), (2, 'Trill'), (3, 'Tap/Flap'),
        (4, 'Fricative'), (5, 'Lat. Fricative'), (6, 'Approximant'), (7, 'Lat. Approximant')
    ]
}