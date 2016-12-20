import botocore.exceptions

class S3Bucket:
    def __init__(self, resource, name):
        self.resource = resource
        self.name = name

    def upload(self, source, dest=None):
        dest = source if dest is None else dest
        if not self.__exists():
            print ("Bucket - '{0}' does not exist. Creating the bucket".format(self.name))
            self.__create()

        print ("Uploading '{0}' to '{1}'" \
            .format(source, "{0}/{1}".format(self.name, dest)))
        self.resource.Bucket(self.name).upload_file(source, dest)

    def __create(self):
        self.resource.Bucket(self.name)
        self.resource.create_bucket(Bucket=self.name,
            CreateBucketConfiguration={
                    'LocationConstraint': 'eu-west-1'
                }
        )

    def __exists(self):
        return self.resource.Bucket(self.name) in self.resource.buckets.all()
