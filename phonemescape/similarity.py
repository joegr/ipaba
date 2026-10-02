"""
Articulatory similarity between IPA segments.

Similarity combines two components:

1. **Distinctive-feature similarity** (primary): one minus the normalised,
   optionally weighted Hamming distance between the segments' feature
   bundles (see ``features.py``).  A +/- mismatch costs 1, a mismatch
   between a specified and an unspecified (0) value costs 0.5, and only
   features specified for at least one of the two segments are counted.
   This defines similarity for ANY pair of segments, including
   vowel/consonant pairs (i ~ j, u ~ w).

2. **Chart proximity** (secondary): Euclidean distance between the
   segments' articulatory points on their own chart plane (vowel trapezoid
   or consonant grid), normalised by the largest distance on that plane.
   Chart proximity only exists within a plane; between a vowel and a
   consonant there is no shared chart, so that component scores 0 and the
   two kinds of pair stay on one comparable scale.

    sim = feature_weight * feature_sim + (1 - feature_weight) * chart_sim
    (chart_sim = 0 across planes)

Scores range from 0 to 1; identical segments score 1.
"""

from itertools import combinations
from typing import Dict, List, Optional, Tuple

import numpy as np

from .data import ALL_CONSONANTS, ARTICULATORY_FEATURES, IPA_VOWELS
from .features import FEATURE_NAMES
from .segments import Segment, get_segment, inventory

#: Weight of the feature component when both segments share a chart plane.
DEFAULT_FEATURE_WEIGHT = 0.75


