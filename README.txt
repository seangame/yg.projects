yg.projects
===========

yg.projects is a Python library representing the YouGov project management
models. The library includes support for time accounting, NetSuite
interaction, and calendars.

Timesheet Entry
===============

yg.projects facilitates most of the heavy lifting involved with timesheet
entry. Here is an example script leveraging yg.projects for entering time on
two projects in a 60/40 distribution::

    import datetime

    from yg.projects import models
    import yg.projects.commands as cmds

    class TimeEntry(cmds.TimeEntry):
        @classmethod
        def get_distribution(cls, projects):
            dist = models.Distribution()
            dist[projects.Gryphon]=6
            dist[projects.Datum]=4
            return dist

        def is_vacation(date):
            return date in [
                datetime.date(2014,4,17),
                datetime.date(2014,4,18),
            ]

        exclusions = cmds.TimeEntry.exclusions + (is_vacation,)

    if __name__ == '__main__':
        TimeEntry.run()

One must download a `CSV report of projects
<http://yg-public.s3.amazonaws.com/r/13/projects.csv>`_ to './projects.csv'.

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

Note that this routine should be used with care. It can create hundreds of
time entries in a few minutes. As of yet, there is no way to easily remove
erroneous entries, so do use this technique with caution. Also, please be
careful to always enter your time accurately, such that it reflects the
number of hours actually worked on a given project.
