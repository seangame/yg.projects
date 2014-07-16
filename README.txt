yg.projects
===========

yg.projects is a Python library representing the YouGov project management
models. The library includes support for time accounting, NetSuite
interaction, and calendars.

This project requires Python 3.

Timesheet Entry
===============

yg.projects facilitates most of the heavy lifting involved with timesheet
entry. Here is an example script leveraging yg.projects for entering time on
two projects in a 60/40 distribution::

    # enter-time.py
    import datetime

    from yg.projects import models
    import yg.projects.commands as cmds
    from yg.projects import calendar

    class MyCalendar(calendar.YouGovAmericaCalendar):
        vacation_days = (
            datetime.date(2014, 4, 17),
            datetime.date(2014, 4, 18),
        )

    class TimeEntry(cmds.TimeEntry):
        calendar = MyCalendar()

        @classmethod
        def get_project_distribution(cls, projects):
            dist = models.Distribution()
            dist[projects.Gryphon]=6
            dist[projects.Datum]=4
            return dist

    if __name__ == '__main__':
        TimeEntry.run()

Then, the script could be invoked as so::

    python enter-time.py apr

The call to 'tb.submit()' will trigger a login, which will prompt for the
e-mail address and password, the latter of which will subsequently be saved
in a keyring.

The script will create timesheet entries of 8 hours per day for each weekday
in the month of April, excluding (US) holidays and the two days indicated as
vacation. It will allocate those 8 hours in a ratio of 6:4 Gryphon:Datum. It
will submit the time entries to the "Sandbox" instance of NetSuite unless
--prod is passed.

With great power comes great responsibility. Please be
careful to always enter your time accurately, such that it reflects the
number of hours actually worked on a given project.

Removing Entries
================

``yg.projects`` provides a relatively easy way to remove unwanted entries.
If you've used something like enter-time.py above to add entries
programmatically, but then found that you made a mistake or the entries did
not populate properly, here is how you might clear those entries::

    import yg.projects.calendar
    import yg.netsuite
    yg.netsuite.Credential().install()
    days = yg.projects.calendar.month_days('Dec')
    for day in days:
        yg.netsuite.TimeBill.clear_for_date(day)

Developing
==========

``timesheet.js``, while developed here, must be uploaded to NetSuite for
the updates to take effect. Only certain users (Nitin, Jason) have access to
do this, so ask them for help.

Tests may be easily run using pytest-runner::

    python setup.py ptr
