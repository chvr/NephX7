# Usage: python feeds-log-parser.py feeds-solution.log --output output.txt --force --verbose
#   or simply: python feeds-log-parser.py -f -v
#
# For help: python feeds-log-parser.py --help
#
#
# Version History
#
# 2015-07-23    v1.0.0      First version
# 2015-07-24    v1.0.1      Minor refactoring
#

DEFAULT_LOG_FILE = 'feeds-solution.log'
DEFAULT_OUTPUT_FILE = 'output.txt'

# Ruby-friendly regex pattern:
#   ^(?<datetime>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[[^]]+\].*?-\s((?<subscriber>\S+)\s(?<subscriberEvent>\d+),\s)*(?<provider>\S+)(\sTID_\d+)*\s\|\sMATCH\s(?<providerEvent>.*?)\s\|\sSEQ\s(?<sequenceId>.*?)\s\|\s\S+:\s\[(?<text>[^\]]+)\].*?$
LOG_PATTERN = r'^' \
              r'(?P<datetime>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[[^]]+\].*?-\s' \
              r'((?P<subscriber>\S+)\s(?P<subscriberEvent>\d+),\s)*' \
              r'(?P<provider>\S+)(\sTID_\d+)*' \
              r'\s\|\sMATCH\s(?P<providerEvent>.*?)' \
              r'\s\|\sSEQ\s(?P<sequenceId>.*?)' \
              r'\s\|\s\S+:\s\[(?P<text>[^\]]+)\].*?' \
              r'$'


import sys
import os.path
import argparse
import re
from datetime import datetime


# FeedsLogEntry class =======================================================
class FeedsLogEntry:

    def __init__(self, subscriber, subscriber_event, provider, provider_event, sequence_id, text, date_time):
        self._subscriber = subscriber
        self._subscriber_event = subscriber_event
        self._provider = provider
        self._provider_event = provider_event
        self._sequence_id = sequence_id
        self._text = text
        self._date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S,%f')

    @property
    def subscriber(self):
        return self._subscriber

    @property
    def subscriber_event(self):
        return self._subscriber_event

    @property
    def provider(self):
        return self._provider

    @property
    def provider_event(self):
        return self._provider_event

    @property
    def sequence_id(self):
        return self._sequence_id

    @property
    def text(self):
        return self._text

    @property
    def date_time(self):
        return self._date_time

    def __repr__(self):
        return self.__to_string()

    def __str__(self):
        return self.__to_string()

    def __to_string(self):
        return '%s [Subscriber=%s, SubscriberEvent=%s, Provider=%s, ProviderEvent=%s, SequenceID=%s, Text=%s, DateTime=%s]'\
            % (FeedsLogEntry.__name__, self.subscriber, self.subscriber_event, self.provider, self.provider_event, self.sequence_id, self.text, self.date_time)

# End of FeedsLogEntry class ================================================


# Main
def main():
    args = setup_command_args()
    raw_logs = read_log_file(args.log_file, args.verbose)
    feeds_logs = parse_raw_logs(raw_logs, args.verbose)
    result = calculate_elapsed_times(feeds_logs, args.verbose)
    write_to_output_file(args.output, result, args.verbose)

    if args.verbose:
        print('Done!\n')


# Setup command arguments
def setup_command_args():
    ap = argparse.ArgumentParser(description='FeedsLogParser 1.0\nTeam Bata (c) 2015', formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('log_file', nargs='?', default=DEFAULT_LOG_FILE, help='log file to parse')
    ap.add_argument('-f', '--force', action='store_true', help='overrides output file without asking')
    ap.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    ap.add_argument('-o', '--output', nargs='?', default=DEFAULT_OUTPUT_FILE, help='output file to generate')
    args, unknown_args = ap.parse_known_args()

    if unknown_args:
        print('%s: unknown options - %s' % (__file__, tuple(unknown_args)))
        print('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
        sys.exit()

    if not os.path.isfile(args.log_file):
        if args.log_file != DEFAULT_LOG_FILE:
            print('%s: log file \'%s\' not found.' % (__file__, args.log_file))
            print('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
            sys.exit()
        else:
            ap.print_help()
            sys.exit()

    if os.path.isfile(args.output) and not args.force:
        print('%s: output file \'%s\' already exists. Use --force argument to allow overriding of output file.' % (__file__, args.output))
        print('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
        sys.exit()

    if args.verbose:
        print('+==============================+')
        print('|   Kambi FeedsLogParser 1.0   |')
        print('|          Team Bata           |')
        print('|      Copyright (c) 2015      |')
        print('+==============================+\n')
        print('  Log file    = %s' % args.log_file)
        print('  Output file = %s\n' % args.output)

    return args


# Read log file
def read_log_file(log_file, verbose=False):
    if verbose:
        print('Reading log file \'%s\'...' % log_file)

    with open(log_file) as f:
        return f.readlines()


# Write to output file
def write_to_output_file(output_file, result_list, verbose=False):
    with open(output_file, 'w') as f:
        for item in result_list:
            f.write('%s\n' % item)

    if verbose:
        print('Created output file: \'%s\'.' % output_file)


# Parse raw logs using regex pattern
def parse_raw_logs(raw_logs, verbose=False):
    feeds_logs = []

    if verbose:
        print('Parsing:')

    count = 0
    for log in raw_logs:
        m = re.match(LOG_PATTERN, log)
        if m:
            entry = FeedsLogEntry(
                m.group('subscriber')
                , m.group('subscriberEvent')
                , m.group('provider')
                , m.group('providerEvent')
                , m.group('sequenceId')
                , m.group('text')
                , m.group('datetime')
            )
            feeds_logs.append(entry)

            if verbose:
                count += 1
                print('- %s' % entry)

    if verbose:
        print('    %d line(s) successfully parsed' % count)

    return feeds_logs


# Calculate elapsed times between source and destination log entries
def calculate_elapsed_times(feeds_logs, verbose=False):
    output = []

    source_logs = {}
    dest_logs = []

    if verbose:
        print('Calculating elapsed times:')

    for log in feeds_logs:
        if not log.subscriber:
            key = '%s_%s' % (log.provider_event, log.sequence_id)
            source_logs[key] = log
        else:
            dest_logs.append(log)

    for dest_log in dest_logs:
        try:
            source_log_key = '%s_%s' % (dest_log.provider_event, dest_log.sequence_id)
            source_log = source_logs[source_log_key]
        except KeyError:
            if verbose:
                print('  No matching source log - %s' % source_log_key)

            continue

        elapsed_time = __unix_time_in_millis(dest_log.date_time) - __unix_time_in_millis(source_log.date_time)

        result = '  %d ms -> From %s to %s of MatchID %s with SeqID of %s' % (elapsed_time, source_log.provider, dest_log.subscriber, source_log.provider_event, dest_log.sequence_id)
        output.append(result)

        if verbose:
            print(result)

    return output


# DateTime to Unix epoch format
def __unix_time_in_millis(date_time):
    epoch = datetime.utcfromtimestamp(0)
    delta = date_time - epoch
    return delta.total_seconds() * 1000.0


# Main entry point
main()
