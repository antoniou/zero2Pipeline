import os
import boto3

from config import Config
from stack import Stack
from sys_args import SysArgs


def main():
    application =  SysArgs().get('APPLICATION', 1)
    c = Config(os.environ['ENVIRONMENT'], 'beanstalk', application)
    c.add_cf_parameter('Application', application)
    c.add_cf_parameter('Environment', os.environ['ENVIRONMENT'])
    # c.add_cf_parameter('AppVersion', SysArgs().get('APP_VERSION', 2))

    if 'S3_CONFIG_BUCKET' in os.environ:
        bucket = os.environ['S3_CONFIG_BUCKET']
        c.add_cf_parameter('S3ConfigBucketName', bucket)

    s = Stack(c.stack_name(), boto3.client('cloudformation'), boto3.resource('cloudformation'))
    s.apply(c.cf_template(), c.cf_parameters())


if __name__ == "__main__":
    main()
