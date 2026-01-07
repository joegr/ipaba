"""
2D plotting functionality for IPA phoneme visualization.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Dict, List, Tuple, Optional
from .data import IPA_VOWELS, IPA_CONSONANTS


class IPAPlotter:
    """Handles 2D plotting of IPA phonemes on vowel and consonant charts."""
    
    def __init__(self):
        self.fig_size = (12, 8)
        self.vowel_colors = {
            'unrounded': '#FF6B6B',  # Red for unrounded
            'rounded': '#4ECDC4'      # Teal for rounded
        }
        self.consonant_colors = {
            'voiceless': '#95A5A6',   # Gray for voiceless
            'voiced': '#3498DB'       # Blue for voiced
        }
    
    def plot_vowel_chart(self, 
                        highlight_phonemes: Optional[List[str]] = None,
                        show_grid: bool = True,
                        title: str = "IPA Vowel Chart") -> plt.Figure:
        """
        Create a 2D plot of IPA vowels.
        
        Args:
            highlight_phonemes: List of vowel symbols to highlight
            show_grid: Whether to show grid lines
            title: Plot title
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Plot vowels
        for symbol, (x, y, height, backness, roundedness, description) in IPA_VOWELS.items():
            color = self.vowel_colors[roundedness]
            size = 300 if highlight_phonemes and symbol in highlight_phonemes else 200
            alpha = 1.0 if highlight_phonemes and symbol in highlight_phonemes else 0.7
            
            ax.scatter(x, y, s=size, c=color, alpha=alpha, edgecolors='black', linewidth=1)
            ax.annotate(symbol, (x, y), fontsize=14, ha='center', va='center', fontweight='bold')
        
        # Set up axes
        ax.set_xlim(0, 7)
        ax.set_ylim(-2, 6)
        ax.set_xlabel('Tongue Backness → Front to Back', fontsize=12)
        ax.set_ylabel('Tongue Height → Close to Open', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        # Add axis labels for vowel positions
        ax.set_xticks([1, 2, 3, 4, 5, 6])
        ax.set_xticklabels(['Front', '', 'Central', '', '', 'Back'])
        ax.set_yticks([-1, 0, 1, 2, 3, 4, 5])
        ax.set_yticklabels(['Open', 'Near-open', 'Open-mid', 'Mid', 'Close-mid', 'Near-close', 'Close'])
        
        # Add legend
        legend_elements = [
            patches.Patch(color=self.vowel_colors['unrounded'], label='Unrounded'),
            patches.Patch(color=self.vowel_colors['rounded'], label='Rounded')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def plot_consonant_chart(self,
                           highlight_phonemes: Optional[List[str]] = None,
                           show_grid: bool = True,
                           title: str = "IPA Consonant Chart") -> plt.Figure:
        """
        Create a 2D plot of IPA consonants.
        
        Args:
            highlight_phonemes: List of consonant symbols to highlight
            show_grid: Whether to show grid lines
            title: Plot title
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Plot consonants
        for symbol, (x, y, manner, place, voicing, description) in IPA_CONSONANTS.items():
            color = self.consonant_colors[voicing]
            size = 300 if highlight_phonemes and symbol in highlight_phonemes else 200
            alpha = 1.0 if highlight_phonemes and symbol in highlight_phonemes else 0.7
            
            ax.scatter(x, y, s=size, c=color, alpha=alpha, edgecolors='black', linewidth=1)
            ax.annotate(symbol, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
        
        # Set up axes
        ax.set_xlim(0, 11)
        ax.set_ylim(-1, 7)
        ax.set_xlabel('Place of Articulation → Front to Back', fontsize=12)
        ax.set_ylabel('Manner of Articulation → More to Less Consonantal', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        # Add axis labels
        place_labels = ['', 'Bilabial', 'Labiodental', 'Dental', 'Alveolar', 
                       'Postalveolar', 'Retroflex', 'Palatal', 'Velar', 'Uvular', 'Glottal']
        ax.set_xticks(range(1, 11))
        ax.set_xticklabels(place_labels[1:], rotation=45, ha='right')
        
        manner_labels = ['', 'Trill', 'Approximant', 'Affricate', 'Fricative', 'Plosive', 'Nasal']
        ax.set_yticks(range(0, 7))
        ax.set_yticklabels(manner_labels)
        
        # Add legend
        legend_elements = [
            patches.Patch(color=self.consonant_colors['voiceless'], label='Voiceless'),
            patches.Patch(color=self.consonant_colors['voiced'], label='Voiced')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def plot_combined_chart(self,
                          highlight_vowels: Optional[List[str]] = None,
                          highlight_consonants: Optional[List[str]] = None,
                          show_grid: bool = True,
                          title: str = "IPA Combined Chart") -> plt.Figure:
        """
        Create a combined plot showing both vowels and consonants.
        
        Args:
            highlight_vowels: List of vowel symbols to highlight
            highlight_consonants: List of consonant symbols to highlight
            show_grid: Whether to show grid lines
            title: Plot title
            
        Returns:
            matplotlib Figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Plot vowels on left
        for symbol, (x, y, height, backness, roundedness, description) in IPA_VOWELS.items():
            color = self.vowel_colors[roundedness]
            size = 300 if highlight_vowels and symbol in highlight_vowels else 200
            alpha = 1.0 if highlight_vowels and symbol in highlight_vowels else 0.7
            
            ax1.scatter(x, y, s=size, c=color, alpha=alpha, edgecolors='black', linewidth=1)
            ax1.annotate(symbol, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
        
        ax1.set_xlim(0, 7)
        ax1.set_ylim(-2, 6)
        ax1.set_xlabel('Tongue Backness', fontsize=11)
        ax1.set_ylabel('Tongue Height', fontsize=11)
        ax1.set_title('Vowels', fontsize=13, fontweight='bold')
        ax1.set_xticks([1, 3, 5, 6])
        ax1.set_xticklabels(['Front', 'Central', 'Back', ''])
        ax1.set_yticks([-1, 0, 1, 2, 3, 4, 5])
        ax1.set_yticklabels(['Open', '', '', 'Mid', '', 'Near-close', 'Close'])
        ax1.grid(show_grid, alpha=0.3)
        
        # Plot consonants on right
        for symbol, (x, y, manner, place, voicing, description) in IPA_CONSONANTS.items():
            color = self.consonant_colors[voicing]
            size = 300 if highlight_consonants and symbol in highlight_consonants else 200
            alpha = 1.0 if highlight_consonants and symbol in highlight_consonants else 0.7
            
            ax2.scatter(x, y, s=size, c=color, alpha=alpha, edgecolors='black', linewidth=1)
            ax2.annotate(symbol, (x, y), fontsize=10, ha='center', va='center', fontweight='bold')
        
        ax2.set_xlim(0, 11)
        ax2.set_ylim(-1, 7)
        ax2.set_xlabel('Place of Articulation', fontsize=11)
        ax2.set_ylabel('Manner of Articulation', fontsize=11)
        ax2.set_title('Consonants', fontsize=13, fontweight='bold')
        ax2.set_xticks(range(1, 11))
        ax2.set_xticklabels(['Bilabial', 'Labiodental', 'Dental', 'Alveolar', 
                            'Postalveolar', 'Retroflex', 'Palatal', 'Velar', 'Uvular', 'Glottal'], 
                           rotation=45, ha='right')
        ax2.set_yticks(range(0, 7))
        ax2.set_yticklabels(['', 'Trill', 'Approximant', 'Affricate', 'Fricative', 'Plosive', 'Nasal'])
        ax2.grid(show_grid, alpha=0.3)
        
        # Add legends
        vowel_legend = [
            patches.Patch(color=self.vowel_colors['unrounded'], label='Unrounded'),
            patches.Patch(color=self.vowel_colors['rounded'], label='Rounded')
        ]
        consonant_legend = [
            patches.Patch(color=self.consonant_colors['voiceless'], label='Voiceless'),
            patches.Patch(color=self.consonant_colors['voiced'], label='Voiced')
        ]
        
        ax1.legend(handles=vowel_legend, loc='upper right')
        ax2.legend(handles=consonant_legend, loc='upper right')
        
        plt.suptitle(title, fontsize=15, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_similarity_network(self,
                              phonemes: List[str],
                              similarity_matrix: np.ndarray,
                              threshold: float = 0.5,
                              title: str = "Phoneme Similarity Network") -> plt.Figure:
        """
        Plot a network graph showing phoneme similarities.
        
        Args:
            phonemes: List of phoneme symbols
            similarity_matrix: Matrix of similarity values
            threshold: Minimum similarity to show connection
            title: Plot title
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create positions for phonemes based on their IPA coordinates
        positions = {}
        for i, phoneme in enumerate(phonemes):
            if phoneme in IPA_VOWELS:
                x, y, _, _, _, _ = IPA_VOWELS[phoneme]
                positions[phoneme] = (x, y)
            elif phoneme in IPA_CONSONANTS:
                x, y, _, _, _, _ = IPA_CONSONANTS[phoneme]
                positions[phoneme] = (x, y)
        
        # Plot edges (connections)
        for i in range(len(phonemes)):
            for j in range(i + 1, len(phonemes)):
                similarity = similarity_matrix[i, j]
                if similarity >= threshold:
                    phoneme1, phoneme2 = phonemes[i], phonemes[j]
                    if phoneme1 in positions and phoneme2 in positions:
                        x1, y1 = positions[phoneme1]
                        x2, y2 = positions[phoneme2]
                        ax.plot([x1, x2], [y1, y2], 'gray', alpha=similarity, linewidth=similarity * 3)
        
        # Plot nodes (phonemes)
        for phoneme, (x, y) in positions.items():
            ax.scatter(x, y, s=300, c='lightblue', edgecolors='black', linewidth=2)
            ax.annotate(phoneme, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('IPA Chart X Coordinate', fontsize=12)
        ax.set_ylabel('IPA Chart Y Coordinate', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
