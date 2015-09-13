# Usage: python feeds-log-parser.py feeds-solution.log --output output.txt --force --verbose
#   or simply: python feeds-log-parser.py -f -v
#
# For help: python feeds-log-parser.py --help
#
#
# Version History
#
# 2015-07-23    v1.0.0      First version
# 2015-07-24    v1.0.1      Added --show-feeds command argument. Some fixes and minor refactoring. Reformatted output.
# 2015-07-27    v1.0.2      Added statistics: average processing time. Some minor refactoring (proper way of using @property - only when you need to).
#

DEFAULT_LOG_FILE = 'feeds-solution.log'
DEFAULT_OUTPUT_FILE = 'output.txt'

# Ruby-friendly regex pattern:
#   ^(?<datetime>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[[^]]+\].*?-\s((?<subscriber>\S+)\s(?<subscriberEvent>\d+),\s)*(?<provider>\S+)(\sTID_\d+)*.*?\s\|\sMATCH\s(?<providerEvent>.*?)\s\|\sSEQ\s(?<sequenceId>.*?)\s\|\s\S+:\s\[(?<text>[^\]]+)\].*?$
LOG_PATTERN = r'^' \
              r'(?P<datetime>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[[^]]+\].*?-\s' \
              r'((?P<subscriber>\S+)\s(?P<subscriberEvent>\d+),\s)*' \
              r'(?P<provider>\S+)(\sTID_\d+)*.*?' \
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
        self.subscriber = subscriber
        self.subscriber_event = subscriber_event
        self.provider = provider
        self.provider_event = provider_event
        self.sequence_id = sequence_id
        self.text = text
        self.date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S,%f')

    def __repr__(self):
        return self.__to_string()

    def __str__(self):
        return self.__to_string()

    def __to_string(self):
        return '%s [Subscriber=%s, SubscriberEvent=%s, Provider=%s, ProviderEvent=%s, SequenceID=%s, Text=%s, DateTime=%s]' \
               % (FeedsLogEntry.__name__, self.subscriber, self.subscriber_event, self.provider, self.provider_event, self.sequence_id, self.text, self.date_time)

# End of FeedsLogEntry class ================================================


# FeedsResultEntry class ====================================================
class FeedsResultEntry:

    def __init__(self, source, destination, start_time, end_time, elapsed_time, match_id, sequence_id, text):
        self.source = source
        self.destination = destination
        self.start_time = start_time
        self.end_time = end_time
        self.elapsed_time = elapsed_time
        self.match_id = match_id
        self.sequence_id = sequence_id
        self.text = text

    def __repr__(self):
        return self.__to_string()

    def __str__(self):
        return self.__to_string()

    def __to_string(self):
        return '%s [Source=%s, Destination=%s, StartTime=%s, EndTime=%s, ElapsedTime=%s, MatchID=%s, SequenceID=%s, Text=%s]' \
               % (FeedsLogEntry.__name__, self.source, self.destination, self.start_time, self.end_time, self.elapsed_time, self.match_id, self.sequence_id, self.text)

# End of FeedsResultEntry class =============================================


# FeedsStatisticsEntry class ================================================
class FeedsStatisticsEntry:

    def __init__(self, name, total_feed_count=0, total_elapsed_time=0):
        self.name = name
        self._total_feed_count = total_feed_count
        self._total_elapsed_time = total_elapsed_time
        self._average_elapsed_time = 0

    @property
    def average_elapsed_time(self):
        return round(self._average_elapsed_time, 2)

    def add_new_elapsed_time(self, value):
        self._total_feed_count += 1
        self._total_elapsed_time += value
        self._average_elapsed_time = self._total_elapsed_time / self._total_feed_count

    def __repr__(self):
        return self.__to_string()

    def __str__(self):
        return self.__to_string()

    def __to_string(self):
        return '%s [Name=%s, TotalFeedCount=%d, TotalElapsedTime=%d, AverageElapsedTime=%d]' \
               % (FeedsStatisticsEntry.__name__, self.name, self._total_feed_count, self._total_elapsed_time, self._average_elapsed_time)

# End of FeedsStatisticsEntry class =========================================


# FeedsIntervalEntry class ================================================
class FeedsIntervalEntry:

    def __init__(self, start_time, end_time, interval, feed_count, feeds):
        self._start_time = start_time
        self._end_time = end_time
        self._interval = interval
        self._feed_count = feed_count
        self._feeds = feeds

    def add_entry(self, value):
        self._feed_count += 1
        self._feeds.append(value)

    def __repr__(self):
        return self.__to_string()

    def __str__(self):
        return self.__to_string()

    def __to_string(self):
        return '%s [StartTime=%d, EndTime=%d, Interval=%d s, Count=%s]' \
               % (FeedsIntervalEntry.__name__, self._start_time, self._end_time, self._interval / 1000, self._feed_count)

