import os

import smoke
from sys_args import SysArgs


if __name__ == "__main__":
    app_env = os.environ["ENVIRONMENT"]
    application =  SysArgs().get('APPLICATION', 1)
    app_version = SysArgs().get('APP_VERSION', 2)

    started = smoke.wait_for_response_to_contain(
      "https://{0}-{1}.smbctest.com/healthcheck".format(app_env, application),
      "DTS_FRONTEND Version {0}".format(app_version),
      4,
      30
    )

    if not started:
        exit(1)
