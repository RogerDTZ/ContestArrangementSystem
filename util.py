import sys
import re
import yaml
import json
import secrets
from pathlib import Path


def user_abort(msg=None):
    if msg:
        print('[INFO] User abort: {}'.format(msg))
    else:
        print('[INFO] Cancelled by user.')
    exit(0)


def info(msg):
    print('[INFO] {}'.format(msg))


def normal(msg):
    info(msg)
    exit(0)


def invalid_format(arg_name, arg_value):
    print('[Invalid format] {} is in wrong format: {}'.format(arg_name, arg_value))
    exit(1)


def invalid_arg(arg_name, arg_value):
    print('[Invalid argument] {} is invalid: {}'.format(arg_name, arg_value))
    exit(1)


def error(msg):
    print('[ERROR] {}'.format(msg))
    exit(1)


def fatal(msg):
    print('[FATAL] {}'.format(msg))
    exit(1)


def ask_variable(name, default=None):
    if default is None:
        while True:
            print(f"{name}: ", end='', file=sys.stderr)
            val = input()
            if val == '':
                print(f"{name} must not be empty!", file=sys.stderr)
            else:
                break
        return val
    else:
        print(f"{name} [{default}]: ", end='', file=sys.stderr)
        val = input()
        return default if val == '' else val


def ask_confirm(msg, default: bool):
    confirm = ask_variable('{} (y/n)'.format(msg), 'y' if default else 'n')[0]
    if confirm not in ['y', 'Y', 'n', 'N']:
        error('Please answer y/n.')
    return True if confirm in ['y', 'Y'] else False


def read_yaml(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def write_yaml(path: Path, data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data=data, stream=f, allow_unicode=True)


def read_tsv(path: Path) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    res = []
    for line in lines:
        if line.endswith('\n'):
            line = line[:-1]
        res.append(line.split('\t'))
    return res


def write_tsv(path: Path, data: list):
    with open(path, 'w', encoding='utf-8') as f:
        for line in data:
            for index in range(len(line)):
                value = line[index]
                f.write(str(value))
                if index < len(line) - 1:
                    f.write('\t')
            f.write('\n')


def read_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def write_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False))


def decode_range(data: str, range_name='range'):
    data = data.strip()
    if not re.match('[0-9]*-[0-9]*$', data):
        invalid_format(range_name, data)
    res = tuple(list(map(int, data.split('-'))))
    if res[0] > res[1]:
        invalid_arg(range_name, res)
    return res


def encode_range(low: int, high: int):
    return '{}-{}'.format(low, high)


def generate_random_password(alphabet, length):
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def table_line(width):
    return '+' + ('-' * width) + '+'


def table_row(content: str, width, left=-1):
    if left == -1:
        return '|' + content.center(width) + '|'
    return '|' + content.ljust(width - 2 * left).center(width) + '|'
