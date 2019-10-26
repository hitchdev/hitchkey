# HitchKey

HitchKey is a python task runner.

It was designed to be write and run ad hoc project tasks like
building, running tests, generating documentation, linting,
reformatting and deploying code. It runs ad hoc tasks from a
file called key.py in an isolated, self-updating python 3
virtualenv.

hitch/hitchreqs.in:

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

The best way to install the bootstrapper is with [pipsi](https://github.com/mitsuhiko/pipsi):

```
pipsi install hitchkey
```

It's also safe to install in the system python with sudo pip (hitchkey is dependencyless):

```
sudo pip install hitchkey
```

You can then run this command in the root folder of a project you are in:

```
hk --tutorial key

hk helloworld
```

It will create a new directory called "hitch" and put five things in there:

* key.py - the commands which you can run with "hk".
* gen - a symlink to the gen folder (e.g. ~/.hitch/ltnd0x) which contains the hitchkey's python 3 virtualenv and build folder.
* hitchreqs.in - the python packages which you want installed in this virtualenv.
* hitchreqs.txt - the compiled / frozen list of all the packages (does not need to be edited by hand).
* __pycache__ - folder containing the compiled version of key.py.

Then opening hitch/key.py in a text editor and poking around.


## Using hitchkey when you already have a key.py

Once installed, you can simply cd to any project directory with a key.py file or a hitch/key.py file
and run 'hk' and it will set up the environment, installing all the packages specified in hitchreqs.txt.

## Why?

This project grew out of a bash script that I kept creating repeatedly called "dev.sh" that I used to
keep in the root of every project. I would use it to run various development environment workflow tasks
like rebuilding code, running tests or deploying.

Over time I found myself building more and more complex workflows, and it became easier just to 
use python and its ecosystem of packages.
