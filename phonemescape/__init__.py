"""
Phonemescape: International Phonetic Alphabet (IPA) Library
IPA segment tokenization, distinctive features, articulatory similarity
and chart visualization.
"""

from .core import Phonemescape
from .data import (
    ALL_CONSONANTS, IPA_CONSONANTS, IPA_NON_PULMONIC, IPA_OTHER_CONSONANTS, IPA_VOWELS,
)
from .features import FEATURE_NAMES
from .plotting import IPAPlotter
from .segments import Segment, Token, get_segment, segments, tokenize
from .similarity import MouthShapeSimilarity

__version__ = "0.2.0"
__author__ = "Phonemescape Team"

__all__ = [
    "Phonemescape",
    "IPA_VOWELS",
    "IPA_CONSONANTS",
    "IPA_OTHER_CONSONANTS",
    "IPA_NON_PULMONIC",
    "ALL_CONSONANTS",
    "FEATURE_NAMES",
    "IPAPlotter",
    "MouthShapeSimilarity",
    "Segment",
    "Token",
    "get_segment",
    "segments",
    "tokenize",
]
