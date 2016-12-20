from jinja2 import Environment, FileSystemLoader

class Template:
    def __init__(self, name):
        self.name = name

    def render(self, attributes):
        env = Environment(loader=FileSystemLoader('beanstalk'))
        template = env.get_template(self.name)
        return template.render(attributes)
