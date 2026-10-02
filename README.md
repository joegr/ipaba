# Phonemescape 🗣️

A Python library for the International Phonetic Alphabet: tokenizing
transcriptions, distinctive features and natural classes, articulatory
similarity, IPA chart plots, and a **local Neo4j graph of phoneme samples**.

## Features

- **The full IPA chart (2020 revision)**: all 28 vowels, 59 pulmonic consonants,
  10 "other symbols" (w ʍ ɥ ʜ ʢ ʡ ɕ ʑ ɺ ɧ), 10 non-pulmonic consonants (clicks and
  implosives), every diacritic, suprasegmental and tone mark
- **Real IPA tokenization**: `tʰ`, `ã`, `t͡ʃ`, `n̩`, `kʷʼ`, `uː`, `ⁿd`, stress, tone
  letters, syllable breaks, `/phonemic/` and `[phonetic]` delimiters, plus aliases
  for common look-alikes (`g`→`ɡ`, `ʧ`→`t͡ʃ`, `:`→`ː`, `ɚ`, `ɫ` …)
- **Distinctive features**: 28 binary features (Hayes 2009 + [velaric], [long]),
  derived by rule from each symbol's chart description, in ONE space shared by
  vowels and consonants
- **Articulatory similarity**: feature-based, refined by chart proximity
- **Natural-class queries**: `natural_class(sonorant='-', continuant='+')`
- **Chart plots** in the official orientation and geometry
- **Neo4j sample graph (local only)**: every sample linked to its segments,
  features, language and to phonetically similar samples

## Installation

```bash
git clone https://github.com/joegr/ipaba.git
cd ipaba
pip install -e .            # core
pip install -e ".[graph]"   # + Neo4j driver for the sample graph
```

## Quick Start

```python
import phonemescape as pm

ipa = pm.Phonemescape()

ipa.calculate_similarity('p', 'b')      # 0.962 – differ only in [voice]
ipa.differing_features('i', 'j')        # {'syllabic': ('+', '-'), 'tense': ('+', '0')}
ipa.find_similar_phonemes('i', top_k=4) # y, ɪ, ɨ, e

ipa.get_phoneme_info('tʰ')['description']   # 'Voiceless alveolar plosive, aspirated'
ipa.natural_class(strident='+')             # ['s', 'z', 'ʃ', 'ʒ', 'ʂ', 'ʐ', 'ɕ', 'ʑ', 'ɧ']

fig = ipa.plot_vowel_chart(highlight=['i', 'e', 'ɛ', 'a', 'ɑ', 'ɔ', 'o', 'u'])
```

## A note on terminology

IPA symbols denote **phones** (speech sounds). A **phoneme** is a contrastive
unit of one particular language, written between slashes (/t/), while a phone
is written in square brackets ([tʰ]). Phonemescape works with the
language-independent IPA segments. The API keeps the name "phoneme" for
backwards compatibility.

## Examples

### Segment information

```python
info = ipa.get_phoneme_info('i')
# {'symbol': 'i', 'type': 'vowel', 'coordinates': (-0.08, 0.0),
#  'height': 'close', 'backness': 'front', 'roundedness': 'unrounded',
#  'description': 'Close front unrounded vowel', 'base': 'i',
#  'modifiers': [], 'tones': [], 'features': {'syllabic': '+', ...}}

ipa.get_phoneme_info('t͡s')['description']   # 'Voiceless alveolar sibilant affricate'
ipa.get_phoneme_info('ŋ̊')['description']    # 'Voiceless velar nasal'
ipa.get_phoneme_info('kʼ')['airstream']      # 'glottalic egressive'
ipa.is_vowel('aː'), ipa.is_consonant('p')    # (True, True)
```

### Tokenizing and analysing transcriptions

```python
[t.text for t in ipa.tokenize('/ˈhjuːmən/')]
# ['ˈ', 'h', 'j', 'uː', 'm', 'ə', 'n']

analysis = ipa.analyze_word('[kʰæt]')
analysis['phonemes']          # ['kʰ', 'æ', 't']
analysis['n_vowels'], analysis['n_consonants']    # (1, 2)
analysis['suprasegmentals']   # stress, tone, breaks found in the input
analysis['invalid_phonemes']  # characters that are not IPA

ipa.sample_similarity('kæt', 'bæt')   # phonetic alignment similarity, 0..1
```

### Visualization

