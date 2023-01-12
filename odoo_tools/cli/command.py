from __future__ import print_function
import logging
import sys
import os
from os.path import join as joinpath, isdir

import odoo_tools

commands = {}


class Command:
    name = None

    def __init_subclass__(cls):
        cls.name = cls.name or cls.__name__.lower()
        commands[cls.name] = cls


class Help(Command):
    """Display the list of available commands"""

    def run(self, args):
        print("Available commands:\n")
        names = list(commands)
        padding = max([len(k) for k in names]) + 2
        for k in sorted(names):
            name = k.ljust(padding, ' ')
            doc = (commands[k].__doc__ or '').strip()
            print("    %s%s" % (name, doc))
        print("\nUse '%s <command> --help' for individual command help." %
              sys.argv[0].split(os.path.sep)[-1])


def main():
    args = sys.argv[1:]

    if len(args) > 1 and args[0].startswith('--addons-path=') and not args[1].startswith("-"):
        odoo_tools.tools.config._parse_config([args[0]])
        args = args[1:]

    # Default legacy command
    command = "sync"

    # Subcommand discovery
    if len(args) and not args[0].startswith("-"):
        logging.disable(logging.CRITICAL)
        command = args[0]
        args = args[1:]

    if command in commands:
        o = commands[command]()
        o.run(args)
    else:
        sys.exit('Unknown command %r' % (command,))
