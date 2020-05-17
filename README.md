# HitchKey

HitchKey is a python task runner designed to run project tasks
like building code, running tests, generating docs, linting,
reformatting and triggering deployments.

It runs ad hoc tasks from a file called key.py with an isolated,
self-updating python 3 virtualenv. Installing packages for use
by your tasks is as simple as adding their names in the
requirements file and running your task.

It is unique as a task runner in that it attempts to *only* be
a task runner and provides a means to *install* tools to build
code, connect to servers, etc. rather than attempting to do so
itself.

It is especially well suited to team projects as the project
can be used to build consistent development environments and
development tasks that are more or less invariant no matter
which machine

hitch/key.py

```python
from commandlib import CommandError, Command, python, python_bin
from hitchrun import DIR, expected

# Usable path.py objects -- https://pathpy.readthedocs.io/en/stable/api.html

# DIR.gen -- build directory (~/.hitch/xxxxxx, where the symlink 'gen' links to)
# DIR.project -- the directory containng the "hitch" folder.
# DIR.key -- the directory this file - key.py is in.
# DIR.share -- ~/.hitch/share - build folder shared build artefacts.
# DIR.cur -- the directory "hk" was run in.


# If "expected" is used, no stacktrace will be displayed for that exception
@expected(CommandError)
def hello(argument):
    """
    Try running "hk hello world".
    """
    # https://pathpy.readthedocs.io/en/stable/api.html
    DIR.gen.joinpath("hello.txt").write_text(argument)

    # https://hitchdev.com/commandlib/
    Command("cat", "hello.txt").in_dir(DIR.gen).run()


@expected(CommandError)
def runcommand():
    """
    Run python 3 code with the hk virtualenv.
    """
    python("pythoncode.py").run()             # run python code using this project's virtualenv
    python_bin.python("pythoncode.py").run()  # equivalent
```

hitch/hitchreqs.in:

```
hitchrun
# add python packages here and they will be installed automagically
```



```
$ hk

Usage: hk command [args]

       hello - Try running "hk hello world".
  runcommand - Run python 3 code with the hk virtualenv.

Run 'hk help [command]' to get more help on a particular command.


  hk --upgradepip - Upgrade hitch virtualenv's setuptools and pip
     hk --upgrade - Upgrade all dependencies in hitchreqs.in
  hk --cleanshare - Delete ~/.hitch/share/ folder.
       hk --clean - Delete gen folder
```

## Getting started

First ensure that you do not have a virtualenv activated.

It's recommended that you install the bootstrap script in the system python
environment:

```
sudo pip install hitchkey
```

This script is small, dependencyless, works on python 2 and python 3 and has
just one executable command: hk. It is also safe to install using anaconda or
pipsi if you prefer.

```
hk --demo key

hk helloworld
```

This will create a new directory called "hitch" and put five things in there:

* ```key.py``` - the methods which you can run with "hk command".
* ```gen``` - a symlink to the gen folder (e.g. ~/.hitch/ltnd0x) which contains the hitchkey's python 3 virtualenv and build folder.
* ```hitchreqs.in``` - the python packages which you want installed in this virtualenv.
* ```hitchreqs.txt``` - the compiled and frozen list of all the packages (does not need to be edited by hand).
* ```__pycache__``` - folder containing the compiled version of key.py.

If you open hitch/key.py in a text editor and poke around and run 'hk' in that folder you can see what
it is capable of.


## Using hitchkey when you already have a key.py

Once installed, you can simply cd to any project directory with a key.py file or a hitch/key.py file
and run 'hk' and it will set up the environment, installing all the packages specified in hitchreqs.txt.

## Why hitchkey instead of make/pyinvoke/rake?

This project grew out of a bash script that I kept creating repeatedly called "dev.sh" that I used to
keep in the root of every project. I would use it to run various development environment workflow tasks
like rebuilding code, running tests or deploying.

Over time I found myself building more and more complex workflows, and it became easier just to 
use python and its ecosystem of packages.
