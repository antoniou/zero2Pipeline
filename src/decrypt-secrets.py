from kms import KMS
from s3_bucket import S3Bucket
from optparse import OptionParser
import boto3
import os
from sys_args import SysArgs
from secrets_repo import SecretsRepo

if __name__ == "__main__":

    application = SysArgs() \
        .arg_name('APPLICATION') \
        .arg_number(1) \
        .get_value()

    sub_app = SysArgs() \
        .arg_name('SUB_APPLICATION') \
        .arg_number(2) \
        .fail_if_notfound(False) \
        .get_value()

    file = "appsettings.{0}.secrets.json" \
        .format(os.environ['ENVIRONMENT'])
    secrets_repo = SecretsRepo() \
            .application(application) \
            .sub_application(sub_app) \
            .get()

    encrypted_file = "{0}/{1}.encrypted".format(secrets_repo,file)

    KMS().decrypt(encrypted_file, file)
    print("'{0}' ready to be updated.".format(file))
