import argparse
import os


def parse_args(args, overlays_path):
    parser = argparse.ArgumentParser('yaml_helper.py')
    parser.add_argument('overlay', choices=os.listdir(overlays_path), help='overlay to process')
    parser.add_argument('action', choices=['summarize', 'split'],
                        help='split out.yaml (`kubectl kustomize /path/to/overlay -o /path/to/overlay/out.yaml`) '
                             'into separate resource files in "split"-folder')
    return parser.parse_args(args)
