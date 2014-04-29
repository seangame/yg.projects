import csv
import itertools

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

	def __lt__(self, other):
		return self.name < other.name and len(self.name) < len(other.name)

class Projects(list):
	@classmethod
	def from_csv(cls, filename='projects.csv'):
		with open('projects.csv') as stream:
			return cls(map(Project.from_dict, csv.DictReader(stream)))

	def best(self, short_name):
		return next(
			project
			for project in sorted(self)
			if short_name in project.name
		)
	__getattr__ = best

class Distribution(dict):
	"""
	Provides an overriding distribution

	>>> d = Distribution()
	>>> d['foo'] = 2
	>>> d['bar'] = 1
	foo's portion is 2/3 at a resolution of 1/10
	>>> d.portion('foo')
	Decimal('0.7')
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
