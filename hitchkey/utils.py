from sys import stderr, exit
from subprocess import call, PIPE, Popen, STDOUT
from hitchkey import languagestrings
from functools import reduce
from os import path, getcwd


class CalledProcessError(Exception):
    """Re-implemented CalledProcessError, since it is not available < python 2.7."""
    pass


def check_output(command, stdout=PIPE, stderr=PIPE):
    """Re-implemented subprocess.check_output since it is not available < python 2.7."""
    return Popen(command, stdout=stdout, stderr=stderr).communicate()[0]


def check_call(command, shell=False):
    """Re-implemented subprocess.check_call since it is not available < python 2.7."""
    process = Popen(command, shell=shell)
    process.communicate()
    if process.returncode != 0:
        raise CalledProcessError
    return


def stop_everything(sig, frame):
    """Exit hitch."""
    exit(1)


def check_python_and_virtualenv(python, virtualenv):
    """Check that virtualenv and python3 are available and usable."""
    if python is None:
        if call(["which", "python3"], stdout=PIPE, stderr=PIPE) != 0:
            stderr.write(languagestrings.YOU_MUST_HAVE_PYTHON3_INSTALLED)
            stderr.flush()
            exit(1)
        python3 = check_output(["which", "python3"]).decode('utf8').replace("\n", "")
    else:
        if path.exists(python):
            python3 = python
        else:
            stderr.write("{0} not found.\n\n".format(python))
            stderr.write(languagestrings.YOU_MUST_HAVE_PYTHON3_INSTALLED)
            exit(1)

    python_version = check_output([python3, "-V"], stderr=STDOUT).decode('utf8')
    replacements = ('Python ', ''), ('\n', '')
    str_version = reduce(lambda a, kv: a.replace(*kv), replacements, python_version)
    tuple_version = tuple([int(x) for x in str_version.split('.')[:2]])

    if tuple_version < (3, 3):
        stderr.write(languagestrings.YOU_MUST_HAVE_VERSION_ABOVE_PYTHON33)
        exit(1)

    if virtualenv is None:
        if call(["which", "virtualenv"], stdout=PIPE, stderr=PIPE) != 0:
            stderr.write(languagestrings.YOU_MUST_HAVE_VIRTUALENV_INSTALLED)
            stderr.flush()
            exit(1)
        virtualenv = check_output(["which", "virtualenv"]).decode('utf8').replace("\n", "")
    else:
        if path.exists(virtualenv):
            if python is None:
                python = path.join(path.dirname(virtualenv), "python")
        else:
            stderr.write("{0} not found.\n".format(virtualenv))
            exit(1)

    return python3, virtualenv


def fail_if_spaces_in_path(filepath):
    """Raise error if spaces are found in a path."""
    if " " in filepath:
        stderr.write(languagestrings.SPACES_NOT_ALLOWED.format(getcwd()))
        exit(1)
    return filepath


def read_config(filename):
    """
    Read a standard ini file without section headers.
    """
    properties = {}
    if path.exists(filename):
        with open(filename, 'r') as handle:
            for line in "".join(handle.readlines()).split("\n"):
                if line != "" and not line.startswith(";"):
                    if line.count("=") != 1:
                        stderr.write("Error reading {0}\n".format(filename))
                        stderr.write("Line '{0}' does not follow key=val\n".format(line))
                        exit(1)
                    key, value = line.split("=")
                    properties[key] = value
    return properties
