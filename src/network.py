import os
import boto3

from config import Config
from stack import Stack
from sys_args import SysArgs

def main():
    application = SysArgs().get('APPLICATION', 1)
    c = Config(os.environ['ENVIRONMENT'], 'network', application)

    s = Stack(c.stack_name(),
                boto3.client('cloudformation'),
                boto3.resource('cloudformation'))
    s.apply(c.cf_template(), c.cf_parameters())

if __name__ == "__main__":
    main()