class MouthShapeSimilarity:
    """Calculates articulatory similarity between IPA segments."""

    def __init__(self, feature_weight: float = DEFAULT_FEATURE_WEIGHT,
                 feature_weights: Optional[Dict[str, float]] = None):
        """
        Args:
            feature_weight: share of the feature component (0..1) for
                same-plane comparisons; the rest is chart proximity.
            feature_weights: optional per-feature weights (default 1 each).
        """
        if not 0.0 <= feature_weight <= 1.0:
            raise ValueError("feature_weight must be between 0 and 1")
        unknown = set(feature_weights or {}) - set(FEATURE_NAMES)
        if unknown:
            raise ValueError(f"Unknown features: {sorted(unknown)}")
        self.feature_weight = feature_weight
        self.weights = np.array([(feature_weights or {}).get(f, 1.0) for f in FEATURE_NAMES])
        self.vowel_data = IPA_VOWELS
        self.consonant_data = ALL_CONSONANTS
        self.features = ARTICULATORY_FEATURES
        self.segments = inventory()
        #: Distinctive-feature vectors (+1/-1/0) of every chart symbol.
        self.feature_vectors: Dict[str, np.ndarray] = {
            s: seg.feature_vector for s, seg in self.segments.items()
        }
        self._max_distance = {
            kind: self._plane_diameter(kind) for kind in ('vowel', 'consonant')
        }

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _plane_diameter(self, kind: str) -> float:
        points = [np.array(s.position) for s in self.segments.values() if s.kind == kind]
        return max(float(np.linalg.norm(a - b)) for a, b in combinations(points, 2))

    @staticmethod
    def _resolve(phoneme: str) -> Segment:
        try:
            return get_segment(phoneme)
        except ValueError:
            raise ValueError(f"Not an IPA segment: {phoneme!r}") from None

    # ------------------------------------------------------------------
    # components
    # ------------------------------------------------------------------

    def feature_similarity(self, phoneme1: str, phoneme2: str) -> float:
        """Distinctive-feature similarity (0..1), defined for every pair."""
        a = self._resolve(phoneme1).feature_vector
        b = self._resolve(phoneme2).feature_vector
        specified = (a != 0) | (b != 0)
        if not specified.any():
            return 1.0
        cost = np.abs(a - b) / 2          # 1 for +/-, 0.5 for +/0, 0 for match
        w = self.weights * specified
        return float(1 - (cost * w).sum() / w.sum())

    def chart_similarity(self, phoneme1: str, phoneme2: str) -> Optional[float]:
        """Chart-proximity similarity (0..1), or None across planes."""
        s1, s2 = self._resolve(phoneme1), self._resolve(phoneme2)
        if s1.kind != s2.kind:
            return None
        d = float(np.linalg.norm(np.array(s1.position) - np.array(s2.position)))
        return max(0.0, 1 - d / self._max_distance[s1.kind])

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def phoneme_similarity(self, phoneme1: str, phoneme2: str) -> float:
        """
        Similarity between two segments (0..1).

        Identical segments score 1.  Accepts any single IPA segment, with diacritics or tie bars
        ('tʰ', 'ã', 't͡ʃ').  Raises ValueError for anything else.
        """
        feat = self.feature_similarity(phoneme1, phoneme2)
        chart = self.chart_similarity(phoneme1, phoneme2) or 0.0
        sim = self.feature_weight * feat + (1 - self.feature_weight) * chart
        return float(min(1.0, max(0.0, sim)))

    def similarity_matrix(self, phonemes: List[str]) -> np.ndarray:
        """n x n symmetric similarity matrix with ones on the diagonal."""
        n = len(phonemes)
        matrix = np.eye(n)
        for i, j in combinations(range(n), 2):
            matrix[i, j] = matrix[j, i] = self.phoneme_similarity(phonemes[i], phonemes[j])
        return matrix

    def most_similar_phonemes(self, target_phoneme: str,
                              phoneme_list: Optional[List[str]] = None,
                              top_k: int = 5) -> List[Tuple[str, float]]:
        """The ``top_k`` segments most similar to the target."""
        target = self._resolve(target_phoneme)
        if phoneme_list is None:
            phoneme_list = list(self.segments)
        scored = []
        for phoneme in phoneme_list:
            try:
                if self._resolve(phoneme).symbol == target.symbol:
                    continue
                scored.append((phoneme, self.phoneme_similarity(target_phoneme, phoneme)))
            except ValueError:
                continue
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def mouth_shape_distance(self, phoneme1: str, phoneme2: str) -> float:
        """
        Euclidean distance between the segments' articulatory points on
        their chart plane.  Infinite across planes (vowel vs consonant).
        """
        s1, s2 = self._resolve(phoneme1), self._resolve(phoneme2)
        if s1.kind != s2.kind:
            return float('inf')
        return float(np.linalg.norm(np.array(s1.position) - np.array(s2.position)))

    def articulatory_feature_distance(self, phoneme1: str, phoneme2: str) -> float:
        """
        Weighted Hamming distance between distinctive-feature bundles
        (+/- mismatch = 1, specified/unspecified mismatch = 0.5).
        Defined for every pair of segments.
        """
        a = self._resolve(phoneme1).feature_vector
        b = self._resolve(phoneme2).feature_vector
        return float((np.abs(a - b) / 2 * self.weights).sum())

    def differing_features(self, phoneme1: str, phoneme2: str) -> Dict[str, Tuple[str, str]]:
        """Features on which two segments disagree, as '+', '-', '0' pairs."""
        sym = {1: '+', -1: '-', 0: '0'}
        f1 = self._resolve(phoneme1).feature_dict
        f2 = self._resolve(phoneme2).feature_dict
        return {k: (sym[f1[k]], sym[f2[k]]) for k in FEATURE_NAMES if f1[k] != f2[k]}

    def sequence_distance(self, seq1: List[str], seq2: List[str]) -> float:
        """
        Weighted (phonetic) edit distance between two segment sequences:
        substituting a for b costs 1 - similarity(a, b); inserting or
        deleting a segment costs 1.
        """
        n, m = len(seq1), len(seq2)
        prev = [float(j) for j in range(m + 1)]
        for i in range(1, n + 1):
            cur = [float(i)] + [0.0] * m
            for j in range(1, m + 1):
                sub = 0.0 if seq1[i - 1] == seq2[j - 1] else \
                    1 - self.phoneme_similarity(seq1[i - 1], seq2[j - 1])
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + sub)
            prev = cur
        return prev[m]

    def sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """Alignment similarity of two segment sequences (0..1):
        1 - sequence_distance / length of the longer sequence."""
        longest = max(len(seq1), len(seq2))
        if longest == 0:
            return 1.0
        return 1 - self.sequence_distance(seq1, seq2) / longest

    def is_vowel(self, phoneme: str) -> bool:
        try:
            return self._resolve(phoneme).kind == 'vowel'
        except ValueError:
            return False

    def is_consonant(self, phoneme: str) -> bool:
        try:
            return self._resolve(phoneme).kind == 'consonant'
        except ValueError:
            return False

    def get_vowels(self) -> List[str]:
        return list(self.vowel_data)

    def get_consonants(self) -> List[str]:
        return list(self.consonant_data)

    def cluster_phonemes(self, phonemes: List[str], n_clusters: int = 3) -> Dict[int, List[str]]:
        """
        Agglomerative clustering on distinctive-feature distance (average
        linkage), so clusters correspond to feature-defined natural groups.
        """
        from sklearn.cluster import AgglomerativeClustering

        if n_clusters > len(phonemes):
            raise ValueError("n_clusters cannot exceed the number of phonemes")
        if n_clusters == len(phonemes):
            return {i: [p] for i, p in enumerate(phonemes)}
        distances = 1 - self.similarity_matrix(phonemes)
        model = AgglomerativeClustering(n_clusters=n_clusters, metric='precomputed',
                                        linkage='average')
        labels = model.fit_predict(distances)
        clusters: Dict[int, List[str]] = {}
        for phoneme, label in zip(phonemes, labels):
            clusters.setdefault(int(label), []).append(phoneme)
        return clusters

    def get_phoneme_description(self, phoneme: str) -> str:
        try:
            return self._resolve(phoneme).description
        except ValueError:
            return f"Phoneme {phoneme} not found"

    def get_phoneme_features(self, phoneme: str) -> Dict[str, str]:
        try:
            seg = self._resolve(phoneme)
        except ValueError:
            return {'type': 'unknown'}
        attrs = seg.attribute_dict
        keys = ('height', 'backness', 'roundedness') if seg.kind == 'vowel' \
            else ('manner', 'place', 'voicing')
        return {'type': seg.kind, **{k: attrs[k] for k in keys}}
