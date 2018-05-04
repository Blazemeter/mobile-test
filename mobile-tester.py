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
@click.option('--api_key', prompt=True, help='BlazeMeter api key id', default=lambda: os.environ.get('API_KEY_ID', ''))
@click.option('--api_secret', prompt=True, help='BlazeMeter api key secret', default=lambda: os.environ.get('API_KEY_SECRET', ''))
@click.option('--name', prompt='Test name',
              help='The name of the test', default="Mobile test")
# @click.option('--app_path', prompt='Path of the application',
#               help='The path for application', default="resources/BlazeDemo.ipa")
# @click.option('--test_files_path', prompt='Path of the test file',
# help='The path for zipped test file',
# default="resources/test_bundle_2018_02_21_21_14.zip")
@click.option('--silent', help="assumes default app and test files - no interaction", is_flag=True)
def run(api_key, api_secret, name, silent):
  """Simple program that runs mobile tests on blazemeter platform."""
  click.echo('All passed in variables %s!' % locals())


if __name__ == '__main__':
  run()
