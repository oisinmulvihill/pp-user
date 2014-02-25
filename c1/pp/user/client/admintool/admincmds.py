# -*- coding: utf-8 -*-
"""
"""
import os
#import codecs
import logging
import ConfigParser

import cmdln
import requests

from pp.user.client.rest import UserService


class AdminCmds(cmdln.Cmdln):
    """Usage:
        {name}-admin -c / --config <lp-admin.ini> SUBCOMMAND [ARGS...]
        {name}-admin help SUBCOMMAND

    ${command_list}
    ${help_list}

    """
    # this is also used as the section to get settings from.
    name = "user-admin"

    def __init__(self, *args, **kwargs):
        cmdln.Cmdln.__init__(self, *args, **kwargs)
        self.log = logging.getLogger("%s.AdminCmds" % __name__)

    def get_optparser(self):
        """Parser for global options (that are not specific to a subcommand).
        """
        optparser = cmdln.CmdlnOptionParser(self)

        optparser.add_option(
            '-c', '--config', action='store',
            dest="config_filename",
            default="config.ini",
            help='The global config file %default'
        )

        return optparser

    def postoptparse(self):
        """runs after parsing global options"""

    @property
    def config(self):
        """Return a config instance when called.

        Implement file change and reloading here?

        """
        cfg_filename = self.options.config_filename
        rc = {}

        if os.path.isfile(cfg_filename):
            config = ConfigParser.ConfigParser()
            self.log.debug("config: recovering from <%s>" % cfg_filename)
            config.read(cfg_filename)
            rc = dict(config.items(self.name))

        else:
            self.log.warn(
                "confg: file not found <%s> using defaults." % cfg_filename
            )

        if 'url' not in rc:
            rc['url'] = "http://localhost:60706"

        return rc

    def do_ping(self, subcmd, opts):
        """${cmd_name}: Check if the Latchpony REST Service is running.

        The URL for the service is read from the configuration file.

        ${cmd_usage}
        ${cmd_option_list}

        """
        cfg = self.config
        lp_service_url = cfg['url']

        self.log.debug("ping: URL <%s>" % lp_service_url)
        lps = UserService()
        try:
            result = lps.ping()

        except requests.exceptions.ConnectionError:
            self.log.error("Unable to connect to user service.")

        else:
            self.log.info("Connected to user service OK: %s" % result)
