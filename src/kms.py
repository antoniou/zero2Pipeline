from boto3 import client
import base64

class KMS:
    def __init__(self, key_id=None):
        self.client = client('kms')
        self.key_id = key_id

    def encrypt(self, file, out='encryptedfile'):
        print ("Encrypting file '{0}' to '{1}'".format(file, out))
        res = self.client.encrypt(
            KeyId=self.key_id,
            Plaintext=open(file, 'r').read()
        )

        o = open(out, 'wb').write(res['CiphertextBlob'])

    def decrypt(self, file, out='decryptedfile'):
        print ( "Decrypting file '{0}' to '{1}'".format(file, out))
        res = self.client.decrypt(
            CiphertextBlob=open(file, 'rb').read()
        )

        o = open(out, 'wb').write(res['Plaintext'])
