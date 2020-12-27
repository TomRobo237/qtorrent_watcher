#!/usr/bin/env python3
import argparse
from datetime import datetime
import logging
import os
import sys
from time import sleep

import dotenv
import qbittorrentapi

# LOGGING
log = logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    )

log = logging.getLogger(__name__)
log_format = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')

# Setting up enviorment
dotenv.load_dotenv(dotenv.find_dotenv())
HOST = os.getenv('HOST') or 'localhost'
PORT = os.getenv('PORT') or '8080'
USERNAME = os.getenv('USERNAME') or 'admin'
PASSWORD = os.getenv('PASSWORD') or 'adminadmin'

# Getting client connection
CLIENT = qbittorrentapi.Client(HOST, PORT, USERNAME, PASSWORD)

# Parse command line args
PARSER = argparse.ArgumentParser(description='Monitor torrents and remove based on various criteria. Currently all checks are OR based, if any criteria is met, will execute removal')
PARSER.add_argument('-d', '--dry-run', action='store_true', help='Do not remove files, only log that we would have done something.')
PARSER.add_argument('-c', '--after-completion', type=int, help='Time in seconds after completed download to remove file.')
PARSER.add_argument('-r', '--at-ratio', type=float, help='Remove once a certain ratio has been reached.')
PARSER.add_argument('-i', '--after-inception', type=int, help='Time in seconds after inception')
PARSER.add_argument('-x', '--remove-file', action='store_true', help='Remove file as well as removing the torrent.')
PARSER.add_argument('-s', '--sleep-time', default=86400, help='Seconds in-between checks.')
PARSER.add_argument('-l', '--logfile', help='Logfile to write to.')
PARSER.add_argument('-v', '--loglevel', help='Set logging level')
ARGS = PARSER.parse_args()

# Add logfile
if ARGS.logfile:
    handler = logging.FileHandler(ARGS.logfile)
    handler.setFormatter(log_format)
    log.addHandler(handler)

if ARGS.loglevel:
    log.setLevel(logging.getLevelName(ARGS.loglevel))

def check_dry(func):
    def wrapper(*args, **kwargs):
        if ARGS.dry_run:
            log.info('Would have run %s with %s and %s', func.__name__, args, kwargs)
        else:
            return func(*args, **kwargs)
    return wrapper

def compare_dates(date_a: int, date_b: int) -> bool:
    return date_a >= date_b

def get_max_time(date: int, offset: int) -> int:
    return date + offset

@check_dry
def remove_torrent(torrent: qbittorrentapi.TorrentDictionary) -> None:
    log.info('Removing Torrent: %s, remove file: %s', torrent['name'], ARGS.remove_file)
    torrent.delete(delete_files=ARGS.remove_file)

def main():
    for torrent in CLIENT.torrents_info():
        log.info('Checking torrent %s', torrent['name'])
        if torrent['progress'] != 1:
            log.info('Skipping %s, not completed yet.', torrent['name'])
            continue

        if ARGS.at_ratio:
            log.info('(Ratio) Max ratio: %s, current ratio: %s', ARGS.at_ratio, torrent['ratio'])
            if ARGS.at_ratio <= torrent['ratio']:
                remove_torrent(torrent)
                continue

        if ARGS.after_completion:
            max_time = get_max_time(torrent['completion_on'], ARGS.after_completion)
            now = datetime.now().timestamp()
            log.info('(Completion) Max time: %s, current time: %s', max_time, now)
            if compare_dates(now, max_time):
                remove_torrent(torrent)
                continue

        if ARGS.after_inception:
            max_time = get_max_time(torrent['added_on'], ARGS.after_inception)
            now = datetime.now().timestamp()
            log.info('(Inception) Max time: %s, current time: %s', max_time, now)
            if compare_dates(now, max_time):
                remove_torrent(torrent)
                continue

if __name__ == '__main__':
    while True:
        main()
        sleep(ARGS.sleep_time)

