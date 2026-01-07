"""
Phonemescape: International Phonetic Alphabet (IPA) Library
A Python library for IPA phoneme visualization and mouth shape similarity analysis.
"""

from .core import Phonemescape
from .data import IPA_VOWELS, IPA_CONSONANTS
from .plotting import IPAPlotter
from .similarity import MouthShapeSimilarity

__version__ = "0.1.0"
__author__ = "Phonemescape Team"

__all__ = [
    "Phonemescape",
    "IPA_VOWELS", 
    "IPA_CONSONANTS",
    "IPAPlotter",
    "MouthShapeSimilarity"
]