```python
ipa.plot_vowel_chart(highlight=['i', 'u'])
ipa.plot_consonant_chart(highlight=['p', 't', 'k'])
ipa.plot_combined_chart(highlight_vowels=['i', 'u'], highlight_consonants=['p', 't', 'k'])

# Vowels and consonants are drawn on separate planes; cross-plane edges are dashed
ipa.plot_similarity_network(['i', 'u', 'j', 'w', 'p', 't'], threshold=0.68)
```

### Feature queries and clustering

```python
ipa.find_phonemes_by_features(backness='front')            # vowels only
ipa.find_phonemes_by_features(manner='plosive', voicing='voiceless')
ipa.find_phonemes_by_features(place='velar', nasal='+')    # mix chart attributes and features
ipa.natural_class(syllabic='-', consonantal='-', sonorant='+')   # glides: ʋ j ɰ w ɥ

ipa.get_phoneme_clusters(['i', 'e', 'u', 'o', 'p', 't', 'k'], n_clusters=2)
# {0: ['i', 'e', 'u', 'o'], 1: ['p', 't', 'k']}

ipa.export_data(format='csv')   # every symbol with its chart attributes and features
```

### Command line

```bash
phonemescape info tʰ
phonemescape compare s ʃ
phonemescape similar ɛ -k 5 -t vowel
phonemescape analyze "/ˈhjuːmən/"
phonemescape class sonorant=- continuant=+ voice=+
```

## Neo4j sample graph (local only)

Every sample you add becomes part of one connected graph:

```
(:Sample)-[:HAS_SEGMENT {index}]->(:Segment)     ordered realisation
(:Sample)-[:IN_LANGUAGE]->(:Language)
(:Sample)-[:SIMILAR_TO {score}]-(:Sample)        phonetic alignment ≥ sample_threshold
(:Segment)-[:HAS_FEATURE]->(:Feature {id:'+voice'})
(:Segment)-[:VARIANT_OF]->(:Segment)             tʰ → t, ã → a, t͡ʃ → t, ʃ
(:Segment)-[:SIMILAR_TO {score}]-(:Segment)      ≥ segment_threshold
```

The connection is **restricted to loopback hosts** (`localhost`, `127.0.0.1`,
`::1`). Any other URI is refused before a connection is attempted. The bundled
`docker-compose.yml` binds Neo4j's ports to `127.0.0.1` only.

```bash
docker compose up -d              # Neo4j 5 community; browser at http://localhost:7474
phonemescape graph init           # constraints + all IPA chart segments
phonemescape graph add "/kæt/" --language en --gloss cat
phonemescape graph stats
```

```python
ipa = pm.Phonemescape()
graph = ipa.connect_graph()                    # bolt://localhost:7687
sid = ipa.add_sample('[kʰæt]', language='en', gloss='cat')
graph.similar_samples(sid)                     # e.g. /kæt/ 0.989, /bæt/ 0.899
graph.samples_with_segment('k')                # also finds kʰ via VARIANT_OF
graph.samples_in_natural_class(nasal='+')
graph.segment_frequencies(language='en')
```

Settings come from `NEO4J_URI` (default `bolt://localhost:7687`), `NEO4J_USER`
(`neo4j`), `NEO4J_PASSWORD` (`phonemescape-local`, same as the compose file) and
`NEO4J_DATABASE` (`neo4j`). See `examples/graph_samples.py`.

## Phonological model

### Chart geometry

Vowels and consonants live on **separate planes**, both drawn in the chart's
orientation (close vowels and plosives at the top).

- **Vowel trapezoid**: y = height (0 close … 3 open, seven equidistant rows);
  the back edge is vertical at x = 2; the front edge slopes from x = 0 (close)
  to x = 1 (open), so the open row is half as wide as the close row, as on the
  official chart. Central, near-front and near-back positions are interpolated
  proportionally at each height, so the central line slopes too. In each
  rounding pair the unrounded vowel sits left of the dot and the rounded one
  right.
- **Consonant grid**: x = place (bilabial 0 … glottal 10), y = manner (plosive 0
  … lateral approximant 7); voiceless symbols sit left in a cell, voiced right.
  Other symbols and non-pulmonic consonants get positions between or below the
  pulmonic cells.

### Distinctive features

`syllabic consonantal sonorant continuant delayed_release approximant tap
trill nasal lateral strident voice spread_glottis constricted_glottis labial
round labiodental coronal anterior distributed dorsal high low front back
tense long velaric`, each valued `+`, `-` or `0` (unspecified).

