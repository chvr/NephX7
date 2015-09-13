DEFAULT_INPUT_FILE = 'all-matches.txt'
DEFAULT_OUTPUT_FILE = 'regextractor.log'

# Ruby-friendly regex pattern:
#   match\s.*?matchid="(?<match_id>[^"]+)"((?!\Stype)[\s\S\n])+?\stype="(?<type>1044)"
REGEX_PATTERN = r'match\s.*?matchid="(?P<match_id>[^"]+)"((?!\Stype)[\s\S\n])+?\stype="(?P<type>1044)"'


import argparse
import re
import os
import sys


# RegexObject class =========================================================

class RegexObject:
    def __init__(self, match_id, event_type):
        self.match_id = match_id
        self.event_type = event_type
        self.count = 1

    def increment(self):
        self.count += 1

    def __str__(self):
        return self._tostring()

    def __repr__(self):
        return self._tostring()

    def _tostring(self):
        return '{} [MatchID: {}, EventType: {}, Count: {}]'.format(self.__class__.__name__, self.match_id, self.event_type, self.count)

# End of RegexObject class ==================================================


def main():
    args = setup_command_args()
    raw_input = read_input_file(args.input_file, args.quiet)
    output_map = parse_raw_input(raw_input, args.quiet)
    write_to_output_file(args.output_file, output_map, args.quiet)
    display_result(output_map, args.quiet)


# Setup command arguments
def setup_command_args():
    ap = argparse.ArgumentParser(description='Regextractor 1.0\nTeam Bata (c) 2015', formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('input_file', metavar='input-file', nargs='?', default=DEFAULT_INPUT_FILE, help='input file to parse')
    ap.add_argument('-q', '--quiet', action='store_true', help='silent mode')
    ap.add_argument('-o', '--output-file', nargs='?', default=DEFAULT_OUTPUT_FILE, help='output file to generate')
    args, unknown_args = ap.parse_known_args()

    if unknown_args:
        print('{}: unknown options - {}'.format(__file__, unknown_args))
        print('Try \'python {} --help\' for more information.'.format(os.path.basename(__file__)))
        sys.exit()

    if not os.path.isfile(args.input_file):
        if args.input_file != DEFAULT_INPUT_FILE:
            print('{}: input file \'{}\' not found.'.format(__file__, args.input_file))
            print('Try \'python {} --help\' for more information.'.format(os.path.basename(__file__)))
            sys.exit()
        else:
            ap.print_help()
            sys.exit()

    if args.output_file is None:
        print('{}: no output file specified.'.format(__file__))
        print('Try \'python {} --help\' for more information.'.format(os.path.basename(__file__)))
        sys.exit()

    if not args.quiet:
        print('+==============================+')
        print('|    Kambi Regextractor 1.0    |')
        print('|          Team Bata           |')
        print('|      Copyright (c) 2015      |')
        print('+==============================+\n')
        print('    Input file  = {}'.format(args.input_file))
        print('    Output file = {}\n'.format(args.output_file))

    return args


# Read input file
def read_input_file(input_file, quiet=False):
    if not quiet:
        print('Reading input file \'{}\'...'.format(input_file))

    with open(input_file) as f:
        return f.read()


# Write to output file
def write_to_output_file(output_file, output_map, quiet=False):
    try:
        with open(output_file, 'w') as f:
            for key in output_map:
                f.write('{}\n'.format(output_map[key]))
    except IOError as e:
        print('{}: unable to write to output file \'{}\' ({}).'.format(__file__, output_file, e))
        print('Try \'python {} --help\' for more information.'.format(os.path.basename(__file__)))
        sys.exit()

    if not quiet:
        print('Created output file: \'{}\'.'.format(output_file))


# Parse raw input using regex pattern
def parse_raw_input(raw_input, quiet=False):
    output_map = {}

    if not quiet:
        print('Parsing entries...')

    count = 0
    for result in re.finditer(REGEX_PATTERN, raw_input):
        entry = RegexObject(
            result.group('match_id')
            , result.group('type')
        )
        if entry.match_id not in output_map:
            output_map[entry.match_id] = entry
        else:
            output_map[entry.match_id].increment()

        if not quiet:
            print('    {}'.format(output_map[entry.match_id]))
            count += 1

    if not quiet:
        print('        {} line(s) successfully parsed'.format(count))

    return output_map


# Display result
def display_result(output_map, quiet=False):
    lowest_count = None
    highest_count = 0
    match_count = 0

    if quiet:
        return

    print('Result:')
    for key in output_map:
        if lowest_count is None or output_map[key].count< lowest_count:
            lowest_count = output_map[key].count
        if output_map[key].count > highest_count:
            highest_count = output_map[key].count

    for i in reversed(range(lowest_count, highest_count + 1)):
        for key in output_map:
            if output_map[key].count == i:
                match_count += 1
                print('    Match {}, Occurrence Deletions: {}'.format(output_map[key].match_id, output_map[key].count))

    print('        {} match(es) with delete occurrence'.format(match_count))


main()
