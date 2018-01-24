#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python PWRCheck Reader Commands."""

import argparse
import os
import pprint
import time

import librato

import pwrcheck

__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2018 Greg Albrecht'
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

    opts = parser.parse_args()

    librato_email = os.environ.get('LIBRATO_EMAIL')
    librato_token = os.environ.get('LIBRATO_TOKEN')

    librato_api = None
    if librato_email and librato_token:
        librato_api = librato.connect(librato_email, librato_token)

    pwrcheck_poller = pwrcheck.SerialPoller(
        opts.serial_port, opts.serial_speed)
    pwrcheck_poller.start()

    time.sleep(pwrcheck.PWRCHECK_WARM_UP)

    try:
        while 1:
            print(time.time())
            pprint.pprint(pwrcheck_poller.pwrcheck_props)

            if librato_api:
                print('Submitting to Librato...')
                api_queue = librato_api.new_queue()
                for k,v in pwrcheck_poller.pwrcheck_props.items():
                    api_queue.add(k, float(v))
                api_queue.submit()

            if opts.interval == 0:
                break
            else:
                time.sleep(opts.interval)

    except KeyboardInterrupt:
        pwrcheck_poller.stop()
    finally:
        pwrcheck_poller.stop()
