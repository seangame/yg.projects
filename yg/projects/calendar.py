"""
YouGov calendar modules
"""

import datetime
import sys
import itertools

import workalendar.america
import workalendar.europe
from workalendar.core import Holiday
import dateutil.parser
import dateutil.relativedelta as rd


class Vacation:
    """
    Mix-in for vacation_support
    """
    vacation_days = ()

    def is_working_day(self, day, *args, **kwargs):
        parent_res = super().is_working_day(day, *args, **kwargs)
        return parent_res and not self.is_vacation(day)

    def is_vacation(self, day):
        return day in self.vacation_days


class YouGovAmericaCalendar(Vacation, workalendar.america.UnitedStates):
    include_corpus_christi = False
    hours_per_day = 8

    FIXED_HOLIDAYS = workalendar.america.UnitedStates.FIXED_HOLIDAYS + (
        Holiday(
            datetime.date(2000, 12, 24), "Christmas Eve",
            indication="December 24",
            observance_shift=dict(weekday=rd.FR(-1)),
        ),
        Holiday(
            datetime.date(2000, 12, 31), "New year's eve",
            indication="December 31",
            observance_shift=dict(weekday=rd.FR(-1)),
        ),
    )

    def _add_days(self, year):
        tg = datetime.date(year, 11, 1) + rd.relativedelta(weekday=rd.TH(4))
        yield Holiday(
            tg + datetime.timedelta(days=1),
            "Day after Thanksgiving",
            indication="Friday after Thanksgiving",
        )

    def _remove_days(self, days):
        """
        Remove days found in the US calendar not recognized by YG
        """
        to_remove = ['Colombus Day', 'Inauguration Day', 'Veterans Day']
        return (
            day for day in map(Holiday._from_resolved_definition, days)
            if not day.name in to_remove
        )

    def get_variable_days(self, year):
        days = super().get_variable_days(year)
        return list(itertools.chain(days, self._add_days(year)))

    def get_calendar_holidays(self, year):
        days = super().get_calendar_holidays(year)
        days = self._remove_days(days)
        return list(days)


class YouGovCalendar(Vacation, workalendar.europe.UnitedKingdom):
    hours_per_day = 7.5

    # todo: implement actual YouGov UK holidays


def print_holidays(cal=None):
    cal = cal or YouGovAmericaCalendar()
    year = int(sys.argv[1])
    print("= Holidays {year} =".format(**vars()), end='\n\n')

    print("|| '''Holiday''' || '''Day Indicated''' || '''Day Observed''' ||")
    for holiday in cal.holidays(year):
        holiday.observed = cal.get_observed_date(holiday)
        if not hasattr(holiday, 'indication'):
            holiday.indication = 'unknown'
        print("|| {holiday.name} || {holiday.indication} || "
            "{holiday.observed:%A, %B %d} ||".format(**vars()))

class DateRange:
    """
    >>> start = datetime.date(2014, 5, 16)
    >>> end = datetime.date(2014, 5, 17)
    >>> list(DateRange(start, end))
    [datetime.date(2014, 5, 16)]
    """
    def __init__(self, start, end):
        assert isinstance(start, datetime.date)
        assert isinstance(end, datetime.date)
        self.start = start
        self.end = end

    def __iter__(self):
        days = self._days_from(self.start)
        return itertools.takewhile(self.__contains__, days)

    @staticmethod
    def _days_from(day):
        one_day = datetime.timedelta(days=1)
        while True:
            yield day
            day += one_day

    def __contains__(self, date):
        return self.start <= date < self.end

date_range = DateRange
"alias for compatibility"


def month_days(input):
    """
    Yield each day of a month indicated by the input month, such as 'May' or
    'December' or 'Dec'.
    >>> days = month_days('May')

    days should be iterable
    >>> hasattr(days, '__iter__')
    True

    >>> days = list(days)
    >>> len(days)
    31

    >>> days[0].day
    1
    >>> days[-1].day
    31

    >>> days[0].year == datetime.date.today().year
    True

    >>> isinstance(days[0], datetime.date)
    True
    """
    start = dateutil.parser.parse(input).replace(day=1).date()
    end = start + rd.relativedelta(months=1)
    return DateRange(start, end)

if __name__ == '__main__':
    print_holidays()
