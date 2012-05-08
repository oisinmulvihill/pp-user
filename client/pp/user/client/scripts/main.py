# -*- coding: utf-8 -*-
"""
Oisin Mulvihill
2007-05-18

"""
import os
import sys
import time
import os.path
import logging
import ConfigParser
import logging.config
from optparse import OptionParser


def get_log():
    return logging.getLogger("pp.user.client.scripts.main")


def logtoconsolefallback(log):
    # Log to console instead:
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)
    log.propagate = False


def main():
    """
    """
    current_dir = "%s" % os.path.abspath(os.curdir)

    parser = OptionParser()

    parser.add_option(
        "--config", action="store", dest="config_filename",
        default='main.ini',
        help="This director configuration file to use at run time."
    )

    (options, args) = parser.parse_args()

    log = logging.getLogger()

    # Load the system config:
    if not os.path.isfile(options.config_filename):
        sys.stderr.write("The config file name '%s' wasn't found" % options.config_filename)
        sys.exit(1)

    else:
        logtoconsolefallback(log)

        # Set up the director config and recover the object from it:
        log.info("Main: configuration %s" % options.config_filename)

        try:
            log.info("Main Running: current_dir<%s>." % current_dir)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log.info("Ctrl-C caught, exit time.")
