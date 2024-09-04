#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
managedkaos/azlyrics.py
https://gist.github.com/managedkaos/e3262b80154129cc9a976ee6ee943da3
"""

# Requests is a library that allows you to programmatically send out http requests
# from botocore.vendored import requests
import csv
import requests
from requests.exceptions import ConnectionError
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# requests inside botocore really shouldn't be used. but curious if performance is better
# from botocore.vendored import requests
# from botocore.vendored.requests.exceptions import ConnectionError
# from botocore.vendored.requests.adapters import HTTPAdapter
# from botocore.vendored.requests.packages.urllib3.util.retry import Retry

# os is a library for doing operating system things, like looking through file directories
import os
import s3fs
import time
import logging
import random

# BeautifulSoupp is a library made to allow developers to parse through the contents of a webpage
from bs4 import BeautifulSoup
# import pandas as pd


logger = logging.getLogger('rap_webscraper.{}'.format(__name__))

logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(ch)

SLEEP_TIME = 5.212
NOISE = (-4.438, 4.32)
# act like a mac when requesting url
headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"}
#NOISE = (0,5)

# TODO: create from scrape_config.csv

BUCKETNAME = "bars-api"
BARSDIR = "just-lyrics"
def handle(event, context):

    today_day = time.localtime().tm_mday

    fs = s3fs.S3FileSystem()

    sess = requests.Session()

    retries = Retry(total=2, backoff_factor=2.5, status_forcelist=[500, 501, 502, 503, 504])

    sess.mount('http://', HTTPAdapter(max_retries=retries))
    sess.mount('https://', HTTPAdapter(max_retries=retries))
    #scrape_config = os.path.join("webscrape", "scrape_config.csv")

    #df = pd.read_csv(scrape_config)

    # artists_and_urls = zip(df.to_dict()['artist'].values(), df.to_dict()['url'].values())

    # artists_and_urls = zip(['frankocean'], ['https://www.azlyrics.com/f/frankocean.html'])

    lyric_links = os.path.join(BUCKETNAME, 'lyrics_sources', 'scrape_config.csv')
    with fs.open(lyric_links, 'r') as f:
        reader = csv.DictReader(f)

        artists_and_urls = []
        for row in reader:
            artists_and_urls.append((row['artist'], row['url']))

    # pick a random artist to start with so everyone gets a turn

    for artist_folder_name, url in artists_and_urls[today_day:]:
        """
        sleep before request
        you could check if the artists directory exists and skip first
        but if a previous scrape session ended midway you wouldnt check for any missed songs
        if the url lists gets too long you may get blocked just from the initial request to artist pages
        """
        logger.info('Requesting songs from: {}'.format(url))
        pre_request_sleep = SLEEP_TIME + random.uniform(NOISE[0], NOISE[1])
        logger.info('Sleeping: {}'.format(pre_request_sleep))
        time.sleep(pre_request_sleep)
        # make a request for the data
        try:
            r = sess.get(url, headers=headers)
        except ConnectionError as ce:
            logger.info('Errored on:{} \n{}'.format(url, ce))
            continue

        # convert the response text to soup use lxml parser
        soup = BeautifulSoup(r.text, "lxml")

        # get the songs and links to the lyrics
        for song_link in soup.find_all("a", href=True):
            if len(song_link.text) == 0:
                continue
            lyric_url = song_link['href']

            if ".." in lyric_url:
                lyric_url = "https://www.azlyrics.com" + lyric_url[2:]
                logger.info("Looking @ Lyrics for {}".format(lyric_url))

                filename = song_link.text.replace(' ', '_').replace("'", '').replace('/', '')
                filename += ".txt"
                if filename.lower() == "submit.txt":
                    continue
                filename = os.path.join(BUCKETNAME, BARSDIR, artist_folder_name, filename)
                filename = str(filename)

                logger.info("Filename: {}".format(filename))

                """
				a lot of the unspecified excepts are just to catch annoying character encoding bs
				that comes with webscraping
                string casting because fs exists needs to be a string or there will
                be external errors if the passed type is a byte-string
				"""
                if fs.exists(filename):
                    try:
                        logger.info('File {} already exists, skipping web request'.format(filename.encode('utf-8')))
                    except:
                        continue
                    continue
                try:
                    logger.debug('Requesting: {}'.format(lyric_url))
                except:
                    pass
                """
				sleep for some time (in seconds) so you arent banned from sites..
				add some random noise to the sleep so it don't look like a robot
				"""
                this_sleep = SLEEP_TIME + random.uniform(NOISE[0], NOISE[1])
                logger.info('Sleeping: {}'.format(this_sleep))
                time.sleep(this_sleep)
                try:
                    response = sess.get(lyric_url, headers=headers)
                except ConnectionError as ce:
                    logger.info('{}'.format(ce))
                    continue
                new_soup = BeautifulSoup(response.text, "lxml")

                try:
                    logger.debug('Will Write to: {}'.format(filename))
                except:
                    pass

                # https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
                if not fs.exists(str(os.path.dirname(filename))):
                    logger.info('{} Does not exist.'.format(os.path.dirname(filename)))
                    try:
                        fs.mkdir(str(os.path.dirname(filename)))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                f = fs.open(filename, "w")

                # loop through the no clas divs. they contain the lyrics
                for lyric in new_soup.find_all("div", {"class": None}):
                    try:
                        f = fs.open(filename, "a")
                    except IOError:
                        logger.warning('IOError could not write filename: {}'.format(filename))
                        continue
                    try:
                        f.write(lyric.text)
                    except UnicodeError:
                        logger.warning('UnicodeError, Skipping: {}'.format(filename))
                        f.close()
                        continue

                # the song panel div has the album name and the year
                for song_panel_div in new_soup.find_all("div", {"class": "panel songlist-panel noprint"}):
                    try:
                        f.write('ALBUM INFO')
                        f.write(song_panel_div.text)
                    except UnicodeError:
                        logger.warning('UnicodeError, Skipping')
                        f.close()
                        continue

                f.close()



if __name__ == "__main__":

    hanldle()

