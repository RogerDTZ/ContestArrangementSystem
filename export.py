import time
import os
import xlsxwriter as xw

from util import *
import contest
import contestant
import seat
import affiliation


def export_domjudge_accounts(path):
    data = list()
    data.append(['accounts', '1'])
    for _, c in contestant.get_contestants().items():
        data.append(['team', c.name, c.get_account(), c.password])
    write_tsv(path, data)


def export_domjudge_teams(path):
    data = list()
    for _, c in contestant.get_contestants().items():
        item = dict()
        item['id'] = str(c.team_id)
        item['name'] = c.name
        item['room'] = c.seat_formatted_str
        item['organization_id'] = c.aff
        item['group_ids'] = [str(contest.get_contest().team_category_id)]
        data.append(item)
    write_json(path, data)


def export_domjudge():
    (Path('.') / 'export').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'domjudge').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'domjudge' / 'history').mkdir(exist_ok=True)

    cur_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    root_path = Path('.') / 'export' / 'domjudge' / 'history' / cur_time
    root_path.mkdir()

    export_domjudge_accounts(root_path / 'accounts.tsv')
    export_domjudge_teams(root_path / 'teams.json')

    normal_path = Path('.') / 'export' / 'domjudge'
    os.system("cp {} {}".format(root_path / 'accounts.tsv', normal_path / 'accounts.tsv'))
    os.system("cp {} {}".format(root_path / 'teams.json', normal_path / 'teams.json'))
    with open(normal_path / 'timestamp.txt', 'w', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    info('Successfully export DOMJudge data.')


def export_contestants(path):
    workbook = xw.Workbook(path)

    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
    })

    room_dict = dict()
    aff_dict = dict()

    global_ws = workbook.add_worksheet('Global')
    global_ws.activate()
    # contestant id, name, aff, sid, seat, account, password
    global_ws.write_row('A1', ['编号', '姓名', '学校', '学号', '座位', '账号', '密码'], center_format)
    row_number = 2
    for _, c in contestant.get_contestants().items():
        row = 'A' + str(row_number)
        row_number += 1
        data = [c.id, c.name, c.get_affiliation_fullname(), c.sid, c.seat_formatted_str, c.get_account(), c.password]
        global_ws.write_row(row, data, center_format)
        room = seat.decode_seat(c.seat_formatted_str).room
        if room not in room_dict:
            room_dict[room] = []
        room_dict[room].append(data)
        aff = c.aff
        if aff not in aff_dict:
            aff_dict[aff] = []
        aff_dict[aff].append(data)

    for room, data in room_dict.items():
        room_ws = workbook.add_worksheet(room)
        room_ws.activate()
        room_ws.write_row('A1', ['编号', '姓名', '学校', '学号', '座位', '账号', '密码'], center_format)
        row_number = 2
        for c in data:
            row = 'A' + str(row_number)
            row_number += 1
            room_ws.write_row(row, c, center_format)

    for aff, data in aff_dict.items():
        aff_ws = workbook.add_worksheet(affiliation.get_affiliations()[aff])
        aff_ws.activate()
        aff_ws.write_row('A1', ['编号', '姓名', '学校', '学号', '座位', '账号', '密码'], center_format)
        row_number = 2
        for c in data:
            row = 'A' + str(row_number)
            row_number += 1
            aff_ws.write_row(row, c, center_format)

    workbook.close()


def export_contestant_table():
    (Path('.') / 'export').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'contestants').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'contestants' / 'history').mkdir(exist_ok=True)

    cur_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    root_path = Path('.') / 'export' / 'contestants' / 'history' / cur_time
    root_path.mkdir()

    filename = '{}.xlsx'.format(contest.get_contest().title)

    export_contestants(root_path / filename)

    normal_path = Path('.') / 'export' / 'contestants'
    os.system("cp '{}' '{}'".format(root_path / filename, normal_path / filename))
    with open(normal_path / 'timestamp.txt', 'w', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    info('Successfully export contestant data.')

