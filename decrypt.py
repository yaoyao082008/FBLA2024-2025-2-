# module imports
from cryptography.fernet import Fernet

# open key
with open('cred.key','rb') as mykey:
    key = mykey.read()

# initialize decryption
f = Fernet(key)

# open encrypted credentials
with open('encrypted.json','rb') as encryptedFile:
    encrypted = encryptedFile.read()

# decrypt credentials
decrypted = f.decrypt(encrypted)

# save decrupted credentials
with open('dec_creds.json','wb') as decryptedFile:
    decryptedFile.write(decrypted)