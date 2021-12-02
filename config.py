import argparse
import string

args = argparse.Namespace()


default_args = {
    'pwd_alphabet': string.ascii_lowercase + string.digits,
    'pwd_length': 8
}


def set_default_args():
    for arg, value in default_args.items():
        if not hasattr(args, arg):
            setattr(args, arg, value)
