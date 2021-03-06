import requests
import requests.auth
import os
import json
import time
import logging
import shutil
import click

SLEEP_TIME = 1


def download_file(url):
    local_filename = url.split('/')[-1].split('?')[0]
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return local_filename


@click.command()
@click.option(
    '--api_key',
    prompt=True,
    help='BlazeMeter api key id',
    default=lambda: os.environ.get('API_KEY_ID', ''))
@click.option(
    '--api_secret',
    prompt=True,
    help='BlazeMeter api key secret',
    default=lambda: os.environ.get('API_KEY_SECRET', ''))
@click.option(
    '--name',
    prompt='Test name',
    help='The name of the test',
    default="Mobile test")
# @click.option('--app_path', prompt='Path of the application',
#               help='The path for application', default="resources/BlazeDemo.ipa")
# @click.option('--test_files_path', prompt='Path of the test file',
# help='The path for zipped test file',
# default="resources/test_bundle_2018_02_21_21_14.zip")
@click.option(
    '--silent',
    help="assumes default app and test files - no interaction",
    is_flag=True)
def run(api_key, api_secret, name, silent):
    """Simple program that runs the given mobile tests on blazemeter platform."""
    # click.echo('All passed in variables %s!' % locals())
    app_path = 'resources/BlazeDemo.ipa'
    # 'resources/test_bundle_2018_02_21_21_14.zip'
    test_files_path = 'test-files/python/test_bundle.zip'

    # setup logging
    logging_level = logging.INFO if 'VERBOSE' not in os.environ else logging.DEBUG
    format_string = "%(asctime)s %(thread)d %(threadName)s %(filename)s:%(lineno)d %(funcName)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging_level, format=format_string)

    # setup the base url and basic auth
    auth = requests.auth.HTTPBasicAuth(api_key, api_secret)
    base_url = '{}/api/v4'.format(
        os.environ.get('BZA_URL', 'https://a.blazemeter.com'))

    # creating a test project with name...
    logging.debug("Getting user data for extraction of the project id")
    user_data = requests.get(
        url='{}/user'.format(base_url), auth=auth).json()['result']
    default_project_id = user_data['defaultProject']['id']
    logging.debug("Extracted project id %d", default_project_id)

    devices = requests.get(
        url='{}/tests/list-mobile-devices'.format(base_url), auth=auth).json()['result']

    ios_devices = [device for device in devices if device['platform'] == 'IOS']
    chosen_device = filter(lambda x: x['os'] == '10.2', ios_devices)[0]
    device_arn_1 = chosen_device['arn']

    project_name = name
    data = {
        "name": project_name,
        "projectId": default_project_id,
        "configuration": {
            "plugins": {
                "mobileTest": {
                    "enabled": True,
                    "devices": [
                        {
                            "arn": device_arn_1
                        }
                    ]
                }
            },
            "type": "mobile"
        }
    }
    logging.info("Creating test project with name: %s, device -%s(%s)",
                 project_name, chosen_device['name'], chosen_device['os'])
    logging.info("You can change the device selection later if you wish")

    response = requests.post(
        url='{}/tests'.format(base_url),
        data=json.dumps(data),
        auth=auth,
        headers={
            "Content-Type": "application/json"
        })
    test_object = response.json()['result']
    test_id = test_object['id']
    logging.info("Project created...id %d", test_id)
    logging.debug("Getting upload links")
    requests.post(
        url='{}/tests/{}/mobile-tests/start-uploads?platform={}&framework={}'.format(
            base_url, test_id, 'IOS_APP', 'APPIUM_PYTHON_TEST_PACKAGE'),
        auth=auth)
    got_upload_links = False
    while not got_upload_links:
        test_object = requests.get(
            url='{}/tests/{}'.format(base_url, test_id),
            auth=auth).json()['result']
        mobile_test_configuration = test_object['configuration']['plugins'][
            'mobileTest']
        if 'appUploadUrl' in mobile_test_configuration and 'testPackageUploadUrl' in mobile_test_configuration:
            got_upload_links = True
        else:
            time.sleep(SLEEP_TIME)
    logging.debug("Got upload links")

    # uploading the files
    if not silent:
        application_path = raw_input(
            "Enter application path, hit `enter` for default ({}): ".format(
                app_path)).strip()
        if len(application_path) == 0:
            application_path = app_path
    else:
        application_path = app_path

    # first the application
    mobile_test_configuration = test_object['configuration']['plugins'][
        'mobileTest']
    app_upload_url = mobile_test_configuration['appUploadUrl']
    test_package_url = mobile_test_configuration['testPackageUploadUrl']
    headers = {'Content-Type': 'application/octet-stream'}

    logging.info("Uploading app %s", application_path)

    app_data = open(application_path, 'rb').read()
    requests.put(url=app_upload_url, data=app_data, headers=headers)
    app_upload_succeeded = False
    while not app_upload_succeeded:
        requests.post(
            url='{}/tests/{}/mobile-tests/check-uploads'.format(
                base_url, test_id),
            auth=auth,
            params={
                "fileType": "app"
            })
        test_object = requests.get(
            url='{}/tests/{}'.format(base_url, test_id),
            auth=auth).json()['result']
        mobile_test_configuration = test_object['configuration']['plugins'][
            'mobileTest']

        if 'appUploadStatus' in mobile_test_configuration and mobile_test_configuration['appUploadStatus'] == 'SUCCEEDED':
            app_upload_succeeded = True
        else:
            # validating application
            logging.info('Waiting for verification')
            time.sleep(SLEEP_TIME + 4)

    # uploading tests...
    if not silent:
        test_package = raw_input(
            "Enter zipped test files path, hit `enter` for default ({}): ".format(test_files_path)).strip()
        if len(test_package) == 0:
            test_package = test_files_path
    else:
        test_package = test_files_path

    logging.info("Uploading test package %s", test_package)
    test_package_data = open(test_package, 'rb').read()
    requests.put(url=test_package_url, data=test_package_data, headers=headers)
    test_package_upload_succeeded = False
    while not test_package_upload_succeeded:
        requests.post(
            url='{}/tests/{}/mobile-tests/check-uploads'.format(
                base_url, test_id),
            auth=auth,
            params={
                "fileType": "testPackage"
            })
        test_object = requests.get(
            url='{}/tests/{}'.format(base_url, test_id),
            auth=auth).json()['result']
        mobile_test_configuration = test_object['configuration']['plugins'][
            'mobileTest']
        if 'testPackageUploadStatus' in mobile_test_configuration and mobile_test_configuration['testPackageUploadStatus'] == 'SUCCEEDED':
            test_package_upload_succeeded = True
        else:
            # validating tests
            logging.info('Waiting for verification')
            time.sleep(SLEEP_TIME + 4)

    # selecting device...
    if not silent:
        print("*** Available devices ****")
        for i, device in enumerate(ios_devices[:10]):
            print("{0:2d}. {1}({2})".format(i + 1, device['name'], device['os']))

        choice = raw_input("Enter a choice for device, hit `enter` for default ({}({}): ".
                           format(chosen_device['name'], chosen_device['os'])).strip()
        if len(choice) != 0:
            device = ios_devices[int(choice) - 1]
            logging.info("Chosen device is - %s(%s)",
                         device['name'], device['os'])

            data["configuration"]["plugins"]["mobileTest"][
                "devices"][0]["arn"] = device['arn']

            response = requests.put(
                url='{}/tests/{}'.format(base_url, test_id),
                data=json.dumps(data),
                auth=auth,
                headers={
                    "Content-Type": "application/json"
                })
            test_object = response.json()['result']
            logging.debug("Updated test object is", test_object)

    # starting the test...
    logging.info("You are all set..Starting the test")
    master_object = requests.post(
        url='{}/tests/{}/start'.format(base_url, test_id),
        auth=auth).json()['result']
    session_id = master_object['sessionsId'][0]
    logging.info("Started the test with session id %s", session_id)
    artifacts = []

    logging.info("Running tests")
    # waiting for the results
    while len(artifacts) == 0:
        artifacts = requests.get(
            url='{}/sessions/{}/mobile-test-artifacts'.format(
                base_url, session_id),
            auth=auth).json()['result']
        print('.')
        time.sleep(SLEEP_TIME + 4 + 10)

    logging.info("Congratulations. Test completed. Getting results.")

    # lets filter for relevant artifacts
    results = [
        i for i in artifacts
        if i['type'] in ['SCREENSHOT', 'VIDEO', 'APPIUM_PYTHON_XML_OUTPUT']
    ]

    # filter results for particular keys
    results = [{
        'type': ty['type'],
        'name': ty['name'],
        'url': ty['url']
    } for ty in results]

    # print results
    for item in results:
        print("{")
        for key in item:
            print(key, ':', item[key])
        print("}")


if __name__ == '__main__':
    run()
