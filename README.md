# Phonemescape 🗣️

A Python library for International Phonetic Alphabet (IPA) analysis with mouth shape similarity visualization and 2D plotting capabilities.

## Features

- **Complete IPA Data**: Comprehensive dataset of vowels and consonants with articulatory features
- **2D Visualization**: Beautiful plots of vowel and consonant charts based on standard IPA positions
- **Mouth Shape Similarity**: Calculate similarity between phonemes based on articulatory features and chart proximity
- **Similarity Networks**: Visualize phoneme relationships as network graphs
- **Phoneme Analysis**: Analyze words and find similar phonemes
- **Export Capabilities**: Export data in multiple formats

## Installation

```bash
pip install phonemescape
```

Or install from source:

```bash
git clone https://github.com/phonemescape/phonemescape.git
cd phonemescape
pip install -e .
```

## Quick Start

```python
import phonemescape as pm

# Initialize the library
ipa = pm.Phonemescape()

# Plot the vowel chart
fig = ipa.plot_vowel_chart()
fig.show()

# Plot the consonant chart
fig = ipa.plot_consonant_chart()
fig.show()

# Calculate similarity between phonemes
similarity = ipa.calculate_similarity('i', 'e')
print(f"Similarity between 'i' and 'e': {similarity:.3f}")

# Find similar phonemes
similar = ipa.find_similar_phonemes('i', top_k=5)
for phoneme, sim in similar:
    print(f"{phoneme}: {sim:.3f}")
```

## Examples

### Basic Phoneme Information

```python
import phonemescape as pm

ipa = pm.Phonemescape()

# Get information about a phoneme
info = ipa.get_phoneme_info('i')
print(info)
# {'symbol': 'i', 'type': 'vowel', 'coordinates': (1, 5), 
#  'height': 'close', 'backness': 'front', 'roundedness': 'unrounded',
#  'description': 'Close front unrounded vowel'}

# Check if a phoneme is a vowel or consonant
print(ipa.is_vowel('i'))      # True
print(ipa.is_consonant('p'))  # True
```

### Visualization

```python
import phonemescape as pm

ipa = pm.Phonemescape()

# Plot vowel chart with highlighted phonemes
fig = ipa.plot_vowel_chart(highlight=['i', 'e', 'a'])
fig.show()

# Plot consonant chart
fig = ipa.plot_consonant_chart()
fig.show()

# Combined chart
fig = ipa.plot_combined_chart(
    highlight_vowels=['i', 'u'],
    highlight_consonants=['p', 't', 'k']
)
fig.show()
```

### Similarity Analysis

```python
import phonemescape as pm
import numpy as np

ipa = pm.Phonemescape()

# Calculate similarity matrix for a set of phonemes
phonemes = ['i', 'e', 'a', 'u', 'o']
similarity_matrix = ipa.get_similarity_matrix(phonemes)
print(similarity_matrix)

# Find most similar phonemes to a target
similar = ipa.find_similar_phonemes('i', phoneme_type='vowel', top_k=10)
print("Phonemes similar to 'i':")
for phoneme, similarity in similar:
    print(f"  {phoneme}: {similarity:.3f}")

# Plot similarity network
fig = ipa.plot_similarity_network(['i', 'e', 'a', 'u', 'o'], threshold=0.3)
fig.show()
```

### Word Analysis

```python
import phonemescape as pm

ipa = pm.Phonemescape()

# Analyze a word (using IPA symbols)
analysis = ipa.analyze_word('kæt')  # "cat" in IPA
print(f"Word: {analysis['word']}")
print(f"Phonemes: {analysis['phonemes']}")
print(f"Vowels: {analysis['n_vowels']}, Consonants: {analysis['n_consonants']}")
print(f"Average similarity: {analysis['average_similarity']:.3f}")

# Get details for each phoneme
for detail in analysis['phoneme_details']:
    print(f"  {detail['symbol']}: {detail['description']}")
```

### Advanced Features

