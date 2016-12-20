import yaml
import os

class Config:
    def __init__(self, environment, resource, application):
        self.environment = environment
        self.resource = resource
        self.application = application
        self.config = self.__load()

    def __load(self):
        config_file = "templates/{0}.yaml".format(self.resource)
        print ("Loading config '{0}'".format(config_file))
        return yaml.load(open(config_file))

    def cf_parameters(self):
        return self.config[self.environment]['parameters']

    def add_cf_parameter(self, key, value):
        parameters = self.config[self.environment]['parameters']
        parameters[key] = value

    def cf_template(self):
        return "templates/{0}.json".format(self.resource)

    def stack_name(self):
        return "{0}-{1}-{2}".format(self.environment, self.application, self.resource)

    def url(self):
        return self.config[self.environment]['url']

    def schedule(self):
        try:
            return self.config[self.environment]['schedule']
        except KeyError:
            return None
