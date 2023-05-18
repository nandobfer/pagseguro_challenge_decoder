import requests, json

client = input('client name: ')
cert = json.load(open(f'certificates/{client}.json'))

url = "https://api.pagseguro.com/oauth2/application"

payload = {"name": client}
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {cert['token']}",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

application = json.loads(response.text)
print(application)

cert['application'] = application

with open(f'certificates/{client}.json', 'w') as file:
    json.dump(cert, file, indent=4)