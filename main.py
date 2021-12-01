#!/usr/bin/env python3 
# PYTHON_ARGCOMPLETE_OK

import argparse
import os
import sys
import signal
import json

import config
import contest
from util import *

from pathlib import Path


class SuppressingParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super(SuppressingParser, self).__init__(**kwargs, argument_default=argparse.SUPPRESS)


def build_parser():
    parser = SuppressingParser(
        description="""
    An arrangement system for participant management and DOMJudge registration.
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(
        title='actions', dest='action', parser_class=SuppressingParser
    )
    subparsers.required = True

    contest = subparsers.add_parser('contest',  help='Manage contest.')
    contest_subparsers = contest.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    contest_subparsers.required = True
    contest_create = contest_subparsers.add_parser('create',  help='Create a new contest.')
    contest_lock = contest_subparsers.add_parser('lock',  help='Lock the contest.')
    contest_unlock = contest_subparsers.add_parser('unlock',  help='Unlock the contest.')

    contestant = subparsers.add_parser('contestant', help='Manage contestants.')
    contestant_subparsers = contestant.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    contestant_subparsers.required = True
    contestant_add = contestant_subparsers.add_parser('add', help='Add a contestant.')
    contestant_import = contestant_subparsers.add_parser('import', help='Import contestants from a tsv file.')
    contestant_remove = contestant_subparsers.add_parser('remove', help='Remove a contestant.')
    contestant_show = contestant_subparsers.add_parser('show', help='Show information of a contestant.')
    contestant_seat = contestant_subparsers.add_parser('seat', help='Seat a contestant.')
    contestant_seatall = contestant_subparsers.add_parser('seatall', help='Seat all unseated contestants.')
    contestant_unseat = contestant_subparsers.add_parser('unseat', help='Unseat a contestant.')
    contestant_genpass = contestant_subparsers.add_parser('genpass', help='Generate password for a contestant.')

    seat = subparsers.add_parser('seat', help='Manage seats.')
    seat_subparsers = seat.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    seat_subparsers.required = True
    seat_add = seat_subparsers.add_parser('add', help='Add a seat.')
    seat_import = seat_subparsers.add_parser('import', help='Import seats from a tsv file.')
    seat_remove = seat_subparsers.add_parser('remove', help='Remove a seat.')
    seat_show = seat_subparsers.add_parser('show', help='Find out that who is using a specific seat.')
    seat_where = seat_subparsers.add_parser('where', help='Find out where is a specific team seated.')
    seat_list = seat_subparsers.add_parser('list', help='List all seats and their information.')

    affiliation = subparsers.add_parser('affiliation', help='Manage affiliations.')
    affiliation_subparsers = affiliation.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    affiliation_subparsers.required = True
    affiliation_add = affiliation_subparsers.add_parser('add', help='Add a affiliation.')
    affiliation_import = affiliation_subparsers.add_parser('import', help='Import affiliations from a tsv file.')
    affiliation_remove = affiliation_subparsers.add_parser('remove', help='Remove a affiliation by its externalid.')

    export = subparsers.add_parser('export', help='Export data.')
    export_subparsers = export.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    export_subparsers.required = True
    export_domjudge = export_subparsers.add_parser('domjudge', help='Export accounts.tsv and teams.json for DOMJudge.')
    export_contestants = export_subparsers.add_parser('contestants', help='Export contestant information.')

    return parser


def run_parsed_arguments(args):
    config.args = args

    action = config.args.action

    if action == 'contest':
        subaction = config.args.subaction
        if subaction == 'create':
            contest.create_contest()
        if subaction in ['lock', 'unlock']:
            contest.toggle_lock(subaction == 'lock')
        return


def main():
    def interrupt_handler(sig, frame):
        fatal('Running interrupted')

    signal.signal(signal.SIGINT, interrupt_handler)
    parser = build_parser()
    run_parsed_arguments(parser.parse_args())


if __name__ == '__main__':
    main()

