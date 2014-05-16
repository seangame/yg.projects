import itertools
import json
import decimal
import getpass
import logging
import urllib.parse
import datetime

import dateutil.parser
import requests
import keyring

log = logging.getLogger()

root = 'https://rest.netsuite.com'
ns_url = lambda path: urllib.parse.urljoin(root, path)
system = "NetSuite"

def use_sandbox():
	global system, root
	system += ' Sandbox'
	root = root.replace('rest.netsuite', 'rest.sandbox.netsuite')

session = requests.session()


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

	def handle_response(self, resp):
		if not resp.ok:
			raise NetsuiteFailure(resp.json())
		data = resp.json()
		if isinstance(data, dict) and data.get('status') == 'fail':
			raise NetsuiteFailure(data['message'])
		return data

class Credential(NetSuite):
	path = '/rest/roles'
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
		The transaction date formatted for a Javascript Date()

		>>> entry = Entry(date=datetime.date(2014, 5, 14))
		>>> entry.trandate
		'2014-05-14'
		"""
		return self.date.strftime('%Y-%m-%d')

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
		headers = {
			'Content-Type': 'application/json',
		}
		cred = Credential()
		headers.update(cred.build_auth_header())
		data = json.dumps(self.json, default=self.default_encode)
		resp = session.post(ns_url(self.restlet), headers=headers, data=data)
		return self.handle_response(resp)
