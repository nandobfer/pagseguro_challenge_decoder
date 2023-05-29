import requests, json

client = input('client name: ')
cert = json.load(open(f'certificates/{client}.json'))

url = cert['url']+"/oauth2/authorize/sms"

payload = {"email": 'teste@sandbox.pagseguro.com.br'}
# payload = {"email": cert['email']}
headers = {
    # "accept": "application/json",
    "X_CLIENT_ID": cert['application']['client_id'],
    "X_CLIENT_SECRET": cert['application']['client_secret'],
    "Authorization": f"Bearer {cert['token']}",
    "content-type": "application/json",
    'User-Agent': 'python-requests/2.27.1',
    'Accept-Encoding': 'gzip, deflate, br',
}

response = requests.post(url, json=payload, headers=headers)

authorization = json.loads(response.text)
print({"headers":response.request.headers})
print()
print({"body":response.request.body})
print()
print({"response":authorization})

cert['authorization'] = authorization

with open(f'certificates/{client}.json', 'w') as file:
    json.dump(cert, file, indent=4)