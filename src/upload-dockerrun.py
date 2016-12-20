from template import Template
from s3_bucket import S3Bucket
from zipfile import ZipFile
from sys_args import SysArgs

import boto3
import os
from os.path import basename

def zip_file(file, data, lookin):
    with ZipFile(file, 'w') as config_zip:
        config_zip.writestr('Dockerrun.aws.json', data)

        for root, dirs, files in os.walk(lookin):
            for f in files:
                config_zip.write(os.path.join(root, f), \
                    ".ebextensions/{0}".format(f))
    return config_zip

if __name__ == "__main__":
    application = SysArgs().get('APPLICATION', 1)
    attributes = {
        'app_version': SysArgs().get("APP_VERSION" , 2),
        'aws_account': os.environ['AWS_ACCOUNT'],
        'aws_region': os.environ['AWS_DEFAULT_REGION'],
        'image_name': "smbc/{0}".format(application)
    }

    s3_config_bucket = 'elasticbeanstalk-smbc-dockerrun'
    if 'S3_CONFIG_BUCKET' in os.environ:
        s3_config_bucket = os.environ['S3_CONFIG_BUCKET']

    file = "ebconfig-{0}.zip".format(attributes['app_version'])
    data = Template("{0}/Dockerrun.aws.json.j2".format(application)) \
            .render(attributes)
    lookin = "beanstalk/{0}/.ebextensions".format(application)
    filename = zip_file(file, data, lookin).filename
    S3Bucket(boto3.resource('s3'), s3_config_bucket) \
        .upload(filename, "{0}/{1}".format(application, filename))
