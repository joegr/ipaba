"""
IPA phoneme data with coordinates for visualization and similarity analysis.
Coordinates are based on standard IPA chart positions.
"""

# Vowel data: (symbol, x_coord, y_coord, height, backness, roundedness, description)
IPA_VOWELS = {
    # Close vowels (top row)
    'i': (1, 5, 'close', 'front', 'unrounded', 'Close front unrounded vowel'),
    'y': (2, 5, 'close', 'front', 'rounded', 'Close front rounded vowel'),
    'ɨ': (3, 5, 'close', 'central', 'unrounded', 'Close central unrounded vowel'),
    'ʉ': (4, 5, 'close', 'central', 'rounded', 'Close central rounded vowel'),
    'ɯ': (5, 5, 'close', 'back', 'unrounded', 'Close back unrounded vowel'),
    'u': (6, 5, 'close', 'back', 'rounded', 'Close back rounded vowel'),
    
    # Near-close vowels
    'ɪ': (1, 4, 'near-close', 'near-front', 'unrounded', 'Near-close near-front unrounded vowel'),
    'ʏ': (2, 4, 'near-close', 'near-front', 'rounded', 'Near-close near-front rounded vowel'),
    'ʊ': (5, 4, 'near-close', 'near-back', 'rounded', 'Near-close near-back rounded vowel'),
    
    # Close-mid vowels
    'e': (1, 3, 'close-mid', 'front', 'unrounded', 'Close-mid front unrounded vowel'),
    'ø': (2, 3, 'close-mid', 'front', 'rounded', 'Close-mid front rounded vowel'),
    'ɘ': (3, 3, 'close-mid', 'central', 'unrounded', 'Close-mid central unrounded vowel'),
    'ɵ': (4, 3, 'close-mid', 'central', 'rounded', 'Close-mid central rounded vowel'),
    'ɤ': (5, 3, 'close-mid', 'back', 'unrounded', 'Close-mid back unrounded vowel'),
    'o': (6, 3, 'close-mid', 'back', 'rounded', 'Close-mid back rounded vowel'),
    
    # Mid vowels
    'e̞': (1, 2, 'mid', 'front', 'unrounded', 'Mid front unrounded vowel'),
    'ø̞': (2, 2, 'mid', 'front', 'rounded', 'Mid front rounded vowel'),
    'ə': (3, 2, 'mid', 'central', 'unrounded', 'Mid central vowel (schwa)'),
    'ɤ̞': (5, 2, 'mid', 'back', 'unrounded', 'Mid back unrounded vowel'),
    'o̞': (6, 2, 'mid', 'back', 'rounded', 'Mid back rounded vowel'),
    
    # Open-mid vowels
    'ɛ': (1, 1, 'open-mid', 'front', 'unrounded', 'Open-mid front unrounded vowel'),
    'œ': (2, 1, 'open-mid', 'front', 'rounded', 'Open-mid front rounded vowel'),
    'ɜ': (3, 1, 'open-mid', 'central', 'unrounded', 'Open-mid central unrounded vowel'),
    'ɞ': (4, 1, 'open-mid', 'central', 'rounded', 'Open-mid central rounded vowel'),
    'ʌ': (5, 1, 'open-mid', 'back', 'unrounded', 'Open-mid back unrounded vowel'),
    'ɔ': (6, 1, 'open-mid', 'back', 'rounded', 'Open-mid back rounded vowel'),
    
    # Near-open vowels
    'æ': (1, 0, 'near-open', 'front', 'unrounded', 'Near-open front unrounded vowel'),
    'ɐ': (3, 0, 'near-open', 'central', 'unrounded', 'Near-open central vowel'),
    
    # Open vowels (bottom row)
    'a': (1, -1, 'open', 'front', 'unrounded', 'Open front unrounded vowel'),
    'ɶ': (2, -1, 'open', 'front', 'rounded', 'Open front rounded vowel'),
    'ä': (3, -1, 'open', 'central', 'unrounded', 'Open central unrounded vowel'),
    'ɑ': (5, -1, 'open', 'back', 'unrounded', 'Open back unrounded vowel'),
    'ɒ': (6, -1, 'open', 'back', 'rounded', 'Open back rounded vowel'),
}

