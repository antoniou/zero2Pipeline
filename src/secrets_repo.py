import os

class SecretsRepo:


    def application(self, app):
        self.__application = app
        self.__repo_key= 'SECRET_REPO_DIR'
        return self

    def sub_application(self, sub_app):
        self.__sub_application = sub_app
        return self

    def get(self):
        if self.__repo_key in os.environ:
            repo = os.environ[self.__repo_key]
        else:
            if(self.__sub_application):
                repo = "../{0}-secrets/{1}" \
                    .format(self.__application, self.__sub_application)
            else:
                repo = "../{0}-secrets".format(self.__application)
            print("No environment variable '{0}' found, checking '{1}'" \
                .format(self.__repo_key, repo))

        if not os.path.isdir(repo):
            raise Exception("Secrets repository '{0}' was not found." \
                .format(repo))
        return repo
