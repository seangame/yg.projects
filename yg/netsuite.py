import os
import itertools
import json
import decimal
import getpass
import logging
import urllib.parse
import datetime
import argparse

import dateutil.parser
import requests
import keyring

log = logging.getLogger()

root = 'https://rest.netsuite.com'
ns_url = lambda path: urllib.parse.urljoin(root, path)
system = "NetSuite"

session = requests.session()
session.headers = {'Content-Type': 'application/json'}


class Sandbox:
	@classmethod
	def offer(cls, parser):
		"""
		Given an argparse parser, add a --sandbox parameter which enables the
		sandbox.
		"""
		class SandboxAction(argparse.Action):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, nargs=0, **kwargs)

			def __call__(self, *args, **kwargs):
				cls.use()

		parser.add_argument('--sandbox', action=SandboxAction)

	@staticmethod
	def use():
		global system, root
		system += ' Sandbox'
		root = root.replace('rest.netsuite', 'rest.sandbox.netsuite')


class NetSuite:
	"""
	Common NetSuite functionality
	"""
	@staticmethod
	def default_encode(o):
		"""
		Encode decimals as strings
		"""
		if isinstance(o, decimal.Decimal):
			return str(o)

	@classmethod
	def handle_response(cls, resp):
		if not resp.ok:
			raise NetsuiteFailure(resp.json())
		if resp.headers['Content-Type'].startswith('text/html'):
			raise NetsuiteFailure("Unexpected HTML response")
		if not resp.text:
			# empty response, likely from a DELETE or PUT
			return
		data = resp.json()
		if isinstance(data, dict) and data.get('status') == 'fail':
			raise NetsuiteFailure(data['message'])
		return data

	@staticmethod
	def format_date(date):
		"""
		Render a datetime.date as a Javascript Date()
		Note that NetSuite doesn't appear to support ISO-8601
		date formats, so use the only format known to work.

		>>> NetSuite.format_date(datetime.date(2014, 5, 14))
		'May 14, 2014'
		>>> NetSuite.format_date(datetime.date(2014, 12, 14))
		'December 14, 2014'
		"""
		return date.strftime('%B %d, %Y')

	@classmethod
	def param_url(cls, **data):
		params = urllib.parse.urlencode(data)
		return '&'.join([cls.restlet, params])


class Credential(NetSuite):
	path = '/rest/roles'
	roles_auth = 'NLAuth nlauth_email={email}, nlauth_signature={password}'
	auth_template = ("NLAuth nlauth_account={account}, nlauth_email={email}, "
			"nlauth_signature={password}, nlauth_role={role}")

	def __init__(self):
		self.email = os.environ.get('NETSUITE_EMAIL', None) or input("email> ")
		password = keyring.get_password(system, self.email)
		if not password:
			password = getpass.getpass()
			assert password
			keyring.set_password(system, self.email, password)
		self.password = password

	def is_suitable_role(self, role):
		"""
		Return true for roles suitable for this credential purpose. For
		timesheets, we want the Employee Centre or Employee Center Multi-Sub.
		"""
		return role['role']['name'].startswith('Employee Cent')

	def find_best_role(self):
		roles = self.load_roles()
		role = next(filter(self.is_suitable_role, roles), None)
		if not role:
			print("No suitable role")
			raise SystemExit(1)
		self.account = role['account']['internalId']
		self.role = role['role']['internalId']

	def use_admin(self):
		roles = self.load_roles()
		is_admin = lambda role: role['role']['name'] == 'Administrator'
		role, = filter(is_admin, roles)
		self.account = role['account']['internalId']
		self.role = role['role']['internalId']

	def load_roles(self):
		headers=dict(Authorization=self.roles_auth.format(**vars(self)))
		resp = session.get(ns_url(self.path), headers=headers)
		try:
			return self.handle_response(resp)
		except NetsuiteFailure as exc:
			exc.on_password_fail(self.reset_password)
			raise

	def reset_password(self, failure):
		print("password was rejected")
		password = getpass.getpass("new password> ")
		if not password:
			return
		keyring.set_password(system, self.email, password)
		print("password changed.")

	def build_auth_header(self):
		if not 'role' in vars(self):
			self.find_best_role()
		return dict(Authorization=self.auth_template.format(**vars(self)))

	def install(self):
		"""
		Install self into the session
		"""
		session.headers.update(self.build_auth_header())


class Entry:
	date = datetime.date.today()
	"Date of the entry"

	customer = ""
	"something like SmartTech : Test Project 005"

	memo = ""

	case_task_event = ""
	"something like 'Test Task 0005 (Task)'"

	hours = 0
	"decimal.Decimal or int"

	def __init__(self, **kwargs):
		vars(self).update(kwargs)

	@property
	def json(self):
		"""
		customer is something like "SmartTech : Test Project 005"
		hours should be a decimal.Decimal or int.
		"""
		return dict(
			trandate=self.trandate,
			customer=self.customer,
			casetaskevent=self.case_task_event,
			hours=self.hours,
			memo=self.memo,
		)

	@property
	def trandate(self):
		"""
		The transaction date formatted for NetSuite.
		"""
		return NetSuite.format_date(self.date)

	@classmethod
	def solicit(cls):
		date_input = input("Date (blank to end)> ")
		if not date_input:
			return
		date = dateutil.parser.parse(date_input).date()
		customer = input("Customer> ")
		case = input("Case/Task/Event> ")
		hours = decimal.Decimal(input("Hours> "))
		memo = input("Memo (optional)> ")
		return cls(date=date, customer=customer, case_task_event=case,
			hours=hours, memo=memo)

	def __repr__(self):
		return repr(vars(self))

class NetsuiteFailure(Exception):
	def on_password_fail(self, callback):
		message = self.args[0]
		err_msg = message['error']['message']
		if 'invalid email address or password' in err_msg:
			callback(self)

class TimeBill(NetSuite, list):
	"""
	List of entries
	"""
	restlet = '/app/site/hosting/restlet.nl?script=522&deploy=1'

	@property
	def json(self):
		return dict(timebill=[entry.json for entry in self])

	@classmethod
	def solicit(cls):
		raw_entries = (Entry.solicit() for n in itertools.count())
		entries = itertools.takewhile(bool, raw_entries)
		return cls(entries)

	def submit(self):
		log.info("Submitting %s entries.", len(self))
		data = json.dumps(self.json, default=self.default_encode)
		resp = session.post(ns_url(self.restlet), data=data)
		return self.handle_response(resp)

	@classmethod
	def clear_for_date(cls, date, cred=None):
		log.info("Deleting timesheets for %s.", date)
		path = cls.param_url(date=cls.format_date(date))
		resp = session.get(ns_url(path))
		items = cls.handle_response(resp) or []
		for item in items:
			cls.delete_item(item)

	@classmethod
	def delete_item(cls, search_res):
		path = cls.param_url(id=search_res['id'])
		resp = session.delete(ns_url(path))
		return cls.handle_response(resp)
