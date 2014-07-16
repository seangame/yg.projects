import urllib.parse
import datetime
import json

import yg.netsuite as ns

environment = 'production'

script_ids = {
	'production': 560,
	'sandbox': 566,
	'SB4': 526, # note, SB4 doesn't have Resource Allocations
	'SB6': 562,
}

script_id = script_ids[environment]

if environment != 'production':
	ns.Sandbox.use()

res_alloc_tmpl = '/app/site/hosting/restlet.nl?script={script_id}&deploy=1'
res_alloc_path = res_alloc_tmpl.format(**locals())
url = urllib.parse.urljoin(ns.root, res_alloc_path)

cred = ns.Credential()
if environment.startswith('SB'):
	cred.use_admin(environment)
else:
	cred.use_admin()
cred.install()

# allocate 50 percent time from Jun 1 through Jul 31, 2014
# for Jason (271374) to Gryphon (270907)
alloc = dict(
	amount=50,
	resource_id=271374,
	type="2", # soft (use "1" for hard)
	unit="P", # percent (use "H" for hours)
	project_id=270907,
	start_date=ns.NetSuite.format_date(datetime.date(2014,6,1)),
	end_date=ns.NetSuite.format_date(datetime.date(2014,7,31)),
)

resp = ns.session.post(url, data=json.dumps(alloc))
resp.raise_for_status()
