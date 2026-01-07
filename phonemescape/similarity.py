"""
Mouth shape similarity analysis for IPA phonemes.
Calculates similarity based on articulatory features and IPA chart proximity.

IMPORTANT: Vowels and consonants are on SEPARATE coordinate planes.
Similarity between a vowel and consonant is always 0 (incomparable).
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from .data import IPA_VOWELS, IPA_CONSONANTS, ARTICULATORY_FEATURES, VOWEL_COORD_INFO, CONSONANT_COORD_INFO


class MouthShapeSimilarity:
    """Calculates mouth shape similarity between IPA phonemes."""
    
    def __init__(self):
        self.vowel_data = IPA_VOWELS
        self.consonant_data = IPA_CONSONANTS
        self.features = ARTICULATORY_FEATURES
        
        # Precompute feature vectors for all phonemes
        self.feature_vectors = self._compute_feature_vectors()
    
    def _compute_feature_vectors(self) -> Dict[str, np.ndarray]:
        """
        Compute feature vectors for all phonemes.
        
        Vowels and consonants have SEPARATE vector spaces:
        - Vowels: [x_coord, y_coord, roundedness] on trapezoid plane
        - Consonants: [x_coord, y_coord, voicing] on grid plane
        
        These vectors should NEVER be compared across types.
        """
        vectors = {}
        
        # Vowel feature vectors based on trapezoid coordinates
        # Vector: [x (backness), y (height), roundedness]
        for symbol, (x, y, height, backness, roundedness, _) in self.vowel_data.items():
            vector = np.array([
                x,  # Trapezoid x coordinate (backness: 0=front, 2=back)
                y,  # Trapezoid y coordinate (height: 0=close, 3=open)
                self.features['vowel_roundedness'][roundedness]
            ], dtype=float)
            vectors[symbol] = vector
        
        # Consonant feature vectors based on grid coordinates
        # Vector: [x (place), y (manner), voicing]
        for symbol, (x, y, manner, place, voicing, _) in self.consonant_data.items():
            vector = np.array([
                x,  # Grid x coordinate (place: 0=bilabial, 10=glottal)
                y,  # Grid y coordinate (manner: 0=plosive, 7=lateral approx)
                self.features['consonant_voicing'][voicing]
            ], dtype=float)
            vectors[symbol] = vector
        
        return vectors
    
    def phoneme_similarity(self, phoneme1: str, phoneme2: str) -> float:
        """
        Calculate similarity between two phonemes based on mouth shape proximity.
        
        IMPORTANT: Vowels and consonants are on SEPARATE coordinate planes.
        Comparing a vowel to a consonant returns 0.0 (incomparable).
        
        Args:
            phoneme1: First phoneme symbol
            phoneme2: Second phoneme symbol
            
        Returns:
            Similarity score between 0 and 1
        """
        if phoneme1 not in self.feature_vectors or phoneme2 not in self.feature_vectors:
            raise ValueError(f"One or both phonemes not found: {phoneme1}, {phoneme2}")
        
        # Check if both are vowels or both are consonants
        both_vowels = phoneme1 in self.vowel_data and phoneme2 in self.vowel_data
        both_consonants = phoneme1 in self.consonant_data and phoneme2 in self.consonant_data
        
        if not (both_vowels or both_consonants):
            # Different types (vowel vs consonant) - INCOMPARABLE on different planes
            return 0.0
        
        # Get vectors
        vector1 = self.feature_vectors[phoneme1]
        vector2 = self.feature_vectors[phoneme2]
        
        if both_vowels:
            # Vowel similarity based on trapezoid distance
            # Max distance on vowel trapezoid: ~3.6 (diagonal from i to ɒ)
            max_distance = 3.6
            euclidean_distance = np.linalg.norm(vector1[:2] - vector2[:2])
            
            # Roundedness penalty (different roundedness = less similar)
            roundedness_match = 1.0 if vector1[2] == vector2[2] else 0.8
            
            # Distance-based similarity
            distance_sim = 1 - (euclidean_distance / max_distance)
            
            return max(0, min(1, distance_sim * roundedness_match))
        
        else:  # both_consonants
            # Consonant similarity based on grid distance
            # Max distance on consonant grid: ~12.7 (diagonal from p to ʟ)
            max_distance = 12.7
            euclidean_distance = np.linalg.norm(vector1[:2] - vector2[:2])
            
            # Voicing penalty (different voicing = slightly less similar)
            voicing_match = 1.0 if vector1[2] == vector2[2] else 0.9
            
            # Distance-based similarity
            distance_sim = 1 - (euclidean_distance / max_distance)
            
            return max(0, min(1, distance_sim * voicing_match))
    
    def similarity_matrix(self, phonemes: List[str]) -> np.ndarray:
        """
        Calculate similarity matrix for a list of phonemes.
        
        Args:
            phonemes: List of phoneme symbols
            
        Returns:
            n x n similarity matrix
        """
        n = len(phonemes)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i, j] = 1.0  # Perfect similarity with self
                else:
                    matrix[i, j] = self.phoneme_similarity(phonemes[i], phonemes[j])
        
        return matrix
    
    def most_similar_phonemes(self, target_phoneme: str, 
                            phoneme_list: Optional[List[str]] = None,
                            top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find most similar phonemes to a target phoneme.
        
        Args:
            target_phoneme: Phoneme to find similarities for
            phoneme_list: List of phonemes to search in (default: all phonemes)
            top_k: Number of top results to return
            
        Returns:
            List of (phoneme, similarity) tuples sorted by similarity
        """
        if target_phoneme not in self.feature_vectors:
            raise ValueError(f"Target phoneme not found: {target_phoneme}")
        
        if phoneme_list is None:
            phoneme_list = list(self.feature_vectors.keys())
        
        # Remove target phoneme from list if present
        search_list = [p for p in phoneme_list if p != target_phoneme]
        
        # Calculate similarities
        similarities = []
        for phoneme in search_list:
            try:
                sim = self.phoneme_similarity(target_phoneme, phoneme)
                similarities.append((phoneme, sim))
            except ValueError:
                continue
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def mouth_shape_distance(self, phoneme1: str, phoneme2: str) -> float:
        """
        Calculate mouth shape distance based on IPA chart coordinates.
        
        IMPORTANT: Only valid for phonemes of the same type (both vowels or both consonants).
        Returns infinity for cross-type comparisons.
        
        Args:
            phoneme1: First phoneme symbol
            phoneme2: Second phoneme symbol
            
        Returns:
            Euclidean distance between phonemes on their respective IPA chart plane
        """
        if phoneme1 not in self.feature_vectors or phoneme2 not in self.feature_vectors:
            raise ValueError(f"One or both phonemes not found: {phoneme1}, {phoneme2}")
        
        # Check if same type
        both_vowels = phoneme1 in self.vowel_data and phoneme2 in self.vowel_data
        both_consonants = phoneme1 in self.consonant_data and phoneme2 in self.consonant_data
        
        if not (both_vowels or both_consonants):
            return float('inf')  # Incomparable - different planes
        
        # Extract coordinates (first 2 elements of vector)
        coord1 = self.feature_vectors[phoneme1][:2]
        coord2 = self.feature_vectors[phoneme2][:2]
        
        return np.linalg.norm(coord1 - coord2)
    
    def articulatory_feature_distance(self, phoneme1: str, phoneme2: str) -> float:
        """
        Calculate distance based on all articulatory features.
        
        IMPORTANT: Only valid for phonemes of the same type.
        Returns infinity for cross-type comparisons.
        
        Args:
            phoneme1: First phoneme symbol
            phoneme2: Second phoneme symbol
            
        Returns:
            Distance based on articulatory features
        """
        if phoneme1 not in self.feature_vectors or phoneme2 not in self.feature_vectors:
            raise ValueError(f"One or both phonemes not found: {phoneme1}, {phoneme2}")
        
        # Check if same type
        both_vowels = phoneme1 in self.vowel_data and phoneme2 in self.vowel_data
        both_consonants = phoneme1 in self.consonant_data and phoneme2 in self.consonant_data
        
        if not (both_vowels or both_consonants):
            return float('inf')  # Incomparable - different types
        
        # Full feature vector comparison
        feat1 = self.feature_vectors[phoneme1]
        feat2 = self.feature_vectors[phoneme2]
        
        return np.linalg.norm(feat1 - feat2)
    
    def is_vowel(self, phoneme: str) -> bool:
        """Check if phoneme is a vowel."""
        return phoneme in self.vowel_data
    
    def is_consonant(self, phoneme: str) -> bool:
        """Check if phoneme is a consonant."""
        return phoneme in self.consonant_data
    
    def get_vowels(self) -> List[str]:
        """Get list of all vowel symbols."""
        return list(self.vowel_data.keys())
    
    def get_consonants(self) -> List[str]:
        """Get list of all consonant symbols."""
        return list(self.consonant_data.keys())
    
    def cluster_phonemes(self, phonemes: List[str], n_clusters: int = 3) -> Dict[int, List[str]]:
        """
        Simple clustering of phonemes based on similarity.
        
        Args:
            phonemes: List of phonemes to cluster
            n_clusters: Number of clusters to create
            
        Returns:
            Dictionary mapping cluster index to list of phonemes
        """
        from sklearn.cluster import KMeans
        
        # Get feature vectors for the specified phonemes
        vectors = [self.feature_vectors[p] for p in phonemes]
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(vectors)
        
        # Group phonemes by cluster
        clusters = {}
        for phoneme, label in zip(phonemes, cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(phoneme)
        
        return clusters
    
    def get_phoneme_description(self, phoneme: str) -> str:
        """Get description of a phoneme."""
        if phoneme in self.vowel_data:
            return self.vowel_data[phoneme][-1]
        elif phoneme in self.consonant_data:
            return self.consonant_data[phoneme][-1]
        else:
            return f"Phoneme {phoneme} not found"
    
    def get_phoneme_features(self, phoneme: str) -> Dict[str, str]:
        """Get articulatory features of a phoneme."""
        if phoneme in self.vowel_data:
            _, _, height, backness, roundedness, _ = self.vowel_data[phoneme]
            return {
                'type': 'vowel',
                'height': height,
                'backness': backness,
                'roundedness': roundedness
            }
        elif phoneme in self.consonant_data:
            _, _, manner, place, voicing, _ = self.consonant_data[phoneme]
            return {
                'type': 'consonant',
                'manner': manner,
                'place': place,
                'voicing': voicing
            }
        else:
            return {'type': 'unknown'}
