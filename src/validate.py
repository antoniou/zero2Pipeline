import boto3

from config import Config
from stack import Stack
from sys_args import SysArgs

def main():
    c = Config('n/a', SysArgs().get('RESOURCE', 1), SysArgs().get('APPLICATION', 2))

    s = Stack(c.stack_name(),
                boto3.client('cloudformation'),
                boto3.resource('cloudformation'))
    s.validate(c.cf_template())

if __name__ == "__main__":
    main()
