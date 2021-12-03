#!/usr/bin/env python3 
# PYTHON_ARGCOMPLETE_OK

import argparse
import string
import signal

import affiliation
import config
import contest
import contestant
import seat
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

    contest_parser = subparsers.add_parser('contest', help='Manage contest.')
    contest_subparsers = contest_parser.add_subparsers(title='actions', dest='subaction',
                                                       parser_class=SuppressingParser)
    contest_subparsers.required = True
    contest_create = contest_subparsers.add_parser('create', help='Create a new contest.')
    contest_lock = contest_subparsers.add_parser('lock', help='Lock the contest.')
    contest_unlock = contest_subparsers.add_parser('unlock', help='Unlock the contest.')
    contest_show = contest_subparsers.add_parser('show', help='Show contest information.')

    contestant_parser = subparsers.add_parser('contestant', help='Manage contestants.')
    contestant_subparsers = contestant_parser.add_subparsers(title='actions', dest='subaction',
                                                             parser_class=SuppressingParser)
    contestant_subparsers.required = True
    contestant_add = contestant_subparsers.add_parser('add', help='Add a contestant.')
    contestant_import = contestant_subparsers.add_parser('import', help='Import contestants from a tsv file.')
    contestant_import.add_argument('file_path', type=Path, help='Path to the file.')
    contestant_remove = contestant_subparsers.add_parser('remove', help='Remove a contestant.')
    contestant_remove.add_argument('id', type=int, help='ID of the contestant to remove.')
    contestant_show = contestant_subparsers.add_parser('show', help='Show information of a contestant.')
    contestant_show.add_argument('id', type=int, nargs='?', default=-1, const=-1, help='ID of the contestant to show. Ignore it to print all contestants.')
    contestant_show.add_argument('-p', '--print-password', action='store_true', default=False, help='Print the password.')
    contestant_seat = contestant_subparsers.add_parser('seat', help='Seat a contestant.')
    contestant_seat.add_argument('id', type=int, help='ID of the contestant to be seated.')
    contestant_seat.add_argument('--manual', '-m', dest='manual_seat', action='store_true', default=False, help='Manually seat the contestant.')
    contestant_seat.add_argument('--override', '-o', dest='override_seat', action='store_true', default=False, help='Override the current seat.')
    contestant_seat.add_argument('--random', '-r', dest='random_apply_seat', action='store_true', default=False, help='Randomly apply a seat (for automatic mode).')
    contestant_seatall = contestant_subparsers.add_parser('seatall', help='Seat all unseated contestants.')
    contestant_seatall.add_argument('--random', '-r', dest='random_apply_seat', action='store_true', default=False, help='Randomly apply a seat (for automatic mode).')
    contestant_unseat = contestant_subparsers.add_parser('unseat', help='Unseat a contestant.')
    contestant_unseat.add_argument('id', type=int, nargs='?', default=-1, help='ID of the contestant to be unseated..')
    contestant_unseatall = contestant_subparsers.add_parser('unseatall', help='Unseat all seated contestants.')
    contestant_genpass = contestant_subparsers.add_parser('genpass', help='Generate password for a contestant.')
    contestant_genpass.add_argument('id', type=int, nargs='?', default=-1, const=-1,
                                    help='ID of the contestant to ' 'generate password.')
    contestant_genpass.add_argument('--override', '-o', action='store_true', default=False, help='Override the existing password.')
    contestant_genpass.add_argument('--pwd-alphabet', type=str,
                                    default=string.ascii_lowercase + string.digits,
                                    help='Alphabet of the password.')
    contestant_genpass.add_argument('--pwd-length', type=int, default=8, help='Length of the password.')

    seat_parser = subparsers.add_parser('seat', help='Manage seats.')
    seat_subparsers = seat_parser.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    seat_subparsers.required = True
    seat_add = seat_subparsers.add_parser('add', help='Add a seat.')
    seat_add.add_argument('room', type=str)
    seat_add.add_argument('seat_id', type=str)
    seat_import = seat_subparsers.add_parser('import', help='Import seats from a tsv file.')
    seat_import.add_argument('file_path', type=Path, help='Path to the tsv file.')
    seat_remove = seat_subparsers.add_parser('remove', help='Remove a seat.')
    seat_remove.add_argument('room', type=str)
    seat_remove.add_argument('seat_id', type=str)
    seat_show = seat_subparsers.add_parser('show', help='Find out that who is using a specific seat.')
    seat_show.add_argument('room', type=str)
    seat_show.add_argument('seat_id', type=str)
    seat_showroom = seat_subparsers.add_parser('showroom', help='Show a room.')
    seat_showroom.add_argument('room', type=str)
    seat_where = seat_subparsers.add_parser('where', help='Find out where is a team seated.')
    seat_where.add_argument('team_id', type=int)

    affiliation_parser = subparsers.add_parser('affiliation', help='Manage affiliations.')
    affiliation_subparsers = affiliation_parser.add_subparsers(title='actions', dest='subaction',
                                                               parser_class=SuppressingParser)
    affiliation_subparsers.required = True
    affiliation_add = affiliation_subparsers.add_parser('add', help='Add a affiliation.')
    affiliation_import = affiliation_subparsers.add_parser('import', help='Import affiliations from a tsv file.')
    affiliation_import.add_argument('file_path', type=Path, help='Path to the tsv file.')
    affiliation_remove = affiliation_subparsers.add_parser('remove', help='Remove a affiliation by its externalid.')
    affiliation_remove.add_argument('externalid', type=str)
    affiliation_show = affiliation_subparsers.add_parser('show', help='Show information of an affiliation.')
    affiliation_show.add_argument('externalid', type=str, nargs='?', default=None, const=None, help='Externalid of the affiliation. Ignore it to print all affiliations.')

    export_parser = subparsers.add_parser('export', help='Export data.')
    export_subparsers = export_parser.add_subparsers(title='actions', dest='subaction', parser_class=SuppressingParser)
    export_subparsers.required = True
    export_domjudge = export_subparsers.add_parser('domjudge', help='Export accounts.tsv and teams.json for DOMJudge.')
    export_contestants = export_subparsers.add_parser('contestants', help='Export contestant information.')

    return parser


