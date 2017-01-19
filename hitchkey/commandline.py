"""High level command line interface to hitch."""
from hitchkey.utils import check_call, check_python_and_virtualenv
from os import path, makedirs
import random
import string
import sys
import os


def new_hitch_dir():
    return path.join(
        path.expanduser("~/.hitch"),
        ''.join([
            random.choice(
                string.digits + string.lowercase
            ) for _ in range(6)
        ])
    )


def run():
    checkdirectory = os.getcwd()
    directories_checked = []
    keypy_filename = None
    while not os.path.ismount(checkdirectory):
        directories_checked.append(checkdirectory)
        if os.path.exists("{0}{1}key.py".format(checkdirectory, os.sep)):
            keypy_filename = "{0}{1}key.py".format(checkdirectory, os.sep)
            break
        elif os.path.exists("{0}{1}hitch{1}key.py".format(checkdirectory, os.sep)):
            keypy_filename = "{0}{1}hitch{1}key.py".format(checkdirectory, os.sep)
            break
        else:
            checkdirectory = os.path.abspath(os.path.join(checkdirectory, os.pardir))

    if not keypy_filename:
        sys.stderr.write("key.py not found in the following directories:\n\n")
        sys.stderr.write('\n'.join(directories_checked))
        sys.stderr.write("\n\nSee http://hitchkey.readthedocs.org/en/latest/quickstart.html\n")
        sys.exit(1)

    keypy_directory = os.path.dirname(keypy_filename)
    hitchdir_location_file = path.join(keypy_directory, "hitchdir")

    check_python_and_virtualenv(None, None)

    if path.exists(hitchdir_location_file):
        with open(hitchdir_location_file, "r") as handle:
            hitchdir = handle.read()
    else:
        hitchdir = new_hitch_dir()
        with open(hitchdir_location_file, 'w') as handle:
            handle.write(hitchdir)

    if not path.exists(hitchdir):
        makedirs(hitchdir)
        check_call([
            "virtualenv",
            path.join(hitchdir, "hvenv"),
            "--no-site-packages",
            "-p", "python3"
        ])
        check_call([path.join(hitchdir, "hvenv", "bin", "pip"), "install", "hitchrun"])
        with open(path.join(hitchdir, "hvenv", "linkfile"), "w") as handle:
            handle.write(path.abspath(keypy_directory))

    hitchrun = path.abspath(path.join(hitchdir, "hvenv", "bin", "hitchrun"))
    os.execvp(hitchrun, [hitchrun] + sys.argv[1:])


if __name__ == '__main__':
    run()
