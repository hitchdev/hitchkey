# HitchKey

HitchKey is a python 3 command line framework for running ad hoc
project based tasks like building code, running tests, deploying, etc.

Example [key.py](https://github.com/crdoconnor/strictyaml/blob/master/hitch/key.py)
from [StrictYAML](https://hitchdev.com/strictyaml) can be used:

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

It was designed so that:

* You can run "hk command args" in any directory within your project and it will find the relevant key.py and run the code.
* You can use DIR.gen to access a build folder to put project related artefacts in (~/.hitch/io2522n5/).
* You can use DIR.cur to access the folder that "hk" was run from.
* You can use DIR.project to access the project folder and DIR.key to access the folder the key.py is in.
* You can use DIR.share folder to keep and use files shared across all projects (~/.hitch/share/).
* It sets up and uses its own isolated virtualenv to run key.py with.
* It will always keep the virtualenv packages up to date based upon what you specify in hitchreqs.in.

## Install

You can install the dependencyless hitchkey bootstrapper by doing:

```
sudo pip install hitchkey
```

If you are morally against the use of "sudo pip", I'd advise using "[pipsi](https://github.com/mitsuhiko/pipsi) install" instead.

## Using hitchkey when you already have a key.py

Once installed, you can simply cd to any project directory with a key.py file or a hitch/key.py file
and run 'hk' and it will set up the environment.

Run 'hk command' after that and it will run a command in key.py.

## Why?

This project grew out of a bash script that I kept creating repeatedly called "dev.sh" that I used to run
various development environment tasks. Over time I grew sophisticated tasks that needed python
and eventually I also started needing a cornucopia of packages installed in a python virtualenv.

