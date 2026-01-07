#!/usr/bin/env python3
"""
Basic usage examples for Phonemescape IPA library.
"""

import phonemescape as pm
import matplotlib.pyplot as plt

def main():
    """Demonstrate basic Phonemescape functionality."""
    
    print("=== Phonemescape Basic Usage Examples ===\n")
    
    # Initialize the library
    ipa = pm.Phonemescape()
    print("✓ Phonemescape library initialized")
    
    # Example 1: Basic phoneme information
    print("\n1. Phoneme Information:")
    print("-" * 30)
    
    # Get info about a vowel
    vowel_info = ipa.get_phoneme_info('i')
    print(f"Vowel 'i': {vowel_info['description']}")
    print(f"  Type: {vowel_info['type']}")
    print(f"  Height: {vowel_info['height']}")
    print(f"  Backness: {vowel_info['backness']}")
    print(f"  Roundedness: {vowel_info['roundedness']}")
    print(f"  Coordinates: {vowel_info['coordinates']}")
    
    # Get info about a consonant
    consonant_info = ipa.get_phoneme_info('p')
    print(f"\nConsonant 'p': {consonant_info['description']}")
    print(f"  Type: {consonant_info['type']}")
    print(f"  Manner: {consonant_info['manner']}")
    print(f"  Place: {consonant_info['place']}")
    print(f"  Voicing: {consonant_info['voicing']}")
    print(f"  Coordinates: {consonant_info['coordinates']}")
    
    # Example 2: Similarity calculations
    print("\n2. Similarity Calculations:")
    print("-" * 30)
    
    # Calculate similarity between vowels
    vowel_pairs = [('i', 'e'), ('i', 'a'), ('i', 'u'), ('a', 'ɑ')]
    for p1, p2 in vowel_pairs:
        similarity = ipa.calculate_similarity(p1, p2)
        print(f"Similarity '{p1}' - '{p2}': {similarity:.3f}")
    
    # Calculate similarity between consonants
    consonant_pairs = [('p', 'b'), ('p', 't'), ('p', 'k'), ('s', 'ʃ')]
    for p1, p2 in consonant_pairs:
        similarity = ipa.calculate_similarity(p1, p2)
        print(f"Similarity '{p1}' - '{p2}': {similarity:.3f}")
    
    # Example 3: Find similar phonemes
    print("\n3. Finding Similar Phonemes:")
    print("-" * 30)
    
    # Find vowels similar to 'i'
    similar_vowels = ipa.find_similar_phonemes('i', phoneme_type='vowel', top_k=5)
    print(f"Vowels similar to 'i':")
    for phoneme, similarity in similar_vowels:
        print(f"  {phoneme}: {similarity:.3f}")
    
    # Find consonants similar to 'p'
    similar_consonants = ipa.find_similar_phonemes('p', phoneme_type='consonant', top_k=5)
    print(f"\nConsonants similar to 'p':")
    for phoneme, similarity in similar_consonants:
        print(f"  {phoneme}: {similarity:.3f}")
    
    # Example 4: Word analysis
    print("\n4. Word Analysis:")
    print("-" * 30)
    
    # Analyze some English words in IPA
    words = ['kæt', 'dɔg', 'hʊmən', 'bɪrd']
    
    for word in words:
        analysis = ipa.analyze_word(word)
        print(f"Word '{word}':")
        print(f"  Phonemes: {analysis['phonemes']}")
        print(f"  Vowels: {analysis['n_vowels']}, Consonants: {analysis['n_consonants']}")
        print(f"  Average similarity: {analysis['average_similarity']:.3f}")
    
    # Example 5: Find phonemes by features
    print("\n5. Finding Phonemes by Features:")
    print("-" * 30)
    
    # Find all front vowels
    front_vowels = ipa.find_phonemes_by_features(backness='front')
    print(f"Front vowels: {front_vowels}")
    
    # Find all bilabial consonants
    bilabial_consonants = ipa.find_phonemes_by_features(place='bilabial')
    print(f"Bilabial consonants: {bilabial_consonants}")
    
    # Find all voiceless plosives
    voiceless_plosives = ipa.find_phonemes_by_features(manner='plosive', voicing='voiceless')
    print(f"Voiceless plosives: {voiceless_plosives}")
    
    # Example 6: Similarity matrix
    print("\n6. Similarity Matrix:")
    print("-" * 30)
    
    # Create similarity matrix for a subset of phonemes
    phonemes = ['i', 'e', 'a', 'u', 'o']
    similarity_matrix = ipa.get_similarity_matrix(phonemes)
    
    print("Similarity matrix for ['i', 'e', 'a', 'u', 'o']:")
    print("     " + "  ".join(f"{p:>3}" for p in phonemes))
    for i, p1 in enumerate(phonemes):
        print(f"{p1:>3} " + "  ".join(f"{similarity_matrix[i,j]:>3.2f}" for j in range(len(phonemes))))
    
    # Example 7: Clustering
    print("\n7. Phoneme Clustering:")
    print("-" * 30)
    
    # Cluster some phonemes
    test_phonemes = ['i', 'e', 'a', 'u', 'o', 'p', 't', 'k', 'm', 'n']
    clusters = ipa.get_phoneme_clusters(test_phonemes, n_clusters=3)
    
    for cluster_id, cluster_phonemes in clusters.items():
        print(f"Cluster {cluster_id}: {cluster_phonemes}")
    
    print("\n=== Examples Complete ===")
    print("Run the plotting examples to see visualizations!")

if __name__ == "__main__":
    main()