from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from datetime import datetime
import base64, requests, json, os

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
        response = requests.post("https://api.pagseguro.com/certificates", headers={
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
    response = requests.post("https://api.pagseguro.com/oauth2/token", headers={
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',

    }, json={
        "grant_type": "challenge",
        "scope": "certificate.create"
    })
    print(f"challenge generated at {datetime.now()}")

    return json.loads(response.text)

def generateKeys(loja, api):
    print('verificando chaves')
    
    response = requests.post(f"{api}/api/v1/bapka/mottu/pagseguro/new_keys", json={"loja": loja})
    data = json.loads(response.text)
    
    if 'url' in data:
        print(f"nenhuma chave encontrada para a loja {loja}, gerando agora")
        print(f"\nchave privada armazenada e pública disponilizada na url:")
        print(data['url'])
        input("\nAPÓS inserir a url no site da pagseguro, pressione enter")
    else:
        print("chaves já criadas, insera a url no site:")
        print(data['url'])
        input("\nAPÓS inserir a url no site da pagseguro, pressione enter")

    return data['keys']

api = "http://app.agenciaboz.com.br:4001"
# api = "http://localhost:4001"
loja = input('loja: ')
token = input('token: ')

keys = generateKeys(loja, api)

challenge = getChallenge(token)

handler = Challenge(challenge, keys['private'])

pagseguro_keys = handler.getKeys()

print(f'\nsaving keys at certificate/`{loja}.json`')
try:
    json.dump(pagseguro_keys, open(f'certificates/{loja}.json', 'w'), indent = 4)
    print('success')
except Exception as error:
    print(error)
    
