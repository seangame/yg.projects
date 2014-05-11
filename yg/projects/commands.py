import argparse

import jaraco.util.logging
import jaraco.util.timing
from workalendar.core import Calendar

import yg.netsuite
from . import calendar
from . import models

class InteractiveEntry:
	@classmethod
	def submit_time(cls):
		yg.netsuite.use_sandbox()
		yg.netsuite.TimeBill.solicit().submit()

	@classmethod
	def get_args():
		"""
		Parse command-line arguments, including the Command and its arguments.
		"""
		parser = argparse.ArgumentParser()
		jaraco.util.logging.add_arguments(parser)
		return parser.parse_args()

	@classmethod
	def run(cls):
		args = cls.get_args()
		jaraco.util.logging.setup(args, format="%(message)s")
		jaraco.util.logging.setup_requests_logging(args.log_level)
		cls.submit_time()


class TimeEntry:
	"""
	A command-line entry point for automating time entry
	"""

	calendar = Calendar()
	"A workalendar Calendar instance suitable for resolving 'working days'"

	@classmethod
	def get_project_distribution(cls, projects):
		"""
		Return a models.Distribution of models.Projects over which hours
		should be distributed.
		"""
		raise NotImplementedError("Distribution must be defined by subclass")

	@staticmethod
	def get_args():
		parser = argparse.ArgumentParser()
		parser.add_argument('month', type=calendar.month_days)
		parser.add_argument('--prod', action="store_false", default=True,
			dest="sandbox")
		return parser.parse_args()

	@classmethod
	def run(cls):
		args = cls.get_args()
		if args.sandbox:
			yg.netsuite.use_sandbox()
		days = map(calendar.is_working_day, args.month)
		projects = models.Projects.from_url()
		dist = cls.get_project_distribution(projects)
		tb = dist.create_timebill(days, hours=cls.calendar.hours_per_day)
		print("Submitting", len(tb), "entries to NetSuite...")
		with jaraco.util.timing.Stopwatch() as watch:
			tb.submit()
		print("Completed in", watch.elapsed)
