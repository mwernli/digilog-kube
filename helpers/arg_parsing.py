import argparse
import os
import re


semver_pattern = re.compile(r'^\d+\.\d+(\.\d+)?$')


def _semver_type(arg_value):
    if not semver_pattern.match(arg_value):
        raise argparse.ArgumentTypeError(
            f'invalid image_tag "{arg_value}", must be format <major>.<minor>[.<patch>] , e.g. 0.1.2'
        )
    return arg_value


def parse_args(args, overlays_path):
    parser = argparse.ArgumentParser('yaml_helper.py')
    subparsers = parser.add_subparsers(help='action types')

    summarize_parser = subparsers.add_parser('summarize', help='summarize resource requests of the overlay')
    summarize_parser.add_argument('overlay', choices=os.listdir(overlays_path), help='overlay to process')
    summarize_parser.set_defaults(action='summarize')

    split_parser = subparsers.add_parser(
        'split',
        help='split out.yaml (`kubectl kustomize /path/to/overlay -o /path/to/overlay/out.yaml`) '
             'into separate resource files in "split"-folder',
    )
    split_parser.add_argument('overlay', choices=os.listdir(overlays_path), help='overlay to process')
    split_parser.set_defaults(action='split')

    image_tag_parser = subparsers.add_parser('image-tag', help='show or set tag of trephor images')
    image_tag_parser.set_defaults(action='image-tag')
    image_tag_parser.add_argument(
        '-u',
        '--update-image-tag',
        metavar='NEW_IMAGE_TAG',
        type=_semver_type,
        help='update the image tag in base config where applicable (format <major>.<minor>[.<patch>] , e.g. 0.1.2)',
    )

    return parser.parse_args(args)