Features are derived **by rule** from height/backness/rounding and
manner/place/voicing, with articulator-based feature geometry: dependents of an
absent articulator are 0. Palatals are dorsal [+high, +front]. Laryngeals
(h ɦ ʔ) are [-consonantal]. Glides are [-consonantal] and liquids
[+consonantal]. Diacritics modify the bundle: `̥` [-voice], `ʰ` [+spread
glottis], `ʼ` [+constricted glottis], `̃` [+nasal], `̩` [+syllabic], `ʷ`
[+labial, +round], `ʲ` [+high, +front], `ˠ` velarized, `ˤ` pharyngealized, `˞`
rhotacized, `ː` [+long], raised approximants become fricatives, lowered
fricatives become approximants, and so on. Tie bars build affricates (stop +
fricative → [-continuant, +delayed release]), double articulations (`k͡p`:
articulators merged) and diphthongs.

Because vowels and consonants share one feature space, natural classes cross
the vowel/consonant divide: `i`~`j`, `u`~`w`, `y`~`ɥ` and `ɯ`~`ɰ` differ only
in [syllabic]. The binary system cannot separate pharyngeals from epiglottals
(`ħ`/`ʜ`, `ʕ`/`ʢ`), so only their chart positions tell them apart.

### Similarity

```
feature_sim = 1 − Σ wᵢ·|aᵢ − bᵢ|/2  /  Σ wᵢ      (over features specified in a or b)
chart_sim   = 1 − distance / plane diameter       (0 between a vowel and a consonant)
similarity  = 0.75 · feature_sim + 0.25 · chart_sim
```

A +/− mismatch costs 1 and a specified/unspecified mismatch costs 0.5.
Per-feature weights and the 0.75 mix are configurable on
`MouthShapeSimilarity`. Sample similarity is a weighted edit distance:
substituting a for b costs 1 − similarity(a, b), and an insertion or deletion
costs 1, normalised by the length of the longer sample.

## API Reference

#### `Phonemescape`
- `get_all_phonemes()`, `get_vowels()`, `get_consonants()`, `is_vowel(p)`, `is_consonant(p)`
- `get_phoneme_info(p)`, `get_distinctive_features(p)`, `differing_features(a, b)`
- `calculate_similarity(a, b)`, `get_similarity_matrix(ps)`, `find_similar_phonemes(p, phoneme_type, top_k)`
- `tokenize(text)`, `analyze_word(text)`, `sample_similarity(t1, t2)`
- `find_phonemes_by_features(**criteria)`, `natural_class(**features)`, `get_phoneme_clusters(ps, n)`
- `plot_vowel_chart`, `plot_consonant_chart`, `plot_combined_chart`, `plot_similarity_network`
- `export_data(format='dict'|'json'|'csv')`
- `connect_graph(**kwargs)`, `add_sample(transcription, **kwargs)`

#### `MouthShapeSimilarity`
- `phoneme_similarity`, `feature_similarity`, `chart_similarity`, `similarity_matrix`
- `most_similar_phonemes`, `mouth_shape_distance` (chart; ∞ across planes),
  `articulatory_feature_distance` (features; defined for every pair)
- `sequence_distance`, `sequence_similarity`, `cluster_phonemes`

#### `IPAPlotter`
- `plot_vowel_chart`, `plot_consonant_chart`, `plot_combined_chart`, `plot_similarity_network`
- `setup_vowel_axes(ax)`, `setup_consonant_axes(ax)`, `draw_network(ax, ...)` for custom figures

#### `PhonemeGraph` (`phonemescape.graph`)
- `setup_schema`, `load_inventory`, `add_sample`, `add_samples`, `relink_samples`
- `get_sample`, `similar_samples`, `samples_with_segment`, `samples_in_natural_class`
- `segment_frequencies`, `stats`, `delete_sample`, `delete_all`

#### Module functions
- `pm.tokenize(text)`, `pm.segments(text)`, `pm.get_segment(symbol)` → `Segment`
  (symbol, kind, base, parts, modifiers, tones, features, position, coordinates, description)

## Development

```bash
pip install -e ".[dev,graph]"
pytest                    # graph tests run when a local Neo4j is up, else skip
black phonemescape/
```

## License

This project is licensed under the MIT License.

## Acknowledgments

- International Phonetic Association: *The International Phonetic Alphabet* (revised to 2020)
- Hayes, B. (2009). *Introductory Phonology*. Wiley-Blackwell (feature system)
- Mortensen, D. et al. (2016). PanPhon: a resource for mapping IPA segments to articulatory feature vectors. *COLING*
- Chomsky, N. & Halle, M. (1968). *The Sound Pattern of English*

## Citation

```bibtex
@software{phonemescape,
  title={Phonemescape: International Phonetic Alphabet Library},
  author={Phonemescape Team},
  year={2026},
  url={https://github.com/joegr/ipaba}
}
```
