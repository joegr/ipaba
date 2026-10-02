#!/usr/bin/env python3
"""
Plotting examples for Phonemescape IPA library.
"""

import matplotlib.pyplot as plt

import phonemescape as pm
from phonemescape.segments import get_segment

# Primary cardinal vowels (Daniel Jones): 1-8
CARDINAL_VOWELS = ['i', 'e', 'ɛ', 'a', 'ɑ', 'ɔ', 'o', 'u']


def main():
    """Demonstrate Phonemescape plotting functionality."""

    print("=== Phonemescape Plotting Examples ===\n")

    ipa = pm.Phonemescape()
    plotter = ipa.plotter
    print("✓ Phonemescape library initialized")

    # Example 1: Basic vowel chart
    print("1. Creating basic vowel chart...")
    ipa.plot_vowel_chart(title="IPA Vowel Chart")
    plt.savefig('vowel_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Saved vowel_chart.png")

    # Example 2: Basic consonant chart
    print("\n2. Creating basic consonant chart...")
    ipa.plot_consonant_chart(title="IPA Consonant Chart (Pulmonic)")
    plt.savefig('consonant_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Saved consonant_chart.png")

    # Example 3: Highlighted vowel chart
    print("\n3. Creating highlighted vowel chart...")
    ipa.plot_vowel_chart(highlight=CARDINAL_VOWELS,
                         title="IPA Vowel Chart - Primary Cardinal Vowels Highlighted")
    plt.savefig('vowel_chart_highlighted.png', dpi=150, bbox_inches='tight')
    print("✓ Saved vowel_chart_highlighted.png")

    # Example 4: Highlighted consonant chart
    print("\n4. Creating highlighted consonant chart...")
    plosives = ipa.find_phonemes_by_features(manner='plosive', category='pulmonic')
    ipa.plot_consonant_chart(highlight=plosives,
                             title="IPA Consonant Chart - Plosives Highlighted")
    plt.savefig('consonant_chart_highlighted.png', dpi=150, bbox_inches='tight')
    print("✓ Saved consonant_chart_highlighted.png")

    # Example 5: Combined chart
    print("\n5. Creating combined chart...")
    ipa.plot_combined_chart(highlight_vowels=CARDINAL_VOWELS,
                            highlight_consonants=plosives,
                            title="IPA Combined Chart - Cardinal Vowels and Plosives")
    plt.savefig('combined_chart.png', dpi=150, bbox_inches='tight')
    print("✓ Saved combined_chart.png")

    # Example 6: Similarity network for vowels
    print("\n6. Creating vowel similarity network...")
    vowel_phonemes = ['i', 'e', 'ɛ', 'a', 'ɑ', 'ɒ', 'o', 'ɔ', 'u', 'ʊ']
    ipa.plot_similarity_network(vowel_phonemes, threshold=0.8,
                                title="Vowel Similarity Network")
    plt.savefig('vowel_similarity_network.png', dpi=150, bbox_inches='tight')
    print("✓ Saved vowel_similarity_network.png")

    # Example 7: Similarity network for consonants
    print("\n7. Creating consonant similarity network...")
    consonant_phonemes = ['p', 'b', 't', 'd', 'k', 'ɡ', 'f', 'v', 's', 'z', 'ʃ', 'ʒ']
    ipa.plot_similarity_network(consonant_phonemes, threshold=0.85,
                                title="Consonant Similarity Network")
    plt.savefig('consonant_similarity_network.png', dpi=150, bbox_inches='tight')
    print("✓ Saved consonant_similarity_network.png")

    # Example 8: Mixed network - vowels and consonants on separate planes,
    # cross-plane (feature-based) edges dashed: i~j, u~w are near-identical.
    print("\n8. Creating mixed phoneme similarity network...")
    mixed_phonemes = ['i', 'a', 'u', 'j', 'w', 'p', 't', 'k', 'm', 'n', 's', 'l']
    ipa.plot_similarity_network(mixed_phonemes, threshold=0.68,
                                title="Mixed Phoneme Similarity Network")
    plt.savefig('mixed_similarity_network.png', dpi=150, bbox_inches='tight')
    print("✓ Saved mixed_similarity_network.png")

    # Example 9: Progressive vowel similarity visualization
    print("\n9. Creating progressive vowel similarity visualization...")
    fig9, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig9.suptitle('Progressive Vowel Similarity Networks', fontsize=16, fontweight='bold')
    segs = [get_segment(v) for v in CARDINAL_VOWELS]
    matrix = ipa.get_similarity_matrix(CARDINAL_VOWELS)
    for ax, threshold in zip(axes.flat, [0.6, 0.65, 0.7, 0.75, 0.8, 0.85]):
        plotter.setup_vowel_axes(ax)
        plotter.draw_network(ax, segs, matrix, threshold, list(range(len(segs))))
        ax.set_title(f'Threshold ≥ {threshold}', fontsize=12)
    fig9.tight_layout()
    plt.savefig('progressive_vowel_networks.png', dpi=150, bbox_inches='tight')
    print("✓ Saved progressive_vowel_networks.png")

    # Example 10: Feature-based visualization
    print("\n10. Creating feature-based visualization...")
    fig10, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig10.suptitle('IPA Segments by Articulatory Features', fontsize=16, fontweight='bold')
    panels = [
        ('Front vowels', 'red', dict(backness='front')),
        ('Back vowels', 'blue', dict(backness='back')),
        ('Labial consonants [+labial, +consonantal]', 'green',
         dict(labial='+', consonantal='+', category='pulmonic')),
        ('Dorsal consonants [+dorsal, +consonantal]', 'purple',
         dict(dorsal='+', consonantal='+', category='pulmonic')),
    ]
    for ax, (title, color, criteria) in zip(axes.flat, panels):
        symbols = ipa.find_phonemes_by_features(**criteria)
        is_vowel_panel = 'backness' in criteria
        if is_vowel_panel:
            plotter.setup_vowel_axes(ax)
        else:
            plotter.setup_consonant_axes(ax, short_labels=True)
        for symbol in symbols:
            x, y = get_segment(symbol).coordinates
            ax.scatter(x, y, s=300, c=color, alpha=0.7, edgecolors='black', zorder=5)
            ax.annotate(symbol, (x, y), fontsize=12, ha='center', va='center',
                        fontweight='bold', zorder=6)
        ax.set_title(title, fontsize=14, fontweight='bold')
    fig10.tight_layout()
    plt.savefig('feature_based_visualization.png', dpi=150, bbox_inches='tight')
    print("✓ Saved feature_based_visualization.png")

    plt.close('all')

    print("\n=== All Plotting Examples Complete ===")
    print("Generated files:")
    for name in ['vowel_chart', 'consonant_chart', 'vowel_chart_highlighted',
                 'consonant_chart_highlighted', 'combined_chart', 'vowel_similarity_network',
                 'consonant_similarity_network', 'mixed_similarity_network',
                 'progressive_vowel_networks', 'feature_based_visualization']:
        print(f"  - {name}.png")


if __name__ == "__main__":
    main()