```python
import phonemescape as pm

ipa = pm.Phonemescape()

# Find phonemes by features
front_vowels = ipa.find_phonemes_by_features(backness='front')
print("Front vowels:", front_vowels)

bilabial_consonants = ipa.find_phonemes_by_features(place='bilabial')
print("Bilabial consonants:", bilabial_consonants)

# Cluster phonemes
phonemes = ['i', 'e', 'a', 'u', 'o', 'p', 't', 'k']
clusters = ipa.get_phoneme_clusters(phonemes, n_clusters=3)
for cluster_id, cluster_phonemes in clusters.items():
    print(f"Cluster {cluster_id}: {cluster_phonemes}")

# Export data
json_data = ipa.export_data(format='json')
print(json_data[:100] + "...")  # First 100 characters
```

## API Reference

### Core Classes

#### `Phonemescape`
Main interface for the library.

**Methods:**
- `get_all_phonemes()`: List all available phonemes
- `get_phoneme_info(phoneme)`: Get detailed phoneme information
- `calculate_similarity(phoneme1, phoneme2)`: Calculate similarity between phonemes
- `find_similar_phonemes(target, top_k=10)`: Find most similar phonemes
- `plot_vowel_chart(highlight=None)`: Create vowel chart visualization
- `plot_consonant_chart(highlight=None)`: Create consonant chart visualization
- `plot_combined_chart(...)`: Create combined chart
- `plot_similarity_network(phonemes, threshold=0.5)`: Plot similarity network
- `analyze_word(word)`: Analyze phonemes in a word
- `find_phonemes_by_features(**features)`: Find phonemes by articulatory features

#### `MouthShapeSimilarity`
Calculate mouth shape similarities.

**Methods:**
- `phoneme_similarity(phoneme1, phoneme2)`: Calculate similarity
- `similarity_matrix(phonemes)`: Calculate similarity matrix
- `most_similar_phonemes(target, top_k=5)`: Find most similar phonemes
- `mouth_shape_distance(phoneme1, phoneme2)`: Distance based on chart coordinates
- `articulatory_feature_distance(phoneme1, phoneme2)`: Distance based on features

#### `IPAPlotter`
Create visualizations of IPA charts.

**Methods:**
- `plot_vowel_chart(highlight_phonemes=None)`: Plot vowel chart
- `plot_consonant_chart(highlight_phonemes=None)`: Plot consonant chart
- `plot_combined_chart(...)`: Plot combined chart
- `plot_similarity_network(phonemes, similarity_matrix, threshold=0.5)`: Plot network

## Data Structure

### Vowels
Each vowel is stored with:
- Symbol (IPA character)
- X, Y coordinates (for 2D plotting)
- Height (close, near-close, close-mid, mid, open-mid, near-open, open)
- Backness (front, near-front, central, near-back, back)
- Roundedness (rounded, unrounded)
- Description

### Consonants
Each consonant is stored with:
- Symbol (IPA character)
- X, Y coordinates (for 2D plotting)
- Manner (nasal, plosive, fricative, affricate, approximant, trill)
- Place (bilabial, labiodental, dental, alveolar, postalveolar, retroflex, palatal, velar, uvular, glottal)
- Voicing (voiced, voiceless)
- Description

## Similarity Calculation

The similarity between phonemes is calculated using a combination of:

1. **Articulatory Feature Similarity**: Based on phonetic features (height, backness, place, manner, etc.)
2. **Chart Proximity**: Euclidean distance on the IPA chart
3. **Cosine Similarity**: Between feature vectors

The final similarity score is a weighted average that ranges from 0 (completely different) to 1 (identical).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/phonemescape/phonemescape.git
cd phonemescape
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black phonemescape/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- International Phonetic Association for the IPA chart standards
- The linguistic community for phonetic research and documentation
- Contributors who help improve this library

## Citation

If you use this library in your research, please cite:

```bibtex
@software{phonemescape,
  title={Phonemescape: International Phonetic Alphabet Library},
  author={Phonemescape Team},
  year={2024},
  url={https://github.com/phonemescape/phonemescape}
}
```
