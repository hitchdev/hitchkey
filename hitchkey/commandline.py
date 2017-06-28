"""High level command line interface to hitch."""
from hitchkey import utils
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

    python3, virtualenv = utils.check_python_and_virtualenv(
        None,
        None,
    )

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

    gensymlink = os.path.abspath("gen")

    if os.path.exists(gensymlink):
        genpath = os.path.realpath(gensymlink)
    else:
        genpath = new_hitch_dir()

    if not path.exists(genpath):
        makedirs(genpath)
        utils.check_call([
            virtualenv,
            path.join(genpath, "hvenv"),
            "--no-site-packages",
            "-p", python3
        ])
        with open(path.join(genpath, "hvenv", "linkfile"), 'w') as handle:
            handle.write(keypy_directory)
        utils.check_call([path.join(genpath, "hvenv", "bin", "pip"), "install", "hitchrun"])
        os.symlink(genpath, path.join(keypy_directory, "gen"))

    hitchrun = path.abspath(path.join(genpath, "hvenv", "bin", "hitchrun"))
    os.execvp(hitchrun, [hitchrun] + sys.argv[1:])


if __name__ == '__main__':
    run()
