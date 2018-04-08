"""This module contains shared functions between the various top-level modules."""

import re
import os
import json
import codecs
import chardet

from heybrochecklog import UnrecognizedException


def get_log_contents(log_file):
    """Open a log file and return its contents."""
    encoding = get_log_encoding(log_file)
    with log_file.open(encoding=encoding) as log:
        contents = log.readlines()

    return contents


def get_log_encoding(log_file):
    """Get the encoding of the log file with the chardet library."""
    raw = log_file.read_bytes()
    if raw.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    else:
        result = chardet.detect(raw)
        return result['encoding'] if result['confidence'] > 0.7 else 'utf-8-sig'


def get_language_data(log):
    """Get language data."""
    eac_regex = re.compile(r'Exact Audio Copy V[0-1]\.[0-9]+.*?from.*')
    xld_regex = re.compile(r'X Lossless Decoder version [0-9abc]+ \([0-9\.]+\)')
    if xld_regex.match(log[0]):
        return open_json('xld.json')
    else:
        re_rip_lines = open_json('eac_rip_lines.json')
        rip_line = log[1] if eac_regex.match(log[0]) else log[0]
        # Unfortunately, not all EAC <=0.95 logs are English, so a compiled multi-language ripper
        # regex pattern is necessary.
        for language, regex in re_rip_lines.items():
            if re.match(regex, rip_line):
                return open_json('eac', language + '.json')

    raise UnrecognizedException('Could not recognize ripper / log language.')


def open_json(*paths):
    """Open the language JSON patterns file and return it."""
    basepath = get_path()
    with open(os.path.join(basepath, 'resources', *paths)) as jsonfile:
        language_data = json.load(jsonfile)

    return language_data


def get_path():
    """Get the filepath for the root package directory."""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
