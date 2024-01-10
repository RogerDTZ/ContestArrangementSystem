import time
import os
import xlsxwriter as xw

from util import *
import contest
import contestant
import seat
import affiliation


def export_domjudge_account(path, cid):
    data = list()
    data.append(['accounts', '1'])
    c = contestant.get_contestants()[cid]
    data.append(['team', c.name, c.get_account(), c.password])
    write_tsv(path, data)


def export_domjudge_accounts(path):
    data = list()
    data.append(['accounts', '1'])
    for _, c in contestant.get_contestants().items():
        data.append(['team', c.name, c.get_account(), c.password])
    write_tsv(path, data)


def export_domjudge_team(path, cid):
    data = list()
    c = contestant.get_contestants()[cid]
    item = dict()
    item['id'] = str(c.team_id)
    item['name'] = c.name
    item['room'] = c.seat_formatted_str
    item['organization_id'] = c.aff
    item['group_ids'] = [str(c.team_category)]
    data.append(item)
    write_json(path, data)


def export_domjudge_teams(path):
    data = list()
    for _, c in contestant.get_contestants().items():
        item = dict()
        item['id'] = str(c.team_id)
        item['name'] = c.name
        item['room'] = c.seat_formatted_str
        item['organization_id'] = c.aff
        item['group_ids'] = [str(c.team_category)]
        data.append(item)
    write_json(path, data)


def export_domjudge(contestant_id=-1):
    (Path('.') / 'export').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'domjudge').mkdir(exist_ok=True)

    if contestant_id == -1:
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
    else:
        root_path = Path('.') / 'export' / 'domjudge' / 'personal'
        root_path.mkdir(exist_ok=True)

        contestants = contestant.get_contestants()
        if contestant_id not in contestants:
            error('Contestant {} not found'.format(contestant_id))
        c = contestants[contestant_id]

        filename = '{}-{}-{}-{}'.format(str(c.id), c.aff, c.name, c.get_account())
        export_domjudge_account(root_path / (filename + '.tsv'), c.id)
        export_domjudge_team(root_path / (filename + '.json'), c.id)

        info("Successfully export DOMJudge data for contestant {}.".format(c.id))



def export_contestants(path, print_account_password):
    workbook = xw.Workbook(path)

    center_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
    })

    room_dict = dict()
    aff_dict = dict()

    if print_account_password:
        header = ['编号', '姓名', '学校', '学号', '座位', '账号', '密码']
    else:
        header = ['编号', '姓名', '学校', '学号', '座位']

    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    timestamp_ws = workbook.add_worksheet('Timestamp')
    timestamp_ws.activate()
    timestamp_ws.write(0, 0, cur_time)
    
    global_ws = workbook.add_worksheet('Global')
    global_ws.activate()
    # contestant id, name, aff, sid, seat, account, password
    if print_account_password:
        global_ws.write_row('A1', header, center_format)
    else:
        global_ws.write_row('A1', header, center_format)
    row_number = 2
    for _, c in contestant.get_contestants().items():
        row = 'A' + str(row_number)
        row_number += 1
        if print_account_password:
            data = [c.id, c.name, c.get_affiliation_fullname(), c.sid, c.seat_formatted_str, c.get_account(), c.password]
        else:
            data = [c.id, c.name, c.get_affiliation_fullname(), c.sid, c.seat_formatted_str]
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
        room_ws = workbook.add_worksheet(room[:30])  # sheet name should not exceed 30
        room_ws.activate()
        room_ws.write_row('A1', header, center_format)
        row_number = 2
        for c in data:
            row = 'A' + str(row_number)
            row_number += 1
            room_ws.write_row(row, c, center_format)

    for aff, data in aff_dict.items():
        aff_ws = workbook.add_worksheet(affiliation.get_affiliations()[aff][:30])  # sheet name should not exceed 30
        aff_ws.activate()
        aff_ws.write_row('A1', header, center_format)
        row_number = 2
        for c in data:
            row = 'A' + str(row_number)
            row_number += 1
            aff_ws.write_row(row, c, center_format)
    
    global_ws.activate()

    workbook.close()


def export_contestant_table():
    (Path('.') / 'export').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'contestants').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'contestants' / 'history').mkdir(exist_ok=True)

    cur_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
    root_path = Path('.') / 'export' / 'contestants' / 'history' / cur_time
    root_path.mkdir()

    filename_1 = '{}.xlsx'.format(contest.get_contest().title)
    filename_2 = '{} (accounts).xlsx'.format(contest.get_contest().title)

    export_contestants(root_path / filename_1, print_account_password=False)
    export_contestants(root_path / filename_2, print_account_password=True)

    normal_path = Path('.') / 'export' / 'contestants'
    os.system("cp '{}' '{}'".format(root_path / filename_1, normal_path / filename_1))
    os.system("cp '{}' '{}'".format(root_path / filename_2, normal_path / filename_2))
    with open(normal_path / 'timestamp.txt', 'w', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

    info('Successfully export contestant data.')


def export_sid_score(result_file):
    (Path('.') / 'export').mkdir(exist_ok=True)
    (Path('.') / 'export' / 'sid_score').mkdir(exist_ok=True)
    output_file =  Path('.') / 'export' / 'sid_score' / 'sid_score.tsv'

    with open(result_file, 'r', encoding='utf-8') as f:
        scoreboard = [line.strip().split('\t') for line in f.readlines()[1: ]]
    scoreboard = sorted(scoreboard, key=lambda record: (-int(record[3]), int(record[4])))

    contestants = contestant.get_contestants()
    
    if len(contestants) != len(scoreboard):
        warning(f"Expected {len(contestants)} lines, found {len(scoreboard)} lines in results.tsv")
    
    output = []
    for record in scoreboard:
        team_id = int(record[0])
        person = contestants[contestant.get_cid_from_tid(team_id)]
        score = int(record[3])
        if person.sid and len(person.sid) > 0:
            output.append('\t'.join([str(person.sid), person.name, str(score)]))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\t'.join(["学号", "姓名", "过题数"]) + '\n')
        f.write('\n'.join(output))
    info(f"Exported {len(output)} contestants' score with their SID")
