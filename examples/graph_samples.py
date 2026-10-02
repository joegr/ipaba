#!/usr/bin/env python3
"""
Store phoneme samples in a LOCAL Neo4j graph.

    docker compose up -d          # starts Neo4j on 127.0.0.1 only
    python examples/graph_samples.py

Then explore at http://localhost:7474, e.g.
    MATCH (s:Sample)-[r:SIMILAR_TO]-(o:Sample) RETURN s, r, o
"""

import phonemescape as pm

SAMPLES = [
    {'transcription': '/kæt/', 'language': 'en', 'gloss': 'cat'},
    {'transcription': '[kʰæt]', 'language': 'en', 'gloss': 'cat (narrow)'},
    {'transcription': '/bæt/', 'language': 'en', 'gloss': 'bat'},
    {'transcription': '/ˈhjuːmən/', 'language': 'en', 'gloss': 'human'},
    {'transcription': '/bɝd/', 'language': 'en', 'gloss': 'bird'},
    {'transcription': '/ˈɡato/', 'language': 'es', 'gloss': 'cat'},
    {'transcription': '/ʃa/', 'language': 'fr', 'gloss': 'cat'},
    {'transcription': 'mā', 'language': 'zh', 'gloss': 'mother'},
    {'transcription': 'mǎ', 'language': 'zh', 'gloss': 'horse'},
]


def main():
    ipa = pm.Phonemescape()
    graph = ipa.connect_graph()          # bolt://localhost:7687 by default
    try:
        print("Inventory segments added:", graph.load_inventory())
        ids = graph.add_samples(SAMPLES)
        print("Graph:", graph.stats())

        first = ids[0]
        print(f"\nSamples similar to {SAMPLES[0]['transcription']}:")
        for row in graph.similar_samples(first):
            print(f"  {row['transcription']:<14} {row['score']:.3f}")

        print("\nSamples containing /k/ (incl. variants such as kʰ):")
        for row in graph.samples_with_segment('k'):
            print(" ", row['transcription'])

        print("\nSamples with a voiced stop [-continuant, -sonorant, +voice]:")
        for row in graph.samples_in_natural_class(continuant='-', sonorant='-', voice='+'):
            print(f"  {row['transcription']:<14} {row['matching_segments']}")

        print("\nEnglish segment frequencies:", graph.segment_frequencies('en')[:8])
    finally:
        graph.close()


if __name__ == "__main__":
    main()
