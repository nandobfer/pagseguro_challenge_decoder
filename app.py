from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from datetime import datetime
import base64, requests, json, os

class Challenge():
    def __init__(self, challenge) -> None:
        self.coded = challenge['challenge']
        self.token = challenge['access_token']
        self.decoded = self.decodeChallenge(challenge)
        self.key = RSA.importKey(input('private key: '))
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
        print('\ngetting keys')
        print(datetime.now())
        response = requests.post("https://api.pagseguro.com/certificates", headers={
            'Authorization': f'Bearer {self.token}',
            'X_CHALLENGE': str(self.message)
        })
        return json.loads(response.text)
        
        
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

loja = input('loja: ')
token = input('token: ')
challenge = getChallenge(token)

handler = Challenge(challenge)

keys = handler.getKeys()

print(f'saving keys at certificate/`{loja}.json`')
try:
    json.dump(keys, open(f'certificates/{loja}.json', 'w'), indent = 4)
    print('success')
except Exception as error:
    print(error)
    
