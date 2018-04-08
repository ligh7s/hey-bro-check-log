#!/usr/bin/env python3

import argparse
from heybrochecklog import runner


def parse_args():
    """Parse arguments."""
    description = 'Tool to analyze, translate, and score a CD Rip Log.'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('log', help='log file to check.', nargs='+')
    parser.add_argument('-t', '--translate', help='translate a foreign log to English', action='store_true')
    parser.add_argument('-m', '--markup', help='print the marked up version of the log after analyzing',
                        action='store_true')
    parser.add_argument('-s', '--score-only', help='Only print the score of the log.', action='store_true')

    return parser.parse_args()


if __name__ == '__main__':
    runner(parse_args())
