import urllib.parse
import datetime
import json

import yg.netsuite as ns

ns.Sandbox.use()

res_alloc_path = '/app/site/hosting/restlet.nl?script=562&deploy=1'
url = urllib.parse.urljoin(ns.root, res_alloc_path)

cred = ns.Credential()
cred.use_admin('SB6')
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
