# HitchKey

HitchKey is a python 3 framework to let you easily run short,
ad hoc python code snippets from the command line.

It is designed to be used to trigger tasks like building code,
running tests, generating documentation, linting, reformatting
code and deploying code.

Example [key.py](https://github.com/crdoconnor/strictyaml/blob/master/hitch/key.py)
from [StrictYAML](https://hitchdev.com/strictyaml) can be used.

```
$ hk

Usage: hk command [args]

          bdd - Run story matching keywords.
       docgen - Build documentation.
         rbdd - Run story matching keywords and rewrite if changed.
  regressfile - Run all stories in filename 'filename' in python 2 and 3.
   regression - Run regression testing - lint and then run all tests.
     reformat - Reformat using black and then relint.
         lint - Lint project code and hitch code.
       deploy - Deploy to pypi as specified version.

Run 'hk help [command]' to get more help on a particular command.
```

## Features

* Run "hk command" in any directory or subdirectory in your project and it will run the corresponding method in the key.py file.

* Automatically freezes new packages specified in hitchreqs.in in hitchreqs.txt and keeps the isolated project virtualenv  up to date every time a command is run.

* Creates a project build folder which can be easily accessed with a quick shortcut (DIR.gen) as well as all other commonly required directories (project directory, shared build path, etc.).

* Provides an inbuilt mechanism for bootstrapping various different kinds of hitchkey environments.


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
