#!/usr/bin/env python3
"""
Plotting examples for Phonemescape IPA library.
"""

import phonemescape as pm
import matplotlib.pyplot as plt
import numpy as np

def main():
    """Demonstrate Phonemescape plotting functionality."""
    
    print("=== Phonemescape Plotting Examples ===\n")
    
    # Initialize the library
    ipa = pm.Phonemescape()
    print("✓ Phonemescape library initialized")
    
    # Example 1: Basic vowel chart
    print("1. Creating basic vowel chart...")
    fig1 = ipa.plot_vowel_chart(title="IPA Vowel Chart")
    plt.savefig('vowel_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Saved vowel_chart.png")
    
    # Example 2: Basic consonant chart
    print("\n2. Creating basic consonant chart...")
    fig2 = ipa.plot_consonant_chart(title="IPA Consonant Chart")
    plt.savefig('consonant_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Saved consonant_chart.png")
    
    # Example 3: Highlighted vowel chart
    print("\n3. Creating highlighted vowel chart...")
    highlight_vowels = ['i', 'e', 'a', 'u', 'o']  # Cardinal vowels
    fig3 = ipa.plot_vowel_chart(
        highlight=highlight_vowels,
        title="IPA Vowel Chart - Cardinal Vowels Highlighted"
    )
    plt.savefig('vowel_chart_highlighted.png', dpi=150, bbox_inches='tight')
    print("✓ Saved vowel_chart_highlighted.png")
    
    # Example 4: Highlighted consonant chart
    print("\n4. Creating highlighted consonant chart...")
    highlight_consonants = ['p', 't', 'k', 'b', 'd', 'g']  # Plosives
    fig4 = ipa.plot_consonant_chart(
        highlight=highlight_consonants,
        title="IPA Consonant Chart - Plosives Highlighted"
    )
    plt.savefig('consonant_chart_highlighted.png', dpi=150, bbox_inches='tight')
    print("✓ Saved consonant_chart_highlighted.png")
    
    # Example 5: Combined chart
    print("\n5. Creating combined chart...")
    fig5 = ipa.plot_combined_chart(
        highlight_vowels=['i', 'e', 'a', 'u', 'o'],
        highlight_consonants=['p', 't', 'k', 'b', 'd', 'g'],
        title="IPA Combined Chart - Cardinal Vowels and Plosives"
    )
    plt.savefig('combined_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Saved combined_chart.png")
    
    # Example 6: Similarity network for vowels
    print("\n6. Creating vowel similarity network...")
    vowel_phonemes = ['i', 'e', 'ɛ', 'a', 'ɑ', 'ɒ', 'o', 'ɔ', 'u', 'ʊ']
    fig6 = ipa.plot_similarity_network(
        vowel_phonemes, 
        threshold=0.3,
        title="Vowel Similarity Network"
    )
    plt.savefig('vowel_similarity_network.png', dpi=150, bbox_inches='tight')
    print("✓ Saved vowel_similarity_network.png")
    
    # Example 7: Similarity network for consonants
    print("\n7. Creating consonant similarity network...")
    consonant_phonemes = ['p', 'b', 't', 'd', 'k', 'g', 'f', 'v', 's', 'z', 'ʃ', 'ʒ']
    fig7 = ipa.plot_similarity_network(
        consonant_phonemes,
        threshold=0.2,
        title="Consonant Similarity Network"
    )
    plt.savefig('consonant_similarity_network.png', dpi=150, bbox_inches='tight')
    print("✓ Saved consonant_similarity_network.png")
    
    # Example 8: Mixed similarity network
    print("\n8. Creating mixed phoneme similarity network...")
    mixed_phonemes = ['i', 'a', 'u', 'p', 't', 'k', 'm', 'n', 's', 'l']
    fig8 = ipa.plot_similarity_network(
        mixed_phonemes,
        threshold=0.15,
        title="Mixed Phoneme Similarity Network"
    )
    plt.savefig('mixed_similarity_network.png', dpi=150, bbox_inches='tight')
    print("✓ Saved mixed_similarity_network.png")
    
    # Example 9: Progressive vowel similarity visualization
    print("\n9. Creating progressive vowel similarity visualization...")
    fig9, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig9.suptitle('Progressive Vowel Similarity Networks', fontsize=16, fontweight='bold')
    
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    vowel_subset = ['i', 'e', 'ɛ', 'a', 'ɑ', 'o', 'ɔ', 'u']
    
    for idx, threshold in enumerate(thresholds):
        ax = axes[idx // 3, idx % 3]
        
        # Create similarity matrix
        similarity_matrix = ipa.get_similarity_matrix(vowel_subset)
        
        # Plot network
        positions = {}
        for phoneme in vowel_subset:
            if phoneme in ipa.vowels:
                x, y, _, _, _, _ = ipa.vowels[phoneme]
                positions[phoneme] = (x, y)
        
        # Plot edges
        for i in range(len(vowel_subset)):
            for j in range(i + 1, len(vowel_subset)):
                similarity = similarity_matrix[i, j]
                if similarity >= threshold:
                    phoneme1, phoneme2 = vowel_subset[i], vowel_subset[j]
                    if phoneme1 in positions and phoneme2 in positions:
                        x1, y1 = positions[phoneme1]
                        x2, y2 = positions[phoneme2]
                        ax.plot([x1, x2], [y1, y2], 'gray', alpha=similarity, linewidth=similarity * 2)
        
        # Plot nodes
        for phoneme, (x, y) in positions.items():
            ax.scatter(x, y, s=200, c='lightblue', edgecolors='black', linewidth=1)
            ax.annotate(phoneme, (x, y), fontsize=10, ha='center', va='center', fontweight='bold')
        
        ax.set_title(f'Threshold ≥ {threshold}', fontsize=12)
        ax.set_xlim(0, 7)
        ax.set_ylim(-2, 6)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('progressive_vowel_networks.png', dpi=150, bbox_inches='tight')
    print("✓ Saved progressive_vowel_networks.png")
    
    # Example 10: Feature-based visualization
    print("\n10. Creating feature-based visualization...")
    fig10, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig10.suptitle('IPA Phonemes by Articulatory Features', fontsize=16, fontweight='bold')
    
    # Plot 1: Front vowels
    ax1 = axes[0, 0]
    front_vowels = ipa.find_phonemes_by_features(backness='front')
    # Filter to only include actual vowels
    front_vowels = [v for v in front_vowels if ipa.is_vowel(v)]
    for phoneme in front_vowels:
        x, y, _, _, _, _ = ipa.vowels[phoneme]
        ax1.scatter(x, y, s=300, c='red', alpha=0.7, edgecolors='black')
        ax1.annotate(phoneme, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
    ax1.set_title('Front Vowels', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 7)
    ax1.set_ylim(-2, 6)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Back vowels
    ax2 = axes[0, 1]
    back_vowels = ipa.find_phonemes_by_features(backness='back')
    # Filter to only include actual vowels
    back_vowels = [v for v in back_vowels if ipa.is_vowel(v)]
    for phoneme in back_vowels:
        x, y, _, _, _, _ = ipa.vowels[phoneme]
        ax2.scatter(x, y, s=300, c='blue', alpha=0.7, edgecolors='black')
        ax2.annotate(phoneme, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
    ax2.set_title('Back Vowels', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 7)
    ax2.set_ylim(-2, 6)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Bilabial consonants
    ax3 = axes[1, 0]
    bilabial_consonants = ipa.find_phonemes_by_features(place='bilabial')
    # Filter to only include actual consonants
    bilabial_consonants = [c for c in bilabial_consonants if ipa.is_consonant(c)]
    for phoneme in bilabial_consonants:
        x, y, _, _, _, _ = ipa.consonants[phoneme]
        ax3.scatter(x, y, s=300, c='green', alpha=0.7, edgecolors='black')
        ax3.annotate(phoneme, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
    ax3.set_title('Bilabial Consonants', fontsize=14, fontweight='bold')
    ax3.set_xlim(0, 11)
    ax3.set_ylim(-1, 7)
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Velar consonants
    ax4 = axes[1, 1]
    velar_consonants = ipa.find_phonemes_by_features(place='velar')
    # Filter to only include actual consonants
    velar_consonants = [c for c in velar_consonants if ipa.is_consonant(c)]
    for phoneme in velar_consonants:
        x, y, _, _, _, _ = ipa.consonants[phoneme]
        ax4.scatter(x, y, s=300, c='purple', alpha=0.7, edgecolors='black')
        ax4.annotate(phoneme, (x, y), fontsize=12, ha='center', va='center', fontweight='bold')
    ax4.set_title('Velar Consonants', fontsize=14, fontweight='bold')
    ax4.set_xlim(0, 11)
    ax4.set_ylim(-1, 7)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('feature_based_visualization.png', dpi=150, bbox_inches='tight')
    print("✓ Saved feature_based_visualization.png")
    
    # Clean up all figures
    plt.close('all')
    
    print("\n=== All Plotting Examples Complete ===")
    print("Generated files:")
    print("  - vowel_chart.png")
    print("  - consonant_chart.png") 
    print("  - vowel_chart_highlighted.png")
    print("  - consonant_chart_highlighted.png")
    print("  - combined_chart.png")
    print("  - vowel_similarity_network.png")
    print("  - consonant_similarity_network.png")
    print("  - mixed_similarity_network.png")
    print("  - progressive_vowel_networks.png")
    print("  - feature_based_visualization.png")

if __name__ == "__main__":
    main()