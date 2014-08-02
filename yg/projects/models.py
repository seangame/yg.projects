import re
import csv
import itertools
import urllib.parse

import requests

import yg.netsuite

class Project:
    def __init__(self, **params):
        vars(self).update(params)

    @classmethod
    def from_dict(cls, d):
        d = {key.lower().replace(' ', '_'): val for key, val in d.items()}
        return cls(**d)

    def __repr__(self):
        return ' '.join((self.id, self.name))

class Projects(list):
    root = 'https://yg-public.s3.amazonaws.com/'
    projects_loc = '/r/13/AllProjectswithTasksResults192.csv'

    @classmethod
    def from_csv(cls, filename='projects.csv'):
        with open(filename) as stream:
            return cls(map(Project.from_dict, csv.DictReader(stream)))

    @classmethod
    def from_url(cls, url=projects_loc):
        url = urllib.parse.urljoin(cls.root, url)
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        lines = resp.iter_lines(decode_unicode=True)
        return cls(map(Project.from_dict, csv.DictReader(lines)))

    def best(self, short_name):
        """
        Return the best project for the supplied name

        Consider this list of projects:

        >>> ps = Projects([
        ...     Project(name='Gryphon', id='a'),
        ...     Project(name='Gryphon 4', id='b'),
        ...     Project(name='A Gryphon project', id='c'),
        ...     Project(name='anon project with long name', id='d')
        ... ])

        Regardless of the order the projects are defined,
        >>> import random
        >>> random.shuffle(ps)

        An exact match always matches first,
        >>> ps.best('Gryphon')
        a Gryphon
        >>> ps.best('Gryphon 4')
        b Gryphon 4

        Shorter matches always take precedence,
        >>> ps.best('Gryph')
        a Gryphon

        >>> ps.best('A Gryphon')
        c A Gryphon project

        And an ambiguous match should prefer the one that matches earliest.
        >>> ps.best('project')
        d anon project with long name
        """
        expression_tmpls = (
            '^{short_name}$', # exact
            '^{short_name}', # initial
            '{short_name}', # contains
        )
        # capture the local vars because a generator expression cannot reach
        #  the variables in this scope
        l_vars = locals()
        expressions = (tmpl.format_map(l_vars) for tmpl in expression_tmpls)
        name_length = lambda p: len(p.name)
        matches = (
            project
            # important: loop over expressions first
            for expression in expressions
            for project in sorted(self, key=name_length)
            if re.search(expression, project.name)
        )
        return next(matches)
    __getattr__ = best

class Distribution(dict):
    """
    Provides an overriding distribution

    >>> d = Distribution()
    >>> d['foo'] = 2
    >>> d['bar'] = 1

    foo's portion is 2/3 at a resolution of 1/10
    >>> d.portion('foo', 1.0)
    0.7

    >>> import datetime
    >>> days = [datetime.date.today()]
    >>> tb = d.create_timebill(days, hours=11)
    >>> len(tb)
    2
    >>> foo_entry = next(entry for entry in tb if entry.customer == 'foo')
    >>> foo_entry.hours
    7.3

    """
    # 1/10 resolution
    resolution = 10

    @property
    def total(self):
        return sum(self.values())

    def portion(self, key, value):
        ratio = self[key] / self.total
        portion = ratio*value
        return round(portion*self.resolution)/self.resolution

    def create_timebill(self, days, hours=9):
        """
        Given a distribution of projects, apply that distribution to the
        hours, returning a TimeBill of entries for each day in days.
        """
        return yg.netsuite.TimeBill(
            yg.netsuite.Entry(
                date=day,
                customer=str(proj),
                hours=self.portion(proj, hours),
            )
            for day, proj in itertools.product(days, self)
        )
