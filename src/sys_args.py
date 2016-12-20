import sys

class SysArgs:

    def __init__(self):
        self.__fail_if_notfound = True

    def get(self, name, number):
        if len(sys.argv) <= number:
            self.__fail("Argument '%s' is missing." % name)
        return sys.argv[number]

    def arg_number(self, number):
        self.__number = number
        return self

    def arg_name(self, name):
        self.__name = name
        return self

    def fail_if_notfound(self, fail):
        self.__fail_if_notfound = fail
        return self

    def get_value(self):
        if len(sys.argv) <= self.__number:
            if (self.__fail_if_notfound):
                self.__fail("Argument '%s' is missing." % self.__name)
            else:
                return None
        return sys.argv[self.__number]

    def __fail(self, message):
        print (message)
        sys.exit(-1)
