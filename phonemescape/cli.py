"""
Command-line interface: ``phonemescape <command> ...``

    phonemescape info tʰ
    phonemescape compare p b
    phonemescape similar i -k 5
    phonemescape analyze "/ˈhjuːmən/"
    phonemescape class sonorant=- continuant=+
    phonemescape graph init                 # local Neo4j only
    phonemescape graph add "/kæt/" --language en --gloss cat
    phonemescape graph similar <sample-id>
    phonemescape graph stats
"""

import argparse
import json
import sys
from typing import List, Optional

from .core import Phonemescape


def _print(obj: object) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def _feature_pairs(pairs: List[str]) -> dict:
    out = {}
    for pair in pairs:
        if '=' not in pair:
            raise SystemExit(f"Expected feature=value, got {pair!r}")
        k, v = pair.split('=', 1)
        out[k] = v
    return out


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog='phonemescape', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)

    p = sub.add_parser('info', help='describe one segment')
    p.add_argument('segment')
    p = sub.add_parser('compare', help='similarity of two segments')
    p.add_argument('a')
    p.add_argument('b')
    p = sub.add_parser('similar', help='most similar chart symbols')
    p.add_argument('segment')
    p.add_argument('-k', '--top-k', type=int, default=10)
    p.add_argument('-t', '--type', choices=['vowel', 'consonant', 'both'], default='both')
    p = sub.add_parser('analyze', help='tokenize and analyse a transcription')
    p.add_argument('transcription')
    p = sub.add_parser('class', help='natural class: feature=value ...')
    p.add_argument('features', nargs='+')

    g = sub.add_parser('graph', help='local Neo4j sample graph')
    gsub = g.add_subparsers(dest='graph_command', required=True)
    gsub.add_parser('init', help='create constraints and load the IPA inventory')
    ga = gsub.add_parser('add', help='add a sample')
    ga.add_argument('transcription')
    ga.add_argument('--id')
    ga.add_argument('--language')
    ga.add_argument('--gloss')
    ga.add_argument('--source')
    gs = gsub.add_parser('similar', help='samples similar to a sample')
    gs.add_argument('sample_id')
    gs.add_argument('-n', '--limit', type=int, default=10)
    gw = gsub.add_parser('with', help='samples containing a segment')
    gw.add_argument('segment')
    gsub.add_parser('stats', help='node and relationship counts')

    args = parser.parse_args(argv)
    ipa = Phonemescape()
    try:
        if args.command == 'info':
            _print(ipa.get_phoneme_info(args.segment))
        elif args.command == 'compare':
            _print({'similarity': ipa.calculate_similarity(args.a, args.b),
                    'differing_features': ipa.differing_features(args.a, args.b)})
        elif args.command == 'similar':
            _print(ipa.find_similar_phonemes(args.segment, args.type, args.top_k))
        elif args.command == 'analyze':
            result = ipa.analyze_word(args.transcription)
            result.pop('phoneme_details')
            _print(result)
        elif args.command == 'class':
            _print(ipa.find_phonemes_by_features(**_feature_pairs(args.features)))
        elif args.command == 'graph':
            graph = ipa.connect_graph()
            try:
                if args.graph_command == 'init':
                    _print({'new_segments': graph.load_inventory(), **graph.stats()})
                elif args.graph_command == 'add':
                    _print({'id': graph.add_sample(args.transcription, sample_id=args.id,
                                                   language=args.language, gloss=args.gloss,
                                                   source=args.source)})
                elif args.graph_command == 'similar':
                    _print(graph.similar_samples(args.sample_id, args.limit))
                elif args.graph_command == 'with':
                    _print(graph.samples_with_segment(args.segment))
                elif args.graph_command == 'stats':
                    _print(graph.stats())
            finally:
                graph.close()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