def run_parsed_arguments(args):
    config.args = args
    config.set_default_args()

    action = config.args.action

    if action == 'contest' and config.args.subaction == 'create':
        contest.create_contest()
        return

    # Ensure that current directory is the contest directory.
    contest.ensure_contest_directory()
    # Load the seats.
    seat.get_seats()
    # Load the affiliations.
    affiliation.get_affiliations()
    # Preload the contest.
    contest.get_contest()
    # Preload the contestants.
    contestant.get_contestants()

    if action == 'contest':
        subaction = config.args.subaction
        if subaction in ['lock', 'unlock']:
            contest.toggle_lock(subaction == 'lock')
        if subaction == 'show':
            contest.get_contest().print()
        return

    if action == 'contestant':
        subaction = config.args.subaction

        if contest.contest_locked()[0] and subaction in ['add', 'import', 'remove', 'seat', 'seatall', 'unseat', 'unseatall', 'genpass']:
            error('Contest "{}" has been locked.'.format(contest.get_contest().title))

        if subaction == 'add':
            contestant.create_contestant_interactive()
        if subaction == 'import':
            contestant.import_contestant(config.args.file_path)
        if subaction == 'remove':
            contestant.remove_contestant(config.args.id)
        if subaction == 'show':
            if config.args.id != -1:
                contestant.show_information(config.args.id, config.args.print_password)
            else:
                contestant.show_information_all(config.args.print_password)
        if subaction == 'seat':
            contestant.seat_contestant(config.args.id, manual=config.args.manual_seat, random_apply=config.args.random_apply_seat, override=config.args.override_seat)
        if subaction == 'seatall':
            contestant.seat_all_contestants(random_apply=config.args.random_apply_seat)
        if subaction == 'unseat':
            contestant.unseat_contestant(config.args.id)
        if subaction == 'unseatall':
            contestant.unseat_all_contestant()
        if subaction == 'genpass':
            if config.args.id != -1:
                contestant.generate_password(config.args.id, config.args.pwd_alphabet, config.args.pwd_length,
                                             config.args.override)
            else:
                contestant.generate_password_for_all(config.args.pwd_alphabet, config.args.pwd_length, config.args.override)
        return

    if action == 'seat':
        subaction = config.args.subaction

        if contest.contest_locked()[0] and subaction in ['add', 'import', 'remove']:
            error('Contest "{}" has been locked.'.format(contest.get_contest().title))

        if subaction == 'add':
            seat.create_seat_interactive()
        if subaction == 'import':
            seat.import_seats(config.args.file_path)
        if subaction == 'remove':
            seat.remove_seat(config.args.room, config.args.seat_id)
        if subaction == 'show':
            seat.show_seat(seat.Seat(config.args.room, config.args.seat_id))
        if subaction == 'showroom':
            seat.show_room(config.args.room)
        if subaction == 'where':
            contestant.query_team_seat(config.args.team_id)

        return

    if action == 'affiliation':
        subaction = config.args.subaction

        if contest.contest_locked()[0] and subaction in ['add', 'import', 'remove']:
            error('Contest "{}" has been locked.'.format(contest.get_contest().title))

        if subaction == 'add':
            affiliation.create_affiliation_interactive()
        if subaction == 'import':
            affiliation.import_affiliations(config.args.file_path)
        if subaction == 'remove':
            affiliation.remove_affiliation(config.args.externalid)
        if subaction == 'show':
            if config.args.externalid:
                affiliation.show_affiliation(config.args.externalid)
            else:
                affiliation.show_all_affiliations()

        return

    print(config.args)


def main():
    def interrupt_handler(sig, frame):
        fatal('Running interrupted')

    signal.signal(signal.SIGINT, interrupt_handler)
    parser = build_parser()
    run_parsed_arguments(parser.parse_args())


if __name__ == '__main__':
    main()
