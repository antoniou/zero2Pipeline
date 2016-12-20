import botocore.exceptions

class Stack:
    def __init__(self, name, client, resource):
        self.name = name
        self.client = client
        self.resource = resource

    def exists(self):
        try:
            self.client.describe_stacks(StackName=self.name)
        except botocore.exceptions.ClientError as e:
            errorToCheck= "Stack with id %s does not exist" % self.name
            if errorToCheck == e.response['Error']['Message']:
                return False
            raise e

        return True

    def apply(self, template_name, parameters):
        self.validate(template_name)
        print("Applying template '{0}' to stack '{1}' with parameters {2}"
            .format(template_name, self.name, parameters))

        cf_params=self.__to_cf_params(parameters)
        if(self.exists()):
            self.__update(template_name, cf_params)
        else:
            self.__create(template_name, cf_params)

    def validate(self, template_name):
        print("Validating template '{0}'".format(template_name))

        self.client.validate_template(
            TemplateBody=open(template_name, 'r').read()
        )

    def __print_events(self):
        events = self.client.describe_stack_events(
            StackName=self.name
        )

        print("{!s: <40} {: <20} {: <40} {: <40}"
            .format('Timestamp',
                    'Status',
                    'Type',
                    'Reason')
        )

        for e in events['StackEvents']:
            reason = e['ResourceStatusReason'] if 'ResourceStatusReason' in e.keys() else ''
            print("{!s: <40} {: <20} {: <40} {: <40}"
                .format(e['Timestamp'],
                        e['ResourceStatus'],
                        e['ResourceType'],
                        reason)
            )

    def __create(self, template_name, params):
        print("Creating stack %s" % self.name)

        response = self.client.create_stack(
            StackName=self.name,
            TemplateBody=open(template_name, 'r').read(),
            Parameters=params,
            Capabilities=[
                'CAPABILITY_IAM',
                'CAPABILITY_NAMED_IAM'
            ]
        )
        self.__wait_for('stack_create_complete')
        self.__print_events()

    def __update(self, template_name, params):
        print ("Updating stack %s" % self.name)

        stack = self.resource.Stack(self.name)
        try:
            response = self.client.update_stack(
                StackName=self.name,
                TemplateBody=open(template_name, 'r').read(),
                Parameters=params,
                Capabilities=[
                    'CAPABILITY_IAM',
                    'CAPABILITY_NAMED_IAM'
                ]
            )
        except botocore.exceptions.ClientError as e:
            errorToCheck= "No updates are to be performed."
            if errorToCheck == e.response['Error']['Message']:
                print(errorToCheck)
                return True
            else:
                raise e
        self.__wait_for('stack_update_complete')
        self.__print_events()

    def __to_cf_params(self, parameters):
        params = []
        for (key,value) in  parameters.items():
            params.append({
                'ParameterKey': key,
                'ParameterValue': value,
                'UsePreviousValue': False
            })
        return params

    def __wait_for(self, event):
        waiter = self.client.get_waiter(event)
        waiter.wait(StackName=self.name)
