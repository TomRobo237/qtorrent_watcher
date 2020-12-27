# qBittorrent Watcher client
qBittorrent doesnt have settings to automatically remove after completion or once a certain ratio is hit. So I made one with the help of the API client on pip.

## Installing
First make a virtual enviorment and install the required packages with
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Then setup your connection information in a file `.env` see `env_example` for some defaults.

## Running
Help info:
```
usage: watcher.py [-h] [-d] [-c AFTER_COMPLETION] [-r AT_RATIO] [-i AFTER_INCEPTION] [-x] [-s SLEEP_TIME] [-l LOGFILE]
                  [-v LOGLEVEL]

Monitor torrents and remove based on various criteria. Currently all checks are OR based, if any criteria is met, will execute
removal

options:
  -h, --help            show this help message and exit
  -d, --dry-run         Do not remove files, only log that we would have done something.
  -c AFTER_COMPLETION, --after-completion AFTER_COMPLETION
                        Time in seconds after completed download to remove file.
  -r AT_RATIO, --at-ratio AT_RATIO
                        Remove once a certain ratio has been reached.
  -i AFTER_INCEPTION, --after-inception AFTER_INCEPTION
                        Time in seconds after inception
  -x, --remove-file     Remove file as well as removing the torrent.
  -s SLEEP_TIME, --sleep-time SLEEP_TIME
                        Seconds in-between checks.
  -l LOGFILE, --logfile LOGFILE
                        Logfile to write to.
  -v LOGLEVEL, --loglevel LOGLEVEL
                        Set logging level
```

You can then activate your virtualenv and test out the script and see what settings are good for you.

### System service
I've also included a system service as an example, feel free to edit it with your settings. It assumes you've cloned into or linked the repositor in `/opt/torrent_watcher`
