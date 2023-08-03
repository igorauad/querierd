#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright© 2016 by Alexander Roessler.
# Based on the work of Mark Culler and others.
# This file is part of QuerierD.
#
# QuerierD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# QuerierD is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QuerierD.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import logging
import os
import sys
import threading
import time

from . import Querier


class QuerierInstance:

    def __init__(self, interface, interval, msg_type, group, ttl):
        self.interface = interface
        self.interval = interval
        self.querier = Querier(interface, interval, msg_type, group, ttl)
        self.thread = thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        self.querier.run()

    def stop(self):
        self.querier.stop.set()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.Formatter.converter = time.gmtime  # UTC time

    parser = argparse.ArgumentParser(
        description='Queries multicast group periodically for IGMP snooping')

    parser.add_argument(
        '-i',
        '--interface',
        help='Net interface through which to send IGMP packets \
                        (required)',
        required=True)

    parser.add_argument(
        '-t',
        '--type',
        choices=['v1_query', 'v2_query', 'v3_query', 'v2_report', 'v3_report'],
        default='v3_query',
        help='Target IGMP message type to transmit \
                        (default: v3_query)')

    parser.add_argument('--interval',
                        type=float,
                        help='IGMP transmission interval (default: 5 secs)',
                        default=5.0)

    parser.add_argument('--ttl',
                        type=int,
                        help='IP packet TTL (default: 1)',
                        default=1)

    parser.add_argument('-g',
                        '--group',
                        default=None,
                        help='Target group for group-specific messages \
                        (default: None)')

    parser.add_argument('-d',
                        '--debug',
                        help='Enable debug mode (default: False)',
                        action='store_true')

    args = parser.parse_args()

    if os.getuid() != 0:
        logging.error('You must be root to run a querier.')
        sys.exit(1)

    debug = args.debug
    interval = args.interval
    interface = args.interface
    msg_type = args.type
    group = args.group
    ttl = args.ttl
    wait = 5.0  # network interface checking interval
    processes = {}

    try:
        while True:
            if interface not in processes:
                logging.info('adding new querier: %s' % interface)
                processes[interface] = QuerierInstance(interface, interval,
                                                       msg_type, group, ttl)
                time.sleep(wait)
    except KeyboardInterrupt:
        pass

    if debug:
        logging.info("stopping threads")
    for proc in processes:
        processes[proc].stop()

    # wait for all threads to terminate
    while threading.active_count() > 1:  # one thread for every process is left
        time.sleep(0.1)

    if debug:
        logging.info("threads stopped")

    sys.exit(0)


if __name__ == "__main__":
    main()
