from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from datetime import datetime
import base64, requests, json, os, sys

class Challenge():
    def __init__(self, challenge, key) -> None:
        self.coded = challenge['challenge']
        self.token = challenge['access_token']
        self.decoded = self.decodeChallenge(challenge)
        self.key = RSA.importKey(decodePrivateKey(key))
        self.cipher = PKCS1_OAEP.new(self.key, hashAlgo=SHA256)
        self.message = self.decryptChallenge()
        
    def decodeChallenge(self, coded):
        print("decoding challenge")
        decoded = base64.b64decode(self.coded)

        return decoded
    
    def decryptChallenge(self):
        print("decrypting challenge")
        decrypted = self.cipher.decrypt(self.decoded).decode()

        return decrypted
        
    def getKeys(self):
        print('getting keys')
        print(datetime.now())
        response = requests.post(f"{url}/certificates", headers={
            'Authorization': f'Bearer {self.token}',
            'X_CHALLENGE': str(self.message)
        })
        return json.loads(response.text)
        

def decodePrivateKey(key):
    key = key.split('-----BEGIN PRIVATE KEY-----')[1]
    key = key.split('-----END PRIVATE KEY-----')[0]
    return base64.b64decode(key)
        
def getChallenge(token):
    print("getting challenge")
    response = requests.post(f"{url}/oauth2/token", headers={
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',

    }, json={
        "grant_type": "challenge",
        "scope": "certificate.create"
    })
    print(f"challenge generated at {datetime.now()}")

    return json.loads(response.text)

def generateKeys(api):
    print('verificando chaves')
    url = f"{api}/pagseguro/new_keys"
    print(url)
    response = requests.get(url)
    print(response.text)
    data = json.loads(response.text)
    
    if 'new' in data:
        print(f"nenhuma chave encontrada, gerando agora")
        print(f"\nchave privada armazenada e pública disponilizada na url:")
        print(data['url'])
        input("\nAPÓS inserir a url no site da pagseguro, pressione enter")
    else:
        print("\nchaves já criadas, insera a url no site:")
        print(data['url'])
        input("\nAPÓS inserir a url no site da pagseguro, pressione enter")

    return data['keys']

sandbox = sys.argv[1] == '--sandbox' if len(sys.argv) > 1 else False
url = "https://sandbox.api.pagseguro.com" if sandbox else "https://api.pagseguro.com"

port = input('api port: ')
api = f"https://app.agenciaboz.com.br:{port}/api"
input(f"{api} ?")
client_name = input('client name: ')
# api = "http://localhost:4001"
token = input('token: ')

keys = generateKeys(api)

challenge = getChallenge(token)

handler = Challenge(challenge, keys['private'])


pagseguro_keys = handler.getKeys()
pagseguro_keys['api'] = api
pagseguro_keys['token'] = token
pagseguro_keys['url'] = url

print(f'\nsaving keys at certificate/`{client_name}.json`')
try:
    json.dump(pagseguro_keys, open(f'certificates/{client_name}.json', 'w'), indent = 4)
    print('success')
except Exception as error:
    print(error)
    