# Consonant data: (symbol, x_coord, y_coord, manner, place, voicing, description)
# Places: Bilabial(1), Labiodental(2), Dental(3), Alveolar(4), Postalveolar(5), 
# Retroflex(6), Palatal(7), Velar(8), Uvular(9), Glottal(10)
# Manners: Nasal(6), Plosive(5), Fricative(4), Affricate(3), Approximant(2), Trill(1)
IPA_CONSONANTS = {
    # Nasals
    'm': (1, 6, 'nasal', 'bilabial', 'voiced', 'Bilabial nasal'),
    'm̥': (1, 6, 'nasal', 'bilabial', 'voiceless', 'Voiceless bilabial nasal'),
    'ɱ': (2, 6, 'nasal', 'labiodental', 'voiced', 'Labiodental nasal'),
    'n': (4, 6, 'nasal', 'alveolar', 'voiced', 'Alveolar nasal'),
    'n̪': (3, 6, 'nasal', 'dental', 'voiced', 'Dental nasal'),
    'ɳ': (6, 6, 'nasal', 'retroflex', 'voiced', 'Retroflex nasal'),
    'ɲ': (7, 6, 'nasal', 'palatal', 'voiced', 'Palatal nasal'),
    'ŋ': (8, 6, 'nasal', 'velar', 'voiced', 'Velar nasal'),
    'ɴ': (9, 6, 'nasal', 'uvular', 'voiced', 'Uvular nasal'),
    
    # Plosives
    'p': (1, 5, 'plosive', 'bilabial', 'voiceless', 'Voiceless bilabial plosive'),
    'b': (1, 5, 'plosive', 'bilabial', 'voiced', 'Voiced bilabial plosive'),
    'p̪': (2, 5, 'plosive', 'labiodental', 'voiceless', 'Voiceless labiodental plosive'),
    'b̪': (2, 5, 'plosive', 'labiodental', 'voiced', 'Voiced labiodental plosive'),
    't': (4, 5, 'plosive', 'alveolar', 'voiceless', 'Voiceless alveolar plosive'),
    'd': (4, 5, 'plosive', 'alveolar', 'voiced', 'Voiced alveolar plosive'),
    't̪': (3, 5, 'plosive', 'dental', 'voiceless', 'Voiceless dental plosive'),
    'd̪': (3, 5, 'plosive', 'dental', 'voiced', 'Voiced dental plosive'),
    'ʈ': (6, 5, 'plosive', 'retroflex', 'voiceless', 'Voiceless retroflex plosive'),
    'ɖ': (6, 5, 'plosive', 'retroflex', 'voiced', 'Voiced retroflex plosive'),
    'c': (7, 5, 'plosive', 'palatal', 'voiceless', 'Voiceless palatal plosive'),
    'ɟ': (7, 5, 'plosive', 'palatal', 'voiced', 'Voiced palatal plosive'),
    'k': (8, 5, 'plosive', 'velar', 'voiceless', 'Voiceless velar plosive'),
    'g': (8, 5, 'plosive', 'velar', 'voiced', 'Voiced velar plosive'),
    'q': (9, 5, 'plosive', 'uvular', 'voiceless', 'Voiceless uvular plosive'),
    'ɢ': (9, 5, 'plosive', 'uvular', 'voiced', 'Voiced uvular plosive'),
    'ʔ': (10, 5, 'plosive', 'glottal', 'voiceless', 'Glottal stop'),
    
    # Fricatives
    'ɸ': (1, 4, 'fricative', 'bilabial', 'voiceless', 'Voiceless bilabial fricative'),
    'β': (1, 4, 'fricative', 'bilabial', 'voiced', 'Voiced bilabial fricative'),
    'f': (2, 4, 'fricative', 'labiodental', 'voiceless', 'Voiceless labiodental fricative'),
    'v': (2, 4, 'fricative', 'labiodental', 'voiced', 'Voiced labiodental fricative'),
    'θ': (3, 4, 'fricative', 'dental', 'voiceless', 'Voiceless dental fricative'),
    'ð': (3, 4, 'fricative', 'dental', 'voiced', 'Voiced dental fricative'),
    's': (4, 4, 'fricative', 'alveolar', 'voiceless', 'Voiceless alveolar fricative'),
    'z': (4, 4, 'fricative', 'alveolar', 'voiced', 'Voiced alveolar fricative'),
    'ʃ': (5, 4, 'fricative', 'postalveolar', 'voiceless', 'Voiceless postalveolar fricative'),
    'ʒ': (5, 4, 'fricative', 'postalveolar', 'voiced', 'Voiced postalveolar fricative'),
    'ʂ': (6, 4, 'fricative', 'retroflex', 'voiceless', 'Voiceless retroflex fricative'),
    'ʐ': (6, 4, 'fricative', 'retroflex', 'voiced', 'Voiced retroflex fricative'),
    'ç': (7, 4, 'fricative', 'palatal', 'voiceless', 'Voiceless palatal fricative'),
    'ʝ': (7, 4, 'fricative', 'palatal', 'voiced', 'Voiced palatal fricative'),
    'x': (8, 4, 'fricative', 'velar', 'voiceless', 'Voiceless velar fricative'),
    'ɣ': (8, 4, 'fricative', 'velar', 'voiced', 'Voiced velar fricative'),
    'χ': (9, 4, 'fricative', 'uvular', 'voiceless', 'Voiceless uvular fricative'),
    'ʁ': (9, 4, 'fricative', 'uvular', 'voiced', 'Voiced uvular fricative'),
    'h': (10, 4, 'fricative', 'glottal', 'voiceless', 'Voiceless glottal fricative'),
    'ɦ': (10, 4, 'fricative', 'glottal', 'voiced', 'Voiced glottal fricative'),
    
    # Affricates
    't̪s̪': (3, 3, 'affricate', 'dental', 'voiceless', 'Voiceless dental affricate'),
    'd̪z̪': (3, 3, 'affricate', 'dental', 'voiced', 'Voiced dental affricate'),
    'ts': (4, 3, 'affricate', 'alveolar', 'voiceless', 'Voiceless alveolar affricate'),
    'dz': (4, 3, 'affricate', 'alveolar', 'voiced', 'Voiced alveolar affricate'),
    't̠ʃ': (5, 3, 'affricate', 'postalveolar', 'voiceless', 'Voiceless postalveolar affricate'),
    'd̠ʒ': (5, 3, 'affricate', 'postalveolar', 'voiced', 'Voiced postalveolar affricate'),
    'tʂ': (6, 3, 'affricate', 'retroflex', 'voiceless', 'Voiceless retroflex affricate'),
    'dʐ': (6, 3, 'affricate', 'retroflex', 'voiced', 'Voiced retroflex affricate'),
    'cç': (7, 3, 'affricate', 'palatal', 'voiceless', 'Voiceless palatal affricate'),
    'ɟʝ': (7, 3, 'affricate', 'palatal', 'voiced', 'Voiced palatal affricate'),
    'kx': (8, 3, 'affricate', 'velar', 'voiceless', 'Voiceless velar affricate'),
    'gɣ': (8, 3, 'affricate', 'velar', 'voiced', 'Voiced velar affricate'),
    
    # Approximants
    'ʋ': (2, 2, 'approximant', 'labiodental', 'voiced', 'Labiodental approximant'),
    'ɹ': (4, 2, 'approximant', 'alveolar', 'voiced', 'Alveolar approximant'),
    'ɻ': (6, 2, 'approximant', 'retroflex', 'voiced', 'Retroflex approximant'),
    'j': (7, 2, 'approximant', 'palatal', 'voiced', 'Palatal approximant'),
    'ɰ': (8, 2, 'approximant', 'velar', 'voiced', 'Velar approximant'),
    
    # Trills
    'ʙ': (1, 1, 'trill', 'bilabial', 'voiced', 'Bilabial trill'),
    'r': (4, 1, 'trill', 'alveolar', 'voiced', 'Alveolar trill'),
    'ʀ': (9, 1, 'trill', 'uvular', 'voiced', 'Uvular trill'),
    
    # Lateral approximants
    'l': (4, 0, 'approximant', 'alveolar', 'voiced', 'Alveolar lateral approximant'),
    'ɭ': (6, 0, 'approximant', 'retroflex', 'voiced', 'Retroflex lateral approximant'),
    'ʎ': (7, 0, 'approximant', 'palatal', 'voiced', 'Palatal lateral approximant'),
    'ʟ': (8, 0, 'approximant', 'velar', 'voiced', 'Velar lateral approximant'),
}

# Mapping of articulatory features to numerical values for similarity calculations
ARTICULATORY_FEATURES = {
    'vowel_height': {'close': 5, 'near-close': 4, 'close-mid': 3, 'mid': 2, 'open-mid': 1, 'near-open': 0, 'open': -1},
    'vowel_backness': {'front': 1, 'near-front': 2, 'central': 3, 'near-back': 4, 'back': 5},
    'vowel_roundedness': {'rounded': 1, 'unrounded': 0},
    'consonant_place': {'bilabial': 1, 'labiodental': 2, 'dental': 3, 'alveolar': 4, 'postalveolar': 5, 
                       'retroflex': 6, 'palatal': 7, 'velar': 8, 'uvular': 9, 'glottal': 10},
    'consonant_manner': {'trill': 1, 'approximant': 2, 'affricate': 3, 'fricative': 4, 'plosive': 5, 'nasal': 6},
    'consonant_voicing': {'voiced': 1, 'voiceless': 0}
}