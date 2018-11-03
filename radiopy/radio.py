#! /usr/bin/python

###########################################################################
 #   Copyright (C) 2007-2014 by Guy Rutenberg                              #
 #   guyrutenberg@gmail.com                                                #
 #                                                                         #
 #   This program is free software; you can redistribute it and/or modify  #
 #   it under the terms of the GNU General Public License as published by  #
 #   the Free Software Foundation; either version 2 of the License, or     #
 #   (at your option) any later version.                                   #
 #                                                                         #
 #   This program is distributed in the hope that it will be useful,       #
 #   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
 #   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
 #   GNU General Public License for more details.                          #
 #                                                                         #
 #   You should have received a copy of the GNU General Public License     #
 #   along with this program; if not, write to the                         #
 #   Free Software Foundation, Inc.,                                       #
 #   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import radiopy
import sys
from optparse import OptionParser
import argparse
import logging

__version__ = "0.6"

def parse_arguments():
    parser = argparse.ArgumentParser(usage="%(prog)s [OPTIONS] station_name")
    parser.add_argument(nargs=argparse.REMAINDER, dest="station_name",
                        help="Station name")
    parser.add_argument("-s", "--sleep", dest="sleep", type=int, default=0,
                    help="go to sleep after MIN minutes", metavar="MIN")
    parser.add_argument("-w", "--wake-up", dest="wake", type=int, default=0,
                    help="wake up and start playing after MIN minutes", metavar="MIN")
    parser.add_argument("-l", "--list", dest="list", action="store_true", default=False,
                    help="show a list of known radio stations and their homepage")
    parser.add_argument("-c", "--cache", dest="cache", type=int, default=320,
                    help="set the size of the cache in KBytes [default: %(default)d]", metavar="SIZE")
    parser.add_argument("-r", "--record", dest="record",
                    help="dump the stream to FILE", metavar="FILE")

    parser.add_argument("--random", dest="random", action="store_true", default=False,
                    help="let radio.py select a random station for you")

    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                    help="Verbose mode. Multiple -v options increase the verbosity")
    parser.add_argument("-q", "--quiet", dest="quiet", action="count", default=0,
                    help="Quiet mode. Multiple -q options decrease the verbosity.")

    version = ("%(prog)s {}. Copyright (C) 2007-2014 Guy Rutenberg "
               "http://www.guyrutenberg.com/radiopy/").format(__version__)
    parser.add_argument('--version', action="version",
                        version=version)



    args = parser.parse_args()
    args._station_name = ' '.join(args.station_name)

    log_level = logging.WARNING #DEFAULT
    log_level -= (args.verbose - args.quiet) * 10
    logging.basicConfig(level=log_level, format='%(levelname)s:%(message)s')
    logging.info("Verbosity: {}".format(logging.getLevelName(log_level)))

    if not (args.station_name or args.random or args.list):
        parser.error("Missing station name.")

    return args

def main():
    args = parse_arguments()

    player = radiopy.Player({})
    player_options = {
        'wake': args.wake,
        'sleep': args.sleep,
        'record': args.record,
        'cache': args.cache
    }

    if args.list:
        player.print_list()
        sys.exit(0)
    if args.random:
        player.play_random()
    else:
        player.play(args._station_name, **player_options)



if __name__ == "__main__":
    main()


