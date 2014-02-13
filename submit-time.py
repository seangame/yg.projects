import itertools
import json
import decimal
import getpass
import logging
import argparse
import urllib.parse
import pprint
import datetime

import jaraco.util.logging
import dateutil.parser
import requests
import keyring

log = logging.getLogger()

root = 'https://rest.netsuite.com'
ns_url = lambda path: urllib.parse.urljoin(root, path)
system = "NetSuite"

use_sandbox = True
if use_sandbox:
	# use sandbox
	system += ' Sandbox'
	root = root.replace('rest.netsuite', 'rest.sandbox.netsuite')

session = requests.session()


class Credential(object):
	roles_url = ns_url('/rest/roles')
	roles_auth = 'NLAuth nlauth_email={email}, nlauth_signature={password}'
	auth_template = ("NLAuth nlauth_account={account}, nlauth_email={email}, "
			"nlauth_signature={password}, nlauth_role={role}")

	def __init__(self):
		self.email = input("email> ")
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

	def load_roles(self):
		headers=dict(Authorization=self.roles_auth.format(**vars(self)))
		resp = session.get(self.roles_url, headers=headers)
		resp.raise_for_status()
		return resp.json()

	def build_auth_header(self):
		if not 'role' in vars(self):
			self.find_best_role()
		return dict(Authorization=self.auth_template.format(**vars(self)))


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

	@classmethod
	def json(self):
		"""
		customer is something like "SmartTech : Test Project 005"
		hours should be a decimal.Decimal or int.
		"""
		return dict(
			trandate=self.date.strftime('%d/%m/%Y'),
			customer=self.customer,
			casetaskevent=self.case_task_event,
			hours=self.hours,
			memo=self.memo,
		)

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

class NetsuiteFailure(Exception):
	pass

class NetSuite:
	@staticmethod
	def default_encode(o):
		"""
		Encode decimals as strings
		"""
		if isinstance(o, decimal.Decimal):
			return str(o)

	def handle_response(self, data):
		if data.get('status') == 'failure':
			raise NetsuiteFailure(data['message'])
		return data

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
		log.info("Submitting", len(self), "entries.")
		headers = {
			'Content-Type': 'application/json',
		}
		cred = Credential()
		headers.update(cred.build_auth_header())
		data = json.dumps(self.json, default=self.default_encode)
		resp = session.post(ns_url(self.restlet), headers=headers, data=data)
		resp.raise_for_status()
		return self.handle_response(resp.json())

def run():
	TimeBill.solicit().submit()

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

def handle_command_line():
	args = get_args()
	jaraco.util.logging.setup(args, format="%(message)s")
	setup_requests_logging(args.log_level)
	run()

if __name__ == '__main__':
	handle_command_line()
