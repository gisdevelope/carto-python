from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sync_tables import SyncTableJobManager
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
import time
import logging
import re

# python import_sync_table.py "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip" 900
# Logger (better than print)
import logging
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
import argparse
parser = argparse.ArgumentParser(
    description='Create a sync table from a URL')

parser.add_argument('url', type=str,
                    help='Set the URL of data to sync.' +
                    ' Add it in double quotes')
parser.add_argument('sync_time', type=int,
                    help='Set the time to sync your' +
                    ' table in seconds (min: 900s)')
parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
dataset_manager = DatasetManager(auth_client)
table = dataset_manager.create(args.url, args.sync_time)

# get username from base_url
substring = re.search('https://(.+?).carto.com', args.CARTO_BASE_URL)
if substring:
    username = substring.group(1)

# return the id of the sync
logger.info('Name of table: ' + str(table.name))
print('\nURL of dataset is: https://{org}.carto.com/u/{username}/dataset/{data}').format(org=args.organization,username=username ,data=str(table.name))