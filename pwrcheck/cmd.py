#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python PWRCheck Reader Commands."""

import argparse
import copy
import json
import os
import pprint
import time

import requests

import pwrcheck

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2019 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


def cli() -> None:
    """Tracker Command Line interface for PWRCheck."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--serial_port', help='serial_port', required=True
    )
    parser.add_argument(
        '-b', '--serial_speed', help='serial_speed', default=115200
    )
    parser.add_argument(
        '-i', '--interval', help='interval', default=0, type=int
    )
    parser.add_argument(
        '-u', '--url', help='url', default='http://node-red/pwrcheck'
    )

    opts = parser.parse_args()

    pwrcheck_poller = pwrcheck.SerialPoller(
        opts.serial_port, opts.serial_speed)
    pwrcheck_poller.start()

    time.sleep(pwrcheck.PWRCHECK_WARM_UP)

    try:
        while 1:
            props = copy.copy(pwrcheck_poller.pwrcheck_props)
            props['ts'] = time.time()
            pprint.pprint(pwrcheck_poller.pwrcheck_props)

            if opts.url:
                try:
                    res = requests.post(opts.url, data=props)
                except Exception as exc:
                    print(exc)

            del props

            if opts.interval == 0:
                break
            else:
                time.sleep(opts.interval)

    except KeyboardInterrupt:
        pwrcheck_poller.stop()
    finally:
        pwrcheck_poller.stop()
