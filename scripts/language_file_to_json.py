#!/usr/bin/env python3

"""This script takes an EAC language file and converts it into a JSON for the log checker."""

import os
import sys
import json
import re
import codecs

import json_builder.constants as constants
import json_builder.generators as generators


def main():
    """The main function for the module; handles calling the other functions."""
    language_info = {
        'patterns': constants.SAMPLEPATTERN,
        'translation': {}
    }
    filename = sys.argv[1]
    file_contents = read_file(filename)
    for number, line in regex_the_line(file_contents):
        language_info['translation'][number] = line
    compile_patterns(language_info, filename)
    dump_json(language_info)


def read_file(path):
    """Reads the file and returns a list of the file's contents."""
    if not os.path.exists(path):
        print(path, 'does not exist! Exiting.')
        exit()

    with open(path, 'r', encoding='utf-16le') as source_file:
        file_contents = source_file.readlines()

    return file_contents


def dump_json(language_info):
    """Dump the language file to a JSON."""
    input_filename = os.path.basename(sys.argv[1])
    export_filename = re.sub(r'\..+', '', input_filename).lower()
    file_path = os.path.dirname(os.path.realpath(__file__))
    export_filepath = os.path.join(file_path, '{}.json'.format(export_filename))
    if os.path.exists(export_filepath):
        print('{} already exists, JSON dump canceled.'.format(export_filepath))
    else:
        with codecs.open(export_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(language_info, jsonfile, ensure_ascii=False, indent=4)


def regex_the_line(file_contents):
    """Extracts the line number and text from the language file,
    and returns a (#, line) tuple."""
    for line in file_contents:
        result = re.search(r'(\d+)\s=>?\s"(.*)"', line)
        if result:
            number, text = int(result.group(1)), result.group(2).strip()
            if number in constants.LINENUMBERS:
                yield (number, text)


def compile_patterns(language_info, filename):
    """Compile the patterns dict for the language."""
    translation = language_info['translation']
    generators.substitute_translations(language_info['patterns'], translation)
    language_info['patterns']['drive'] = generators.regex_the_drive(translation)
    generators.ninety_five_settings(language_info['patterns'], translation, filename)
    generators.htoa_crc_checksum_substitution(language_info['patterns'], translation)
    generators.accuraterip(language_info['patterns'], translation)
    generators.range_accuraterip(language_info['patterns'], translation)


if __name__ == '__main__':
    main()
