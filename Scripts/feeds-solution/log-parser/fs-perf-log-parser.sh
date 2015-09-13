#!/usr/bin/python

# Usage: ./fs-perf-log-parser.sh feeds-solution.log -o output.txt --force --verbose
#   or simply: ./fs-perf-log-parser.sh -f -v

DEFAULT_LOG_FILE = 'feeds-solution.log'
DEFAULT_OUTPUT_FILE = 'output.txt'
LOG_PATTERN = r'^(?P<datetime>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[[^]]+\].*?-\s((?P<subscriber>\S+)\s(?P<subscriberEvent>\d+),\s)*(?P<provider>\S+)(\sTID_\d+)*\s\|\sMATCH\s(?P<providerEvent>.*?)\s\|\sSEQ\s(?P<sequenceId>.*?)\s\|\s\S+:\s\[(?P<text>[^\]]+)\].*?$'
# Original Ruby Regex Pattern: ^(?<datetime>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s\[[^]]+\].*?-\s((?<subscriber>\S+)\s(?<subscriberEvent>\d+),\s)*(?<provider>\S+)(\sTID_\d+)*\s\|\sMATCH\s(?<providerEvent>.*?)\s\|\sSEQ\s(?<sequenceId>.*?)\s\|\s\S+:\s\[(?<text>[^\]]+)\].*?$


import sys
import os.path
import argparse
import re
from datetime import datetime


# PerfLog class =============================================================
class PerfLog:

	def __init__(self, subscriber = '', subscriber_event = '', provider = '', provider_event = '', sequence_id = '', text = '', date_time = ''):
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
		return '%s [Subscriber=%s, SubscriberEvent=%s, Provider=%s, ProviderEvent=%s, SequenceID=%s, Text=%s, DateTime=%s]' % (
			PerfLog.__name__
			, self.subscriber
			, self.subscriber_event
			, self.provider
			, self.provider_event
			, self.sequence_id
			, self.text
			, self.date_time
		)
# End of PerfLog class ======================================================


# Main
def main():
	args = setup_args()
	logs = read_file(args.log_file, args.verbose)
	perf_logs = parse_logs(logs, args.verbose)
	result = calculate_perf_logs(perf_logs, args.verbose)
	write_file(args.output, result, args.verbose)

	if args.verbose:
		print ('Done!\n')


# Setup terminal command arguments
def setup_args():
	parser = argparse.ArgumentParser(description='FSPerfLog Parser 1.0\nTeam Bata (c) 2015', formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('log_file', nargs='?', default=DEFAULT_LOG_FILE, help='log file to parse')
	parser.add_argument('-f', '--force', action='store_true', help='overrides output file without asking')
	parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
	parser.add_argument('-o', '--output', nargs='?', default=DEFAULT_OUTPUT_FILE, help='output file to generate')
	args, unknown = parser.parse_known_args()

	if unknown:
		print ('%s: unknown options - %s' % (__file__, tuple(unknown)))
		print ('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
		sys.exit()

	if not os.path.isfile(args.log_file):
		if args.log_file != DEFAULT_LOG_FILE:
			print ('%s: log file \'%s\' not found.' % (__file__, args.log_file))
			print ('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
			sys.exit()
		else:
			parser.print_help()
			sys.exit()

	if os.path.isfile(args.output) and not args.force:
		print ('%s: output file \'%s\' already exists. Use --force argument to allow overriding of output file.' % (__file__, args.output))
		print ('Try \'python %s --help\' for more information.' % os.path.basename(__file__))
		sys.exit()

	if args.verbose:
		print ('+==============================+')
		print ('|  Kambi FSPerfLog Parser 1.0  |')
		print ('|          Team Bata           |')
		print ('|      Copyright (c) 2015      |')
		print ('+==============================+\n')
		print ('  Log file    = %s' % args.log_file)
		print ('  Output file = %s\n' % args.output)

	return args


# Read log file
def read_file(log_file, verbose = False):
	if verbose:
		print ('Successfully read log file \'%s\'.' % log_file)

	with open(log_file) as in_file:
		return in_file.readlines()


# Write to output file
def write_file(output_file, content, verbose = False):
	with open(output_file, 'w') as out_file:
		for line in content:
			out_file.write('%s\n' % line)

	if verbose:
		print ('Created output file: \'%s\'.' % output_file)


# Parse raw logs using regex pattern
def parse_logs(logs, verbose = False):
	perf_logs = []

	if verbose:
		print ('Parsing:')

	count = 0
	for log in logs:
		matcher = re.match(LOG_PATTERN, log)
		if (matcher):
			perf_log = PerfLog(
				matcher.group('subscriber')
				, matcher.group('subscriberEvent')
				, matcher.group('provider')
				, matcher.group('providerEvent')
				, matcher.group('sequenceId')
				, matcher.group('text')
				, matcher.group('datetime')
			)
			perf_logs.append(perf_log)

			count = count + 1
			if verbose:
				print ('- %s' % perf_log)

	if verbose:
		print ('    %d line(s) successfully parsed' % count)

	return perf_logs


# Calculate time differences for each parsed log entries
def calculate_perf_logs(perf_logs, verbose = False):
	output = []

	subscriber_logs = []
	provider_logs = {}

	if verbose:
		print ('Calculating elapsed times:')

	for perf_log in perf_logs:
		if perf_log.subscriber:
			subscriber_logs.append(perf_log)
		else:
			key = '%s_%s' % (perf_log.provider_event, perf_log.sequence_id)
			provider_logs[key] = perf_log

	for subscriber_log in subscriber_logs:
		provider_log_key = '%s_%s' % (subscriber_log.provider_event, subscriber_log.sequence_id)
		provider_log = provider_logs[provider_log_key]
		elapsed_time = unix_time_in_millis(subscriber_log.date_time) - unix_time_in_millis(provider_log.date_time)

		result = '  %d ms -> %s, %s %s' % (elapsed_time, subscriber_log.subscriber, provider_log.provider_event, provider_log.provider)
		output.append(result)

		if verbose:
			print (result)

	return output


# Datetime to Unix epoch format
def unix_time_in_millis(date_time):
	epoch = datetime.utcfromtimestamp(0)
	delta = date_time - epoch
	return delta.total_seconds() * 1000.0


# Main entry point
main()
