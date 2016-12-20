import os
import re
from boto3 import client
from sys_args import SysArgs
from config import Config

class Scheduler:
    def __init__(self, schedule, group):
        self.schedule = schedule
        self.group = group

    def enable(self):
        for event, info in self.schedule.items():
            print("Enabling action for {0} on autoscaling group {1} ".format(event, self.group))
            client('autoscaling').put_scheduled_update_group_action(
                ScheduledActionName=event,
                AutoScalingGroupName=self.group,
                Recurrence=info['Recurrence'],
                MinSize=info['MinSize'],
                MaxSize=info['MaxSize'],
                DesiredCapacity=info['DesiredCapacity'],
            )

    def disable(self):
        for event, info in self.schedule.items():
            print("Disabling action for {0} on autoscaling group {1} ".format(event, self.group))
            client('autoscaling').delete_scheduled_action(
                AutoScalingGroupName=self.group,
                ScheduledActionName=event
            )

class Autoscaling:
    def find_group_for(app, env):
        groups = client('autoscaling').describe_tags(
         Filters=[
            {
                'Name': 'key',
                'Values': ['elasticbeanstalk:environment-name']
            }
         ]
        )['Tags']
        group = [ g['ResourceId'] for g in groups if re.match("{0}-.*{1}.*".format(env[:4], app), g['Value']) ][0]
        return group

if __name__ == "__main__":
    app =  SysArgs().get('APPLICATION', 1)
    env_list = ['int', 'qa', 'staging', 'prod' ]
    env = os.environ['ENVIRONMENT']

    for env in env_list:
        c = Config(env, 'beanstalk', app)
        if c.schedule() is None:
            break
        group = Autoscaling.find_group_for(app, env)
        Scheduler(c.schedule(), group).enable()
