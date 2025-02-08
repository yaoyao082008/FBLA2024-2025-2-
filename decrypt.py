from cryptography.fernet import Fernet

with open('cred.key','rb') as mykey:
    key = mykey.read()

f = Fernet(key)


with open('encrypted.json','rb') as encryptedFile:
    encrypted = encryptedFile.read()

decrypted=f.decrypt(encrypted)

with open('dec_creds.json','wb') as decryptedFile:
    decryptedFile.write(decrypted)