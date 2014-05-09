import yg.netsuite
import requests
cred = yg.netsuite.Credential()
headers={'Content-Type': 'application/json'}
headers.update(cred.build_auth_header())
url = 'https://rest.netsuite.com/app/site/hosting/restlet.nl?script=533&deploy=1'
session = requests.session()
resp = session.get(url, headers=headers)
print(resp.ok)
print(resp.status_code)
print(resp.text)
