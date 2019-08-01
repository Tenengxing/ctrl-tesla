#! /usr/bin/env python3

import requests

TESLA_CLIENT_ID="81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384"
TESLA_CLIENT_SECRET="c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3"
TESLA_BASE_URL="https://owner-api.teslamotors.com/"

def main():
	session = requests.session()
	resp = session.post(TESLA_BASE_URL+"oauth/token?grant_type=password", data={
			"grant_type": "password",
			"client_id": TESLA_CLIENT_ID,
			"client_secret": TESLA_CLIENT_SECRET,
			"email": "guafeng@fmit.cn",
			"password": "-",
		})
	print("http code:", resp.status_code)
	print(resp.json())


if __name__ == '__main__':
    main()