# End of FeedsIntervalEntry class =========================================


# Main
def main():
    args = setup_command_args()
    raw_logs = read_log_file(args.log_file, args.verbose)
    feeds_logs = parse_raw_logs(raw_logs, args.verbose)
    result_logs = calculate_elapsed_times(feeds_logs, args.verbose)
    feeds_statistics = calculate_average_elapsed_time(result_logs, args.verbose)
    feeds_interval = calculate_feeds_interval(result_logs, args.verbose)
    output = format_output(result_logs, feeds_statistics, feeds_interval, args.show_feeds, args.verbose)
    write_to_output_file(args.output, output, args.verbose)

    if args.verbose:
        print('Done!\n')


# Setup command arguments
def setup_command_args():
    ap = argparse.ArgumentParser(description='FeedsLogParser 1.0\nTeam Bata (c) 2015', formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument('log_file', metavar='log-file', nargs='?', default=DEFAULT_LOG_FILE, help='log file to parse')
    ap.add_argument('-f', '--force', action='store_true', help='overrides output file without asking')
    ap.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    ap.add_argument('-s', '--show-feeds', action='store_true', help='show feed messages')
    ap.add_argument('-o', '--output', nargs='?', default=DEFAULT_OUTPUT_FILE, help='output file to generate')
    args, unknown_args = ap.parse_known_args()

    if unknown_args:
        print('%s: unknown options - %s' % (__file__, unknown_args))
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

    if args.output is None:
        print('%s: no output file specified.' % __file__)
        print('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
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
        print('    Log file    = %s' % args.log_file)
        print('    Output file = %s\n' % args.output)

    return args


# Read log file
def read_log_file(log_file, verbose=False):
    if verbose:
        print('Reading log file \'%s\'...' % log_file)

    with open(log_file) as f:
        return f.readlines()


# Write to output file
def write_to_output_file(output_file, output_list, verbose=False):
    try:
        with open(output_file, 'w') as f:
            for item in output_list:
                f.write('%s\n' % item)
    except IOError as e:
        print('%s: unable to write to output file \'%s\' (%s).' % (__file__, output_file, e))
        print('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
        sys.exit()

    if verbose:
        print('Created output file: \'%s\'.' % output_file)


# Parse raw logs using regex pattern
def parse_raw_logs(raw_logs, verbose=False):
    feeds_logs = []

    if verbose:
        print('Parsing log entries...')

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
                print('    %s' % entry)

    if verbose:
        print('        %d line(s) successfully parsed' % count)

    return feeds_logs


# Calculate elapsed times between source and destination log entries and store as result log
def calculate_elapsed_times(feeds_logs, verbose=False):
    result_logs = []

    source_logs = {}
    dest_logs = []
    missing_pair_keys = []

    if verbose:
        print('Calculating elapsed times...')

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
                if source_log_key not in missing_pair_keys:
                    print('    No matching source log, skipping - %s' % source_log_key)
                    missing_pair_keys.append(source_log_key)

            continue

        start_time = __unix_time_in_millis(source_log.date_time)
        end_time = __unix_time_in_millis(dest_log.date_time)
        elapsed_time = end_time - start_time
        if elapsed_time > 0:
            if elapsed_time > 2000:
                print ('LogEntry has {} ms processing time {}'.format(elapsed_time, dest_log.text))
            else:
                result_logs.append(FeedsResultEntry(source_log.provider, dest_log.subscriber, start_time, end_time, elapsed_time, source_log.provider_event, dest_log.sequence_id, dest_log.text))

    return result_logs


# Calculate average elapsed time per source
def calculate_average_elapsed_time(result_logs, verbose=False):
    feeds_statistics = {}

    if verbose:
        print('Calculating average processing time...')

    for result in result_logs:
        key = '{} to {}'.format(result.source, result.destination)
        if key not in feeds_statistics:
            feeds_statistics[key] = FeedsStatisticsEntry(key, 1, result.elapsed_time)
        else:
            feeds_statistics[key].add_new_elapsed_time(result.elapsed_time)

    return feeds_statistics


# Calculate feeds interval per second interval for up to 5 secs
# def calculate_feeds_interval(result_logs, verbose=False):
#     feeds_interval_logs = []
#     average_feeds_intervals = {}
#
#     if verbose:
#         print('Calculating feeds interval...')
#
#     count = 0
#
#     # get feed's first source start time and last destination end time
#     for log in result_logs:
#         count += 1
#         if count is 1:
#             source_first_start_time = log.start_time
#         else:
#             destination_last_end_time = log.end_time
#
#     included_feeds = []
#     start_time = source_first_start_time
#     min_increment = 1000 # 1 second increment
#     max_increment = 5000 # up to 5 seconds
#
#     while start_time < destination_last_end_time:
#         end_time = start_time
#         interval = 0
#
#         while interval < max_increment:
#             end_time += min_increment
#             interval = end_time - start_time
#
#             feeds_interval = FeedsIntervalEntry(start_time, end_time, interval, 0, included_feeds)
#             for log in result_logs:
#                 if log.start_time >= start_time and log.end_time <= end_time:
#                     feeds_interval.add_entry(log)
#
#             # include only if there are feeds counted within the interval
#             # if feeds_interval._feed_count > 0:
#             feeds_interval_logs.append(feeds_interval)
#
#         start_time += min_increment
#
#     for feeds_interval in feeds_interval_logs:
#         feeds = []
#         if feeds_interval._interval not in average_feeds_intervals:
#             feeds.append(feeds_interval._feed_count)
#             average_feeds_intervals[feeds_interval._interval] = feeds
#         else:
#             feeds = average_feeds_intervals[feeds_interval._interval]
#             feeds.append(feeds_interval._feed_count)
#
#     if verbose:
#         for log in feeds_interval_logs:
#             print(log)
#
#     return feeds_interval_logs

def calculate_feeds_interval(result_logs, verbose=False):
    if verbose:
        print('Calculating average feeds interval...')

    source_first_start_time = 0
    destination_last_end_time = 0

    # get feed's first source start time and last destination end time
    for log in result_logs:
        if source_first_start_time == 0:
            source_first_start_time = log.start_time
        else:
            source_first_start_time = min(source_first_start_time, log.start_time)

        destination_last_end_time = max(destination_last_end_time, log.end_time)

    duration_in_secs = (destination_last_end_time - source_first_start_time) / 1000
    total_feeds = len(result_logs)
    average_feeds_interval = total_feeds / duration_in_secs

    output = '- Duration: %d sec, Total No. of Feeds Processed: %d, Average: %f feeds/sec' % (duration_in_secs, total_feeds, average_feeds_interval)

    return output


# Make output readable as humanely as possible
def format_output(result_logs, feeds_statistics, feeds_interval, show_feeds=False, verbose=False):
    output = []

    if verbose:
        print('Generating output:')
        print('- Feed processing times:')

    output.append('- Feed processing times:')

    source_width = 0
    destination_width = 0
    elapsed_time_width = 0
    match_id_width = 0
    sequence_id_width = 0
    average_elapsed_time_width = 0

    for log in result_logs:
        source_width = max(source_width, len(log.source))
        destination_width = max(destination_width, len(log.destination))
        elapsed_time_width = max(elapsed_time_width, len(str(log.elapsed_time)))
        match_id_width = max(match_id_width, len(log.match_id))
        sequence_id_width = max(sequence_id_width, len(log.sequence_id))
    for key in feeds_statistics.keys():
        average_elapsed_time_width = max(average_elapsed_time_width, len(str(feeds_statistics[key].average_elapsed_time)))

    for log in result_logs:
        result = '%s ms -> %s to %s [Match / Seq: %s / %s' % (
            str('%0d' % log.elapsed_time).rjust(elapsed_time_width)
            , log.source.ljust(source_width)
            , log.destination.ljust(destination_width)
            , log.match_id.rjust(match_id_width)
            , log.sequence_id.zfill(sequence_id_width)
        )

        if show_feeds:
            result += ' | Feed: %s]' % log.text
        else:
            result += ']'

        output.append(result)

        if verbose:
            print('    %s' % result)

    output.append('- Average processing time:')
    if verbose:
        print('- Average processing time:')

    for key in feeds_statistics.keys():
        result = '    %s : %s ms' % (
            key.ljust(source_width)
            , str(feeds_statistics[key].average_elapsed_time).rjust(average_elapsed_time_width)
        )
        output.append(result)

        if verbose:
            print(result)

    output.append(feeds_interval)
    if verbose:
        print(feeds_interval)

    return output


# DateTime to Unix epoch format
def __unix_time_in_millis(date_time):
    epoch = datetime.utcfromtimestamp(0)
    delta = date_time - epoch
    return delta.total_seconds() * 1000.0


# Main entry point
main()
