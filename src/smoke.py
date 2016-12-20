import socket
import re
import time

import requests


class VersionCheckingSmokeTest:
    def __init__(self, name, url, version, timeout):
        self.name = name
        self.url = url
        self.version = version
        self.timeout = timeout

    def _parse_app_version(self, result_text):
        version = ""
        try:
            firstline = result_text.splitlines()[0]
            version_regex = re.compile(r'\d+.\d+.\d+')
            version = version_regex.search(firstline)[0].split('.')[2]
        except Exception as ex:
            print("Error parsing app version")
        return version

    def perform(self):
        try:
            request = requests.get(self.url)
            if request.status_code >= 200 and request.status_code < 300:
                app_version = self._parse_app_version(request.text)
                result = self.version == app_version
                print("[{0}]\t Got version {1} expected {2} for {3}".format(
                  self.name,
                  app_version,
                  self.version,
                  self.url))
                return result
            else:
                return False
        except socket.timeout as e:
            print(e)
            return False


class SmokeTest:
    def __init__(self, name, url, timeout):
        self.name = name
        self.url = url
        self.timeout = timeout

    def perform(self):
        try:
            request = requests.get(self.url)
            print("[{0}]\t Got status {1} for {2}".format(
              self.name,
              request.status_code,
              self.url))
            return request.status_code >= 200 and request.status_code < 300
        except socket.timeout as e:
            print(e)
            return False


def _run_smoke_test(test, retries):
    for i in range(0, retries):
        result = test.perform()
        if result:
            break

        if i == (retries - 1):
            raise Exception("No successful result for [{0}] after {1} attempts"
              .format(test.name, retries))
        else:
            wait_time = 15 * (i + 1)
            print("Waiting {0} seconds before retrying".format(wait_time))
            time.sleep(wait_time)


def run_all_smoketests(smoke_tests, retries):
    for smoke_test in smoke_tests:
        _run_smoke_test(smoke_test, retries)


def wait_for_response_to_contain(url, expected_contents, max_retires, back_off_time):
    started = False
    last_request = None
    for i in range(0, max_retires):
        request = requests.get(url)
        last_request = request
        if expected_contents in request.text:
            print("App started")
            started = True
            break
        wait_time = (i+1) * back_off_time
        print("Waiting for {0} to appear in response app to start. \
          Previous attempts {1}. Wait Time {2}.".format(
          expected_contents, i + 1, wait_time
        ))
        time.sleep(wait_time)
    if not started:
        print("Expected content not found in {0}".format(last_request.text))
    return started


if __name__ == "__main__":
    # Example usage
    tests = [
    SmokeTest("Test hitting google", "http://www.google.com/", 100),
    SmokeTest("Test hitting TWs", "http://www.thoughtworks.com/", 100),
    VersionCheckingSmokeTest("Test app version", "https://int-dts.smbctest.com/healthcheck", "126", 100),
    SmokeTest("Test failing test", "http://alpha.stockport.gov.uk/", 100),
    ]
    try:
        run_all_smoketests(tests, 3)
        print("=======================")
        print("Smoke tests successful!")
    except Exception as ex:
        print("=======================")
        print("Smoke tests failed </3 | {0}".format(ex))
        exit(1)
