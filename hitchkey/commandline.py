"""High level command line interface to hitch."""
from os.path import join, ismount, exists, abspath, dirname, realpath
from os import path, makedirs
from hitchkey import utils
from shutil import rmtree
import random
import string
import sys
import os


def new_hitch_dir():
    """
    Create a new named hitchdir.
    """
    return path.join(
        path.expanduser("~/.hitch"),
        ''.join([
            random.choice(
                string.digits + string.ascii_lowercase
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

    while not ismount(checkdirectory):
        if exists("{0}{1}key.py".format(checkdirectory, os.sep)):
            keypy_filename = "{0}{1}key.py".format(checkdirectory, os.sep)
            break
        elif exists(join(checkdirectory, "hitch", "key.py")):
            keypy_filename = join(checkdirectory, "hitch", "key.py")
            break
        else:
            directories_checked.append(join(checkdirectory, "hitch"))
            directories_checked.append(checkdirectory)
            checkdirectory = abspath(join(checkdirectory, os.pardir))

    if not keypy_filename:
        sys.stderr.write("key.py not found in the following directories:\n\n")
        sys.stderr.write('\n'.join(directories_checked))
        sys.stderr.write("\n\nCreate a key.py file in a convenient project directory to begin.\n")
        sys.exit(1)

    keypy_directory = dirname(keypy_filename)

    gensymlink = abspath(join(keypy_directory, "gen"))

    if exists(gensymlink):
        genpath = realpath(gensymlink)
    else:
        genpath = new_hitch_dir()

    if not exists(genpath):
        makedirs(genpath)
        try:
            utils.check_call([
                virtualenv,
                join(genpath, "hvenv"),
                "--no-site-packages",
                "-p", python3
            ])
            utils.check_call([
                join(genpath, "hvenv", "bin", "pip"), "install", "hitchrun"
            ])
            with open(join(genpath, "hvenv", "linkfile"), 'w') as handle:
                handle.write(keypy_directory)
            os.symlink(genpath, join(keypy_directory, "gen"))
        except utils.CalledProcessError:
            rmtree(genpath, ignore_errors=True)
            sys.exit(1)
    hitchrun = abspath(join(genpath, "hvenv", "bin", "hitchrun"))
    os.execvp(hitchrun, [hitchrun] + sys.argv[1:])


if __name__ == '__main__':
    run()
