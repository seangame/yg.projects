import logging
import argparse

import requests
import jaraco.util.logging

import yg.netsuite

def run():
	yg.netsuite.use_sandbox()
	yg.netsuite.TimeBill.solicit().submit()

def get_args():
	"""
	Parse command-line arguments, including the Command and its arguments.
	"""

	parser = argparse.ArgumentParser()
	jaraco.util.logging.add_arguments(parser)
	return parser.parse_args()

def setup_requests_logging(level):
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(level)
	requests_log.propagate = True

	# enable debugging at httplib level
	requests.packages.urllib3.connectionpool.HTTPConnection.debuglevel = level <= logging.DEBUG

def submit_time():
	args = get_args()
	jaraco.util.logging.setup(args, format="%(message)s")
	setup_requests_logging(args.log_level)
	run()
