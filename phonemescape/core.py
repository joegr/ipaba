"""
Core functionality for the Phonemescape IPA library.
"""

from typing import Dict, List, Tuple, Optional, Union
import numpy as np
from .data import IPA_VOWELS, IPA_CONSONANTS
from .plotting import IPAPlotter
from .similarity import MouthShapeSimilarity


class Phonemescape:
    """
    Main class for IPA phoneme analysis and visualization.
    
    This class provides a unified interface for:
    - Accessing IPA phoneme data
    - Calculating mouth shape similarities
    - Creating 2D visualizations
    - Analyzing phoneme relationships
    """
    
    def __init__(self):
        """Initialize the Phonemescape library."""
        self.vowels = IPA_VOWELS
        self.consonants = IPA_CONSONANTS
        self.plotter = IPAPlotter()
        self.similarity_calculator = MouthShapeSimilarity()
    
    def get_all_phonemes(self) -> List[str]:
        """Get list of all available phonemes."""
        return list(self.vowels.keys()) + list(self.consonants.keys())
    
    def get_vowels(self) -> Dict[str, Tuple]:
        """Get all vowel data."""
        return self.vowels
    
    def get_consonants(self) -> Dict[str, Tuple]:
        """Get all consonant data."""
        return self.consonants
    
    def is_vowel(self, phoneme: str) -> bool:
        """Check if a phoneme is a vowel."""
        return phoneme in self.vowels
    
    def is_consonant(self, phoneme: str) -> bool:
        """Check if a phoneme is a consonant."""
        return phoneme in self.consonants
    
    def get_phoneme_info(self, phoneme: str) -> Dict:
        """Get detailed information about a phoneme."""
        if phoneme in self.vowels:
            x, y, height, backness, roundedness, description = self.vowels[phoneme]
            return {
                'symbol': phoneme,
                'type': 'vowel',
                'coordinates': (x, y),
                'height': height,
                'backness': backness,
                'roundedness': roundedness,
                'description': description
            }
        elif phoneme in self.consonants:
            x, y, manner, place, voicing, description = self.consonants[phoneme]
            return {
                'symbol': phoneme,
                'type': 'consonant',
                'coordinates': (x, y),
                'manner': manner,
                'place': place,
                'voicing': voicing,
                'description': description
            }
        else:
            raise ValueError(f"Phoneme '{phoneme}' not found")
    
    def find_similar_phonemes(self, target_phoneme: str, 
                            phoneme_type: str = 'both',
                            top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Find phonemes similar to a target phoneme.
        
        Args:
            target_phoneme: The phoneme to find similarities for
            phoneme_type: 'vowel', 'consonant', or 'both'
            top_k: Number of results to return
            
        Returns:
            List of (phoneme, similarity) tuples
        """
        # Determine which phonemes to search
        if phoneme_type == 'vowel':
            search_phonemes = list(self.vowels.keys())
        elif phoneme_type == 'consonant':
            search_phonemes = list(self.consonants.keys())
        else:  # 'both'
            search_phonemes = self.get_all_phonemes()
        
        return self.similarity_calculator.most_similar_phonemes(
            target_phoneme, search_phonemes, top_k
        )
    
    def calculate_similarity(self, phoneme1: str, phoneme2: str) -> float:
        """Calculate similarity between two phonemes."""
        return self.similarity_calculator.phoneme_similarity(phoneme1, phoneme2)
    
    def get_similarity_matrix(self, phonemes: List[str]) -> np.ndarray:
        """Calculate similarity matrix for a list of phonemes."""
        return self.similarity_calculator.similarity_matrix(phonemes)
    
    def plot_vowel_chart(self, highlight: Optional[List[str]] = None, **kwargs) -> 'plt.Figure':
        """Create vowel chart visualization."""
        return self.plotter.plot_vowel_chart(highlight_phonemes=highlight, **kwargs)
    
    def plot_consonant_chart(self, highlight: Optional[List[str]] = None, **kwargs) -> 'plt.Figure':
        """Create consonant chart visualization."""
        return self.plotter.plot_consonant_chart(highlight_phonemes=highlight, **kwargs)
    
    def plot_combined_chart(self, 
                          highlight_vowels: Optional[List[str]] = None,
                          highlight_consonants: Optional[List[str]] = None, 
                          **kwargs) -> 'plt.Figure':
        """Create combined vowel and consonant chart."""
        return self.plotter.plot_combined_chart(
            highlight_vowels=highlight_vowels,
            highlight_consonants=highlight_consonants,
            **kwargs
        )
    
    def plot_similarity_network(self, 
                             phonemes: List[str],
                             threshold: float = 0.5,
                             **kwargs) -> 'plt.Figure':
        """Plot similarity network for phonemes."""
        similarity_matrix = self.get_similarity_matrix(phonemes)
        return self.plotter.plot_similarity_network(
            phonemes, similarity_matrix, threshold, **kwargs
        )
    
    def analyze_word(self, word: str) -> Dict:
        """
        Analyze the phonemes in a word.
        
        Args:
            word: String containing IPA phoneme symbols
            
        Returns:
            Dictionary with analysis results
        """
        phonemes = list(word)  # Simple split - assumes each character is a phoneme
        
        valid_phonemes = []
        invalid_phonemes = []
        
        for phoneme in phonemes:
            if phoneme in self.vowels or phoneme in self.consonants:
                valid_phonemes.append(phoneme)
            else:
                invalid_phonemes.append(phoneme)
        
        # Calculate pairwise similarities
        if len(valid_phonemes) > 1:
            similarity_matrix = self.get_similarity_matrix(valid_phonemes)
            avg_similarity = np.mean(similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)])
        else:
            avg_similarity = 1.0
        
        return {
            'word': word,
            'phonemes': valid_phonemes,
            'invalid_phonemes': invalid_phonemes,
            'n_phonemes': len(valid_phonemes),
            'n_vowels': len([p for p in valid_phonemes if self.is_vowel(p)]),
            'n_consonants': len([p for p in valid_phonemes if self.is_consonant(p)]),
            'average_similarity': avg_similarity,
            'phoneme_details': [self.get_phoneme_info(p) for p in valid_phonemes]
        }
    
    def get_phoneme_clusters(self, phonemes: List[str], n_clusters: int = 3) -> Dict[int, List[str]]:
        """Cluster phonemes by similarity."""
        return self.similarity_calculator.cluster_phonemes(phonemes, n_clusters)
    
    def find_phonemes_by_features(self, **features) -> List[str]:
        """
        Find phonemes matching specific articulatory features.
        
        Args:
            **features: Key-value pairs of features to match
                       (e.g., height='close', place='bilabial')
                       
        Returns:
            List of matching phonemes
        """
        matches = []
        
        # Check vowels
        for phoneme, (x, y, height, backness, roundedness, _) in self.vowels.items():
            vowel_features = {
                'type': 'vowel',
                'height': height,
                'backness': backness,
                'roundedness': roundedness
            }
            
            if all(vowel_features.get(k) == v for k, v in features.items() 
                   if k in vowel_features):
                matches.append(phoneme)
        
        # Check consonants
        for phoneme, (x, y, manner, place, voicing, _) in self.consonants.items():
            consonant_features = {
                'type': 'consonant',
                'manner': manner,
                'place': place,
                'voicing': voicing
            }
            
            if all(consonant_features.get(k) == v for k, v in features.items() 
                   if k in consonant_features):
                matches.append(phoneme)
        
        return matches
    
    def export_data(self, format: str = 'dict') -> Union[Dict, str]:
        """
        Export phoneme data in various formats.
        
        Args:
            format: 'dict', 'json', or 'csv'
            
        Returns:
            Data in specified format
        """
        data = {
            'vowels': self.vowels,
            'consonants': self.consonants
        }
        
        if format == 'dict':
            return data
        elif format == 'json':
            import json
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == 'csv':
            # Create CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write vowels
            writer.writerow(['Type', 'Symbol', 'X', 'Y', 'Feature1', 'Feature2', 'Feature3', 'Description'])
            for symbol, (x, y, f1, f2, f3, desc) in self.vowels.items():
                writer.writerow(['vowel', symbol, x, y, f1, f2, f3, desc])
            
            # Write consonants
            for symbol, (x, y, f1, f2, f3, desc) in self.consonants.items():
                writer.writerow(['consonant', symbol, x, y, f1, f2, f3, desc])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
