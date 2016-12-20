from kms import KMS
from s3_bucket import S3Bucket
from shutil import copyfile
import boto3
import os
from sys_args import SysArgs
from secrets_repo import SecretsRepo

if __name__ == "__main__":
    attributes = {
        'environment': os.environ['ENVIRONMENT'],
        'key_id': os.environ['KMS_KEY_ID']
    }

    application = SysArgs().get('APPLICATION', 1)
    s3_config_bucket = "smbs-application-config".format(application)

    file = "appsettings.{0}.secrets.json".format(attributes['environment'])
    encrypted_file = "{0}.encrypted".format(file)
    KMS(attributes['key_id']).encrypt(file, encrypted_file)
    print ("Removing unencrypted file {0}".format(file))
    os.remove(file)
    print ("Uploading file {0}".format(encrypted_file))
    S3Bucket(boto3.resource('s3'), s3_config_bucket) \
        .upload(encrypted_file, "{0}/{1}".format(application,encrypted_file))
    final_encrypted_file="{0}/{1}".format(SecretsRepo().application(application).get(), encrypted_file)
    print ("Moving encrypted file to {0}".format(final_encrypted_file))
    copyfile(encrypted_file, final_encrypted_file)
    os.remove(encrypted_file)
