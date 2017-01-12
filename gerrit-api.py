"""experimenting with gerrit api"""

import configparser
import json
import logging
import os
import sys

from flask import Flask
import requests
from requests.auth import HTTPDigestAuth

logging.basicConfig(level=os.getenv('GERRIT_API_LOGLEVEL', logging.INFO))
app = Flask(__name__)

config_file = os.getenv(
    'GERRIT_API_CONF',
    os.environ['HOME'] + '/.local/gerrit-api.conf'
)
logging.debug('config file {}'.format(config_file))
conf = configparser.ConfigParser()
conf.read(config_file)
logging.debug('config sections {}'.format(conf.sections()))


def open_changes(conf):
    """"return the number of open changes"""
    site = conf['main']['url']
    user = conf['main']['user']
    password = conf['main']['password']
    auth = '/a'
    human_unreadable = '&pp=0'
    openchanges_endpoint = (
        site +
        auth +
        '/changes/?q=status:open' +
        human_unreadable
    )
    logging.debug(openchanges_endpoint)
    openchanges = requests.get(
        openchanges_endpoint,
        auth=HTTPDigestAuth(user, password)
    )

    logging.debug(
        'open changes status code is {}'.format(str(openchanges.status_code))
    )

    if openchanges.status_code == 404:
        sys.exit(1)

    # per gerrit api doc:
    # To prevent against Cross Site Script Inclusion (XSSI) attacks, the JSON
    # response body starts with a magic prefix line that must be stripped
    # before feeding the rest of the response body to a JSON parser.
    raw = '\n'.join(openchanges.text.split(sep='\n')[1:])

    j = json.loads(raw)
    logging.debug(j)
    return(len(j))


@app.route("/")
def out_open_changes():
    counter = str(open_changes(conf))
    return "There are {} open changes in gerrit.\n".format(counter)


@app.route("/open-changes")
def out_open_changes_2():
    counter = str(open_changes(conf))
    return "There are {} open changes in gerrit.\n".format(counter)


def main():
    app.run()

if __name__ == "__main__":
    main()
