"""
YouGov calendar modules
"""

import datetime
import functools
import sys
import itertools

import dateutil.parser
import dateutil.relativedelta as rd

class Holiday(datetime.date):
	def __new__(cls, name, indication, date, weekend_hint=rd.MO(1)):
		return datetime.date.__new__(cls, date.year, date.month, date.day)

	def __init__(self, name, indication, date, weekend_hint=rd.MO(1)):
		self.name = name
		self.indication = indication
		self.weekend_hint = weekend_hint

	@property
	def observed(self):
		delta = rd.relativedelta(weekday=self.weekend_hint)
		return self + delta if self.weekday() > 4 else self

def holidays_for_year(year):
	"""
	Produce the YouGov America holidays for the given year.
	"""
	yield Holiday("New Year's Day", "January 1st", datetime.date(year, 1, 1))

	yield Holiday("Martin L King's Birthday", "3rd Monday in January",
		datetime.date(year, 1, 1) + rd.relativedelta(weekday=rd.MO(3)))

	yield Holiday("President's Day", "3rd Monday in February",
		datetime.date(year, 2, 1) + rd.relativedelta(weekday=rd.MO(3)))

	yield Holiday("Memorial Day", "Last Monday in May",
		datetime.date(year, 5, 31) + rd.relativedelta(weekday=rd.MO(-1)))

	yield Holiday("Independence Day", "July 4th", datetime.date(year, 7, 4))

	yield Holiday("Labor Day", "1st Monday in September",
		datetime.date(year, 9, 1) + rd.relativedelta(weekday=rd.MO(1)))

	tg = Holiday("Thanksgiving Day", "4th Thursday in November",
		datetime.date(year, 11, 1) + rd.relativedelta(weekday=rd.TH(4)))
	yield tg
	yield Holiday("Day after Thanksgiving", "Friday after Thanksgiving",
		tg + datetime.timedelta(days=1))

	# Christmas Eve and Christmas
	yield Holiday("Christmas Eve", "December 24",
		datetime.date(year, 12, 24), rd.FR(-1))
	yield Holiday("Christmas Day", "December 25",
		datetime.date(year, 12, 25))

	# New Years Eve
	yield Holiday("New Year's Eve", "December 31",
		datetime.date(year, 12, 31), rd.FR(-1))


@functools.lru_cache()
def holidays_for_year_cached(year):
	return tuple(holidays_for_year(year))

def is_holiday(day):
	return day in holidays_for_year_cached(day.year)

def print_holidays():
	year = int(sys.argv[1])
	print("= Holidays {year} =".format(**vars()), end='\n\n')

	print("|| '''Holiday''' || '''Day Indicated''' || '''Day Observed''' ||")
	for holiday in holidays_for_year(year):
		print("|| {holiday.name} || {holiday.indication} || "
			"{holiday.observed:%A, %B %d} ||".format(**vars()))

def date_range(start, end):
	one_day = datetime.timedelta(days=1)
	day = start
	while day < end:
		yield day
		day += one_day

def is_weekend(date):
	return date.weekday() > 4

def weekdays(range):
	return itertools.filterfalse(is_weekend, range)

def always_date(date):
	if isinstance(date, datetime.datetime):
		return date.date()
	return date

def resolve_days(input_days, *exclusion_tests):
	"""
	Given an iterable of days, exclude any days that pass any exclusion test.
	Exclusion tests should take a datetime.date object and return a boolean
	if the date should be excluded.
	"""
	exclusions = lambda day: any(test(day) for test in exclusion_tests)
	dates = map(always_date, input_days)
	return itertools.filterfalse(exclusions, dates)

def month_days(input):
	"""
	Yield each day of a month indicated by the input month, such as 'May' or
	'December' or 'Dec'.
	"""
	start = dateutil.parser.parse(input).replace(day=1)
	end = start + rd.relativedelta(months=1)
	return date_range(start, end)
