

SPECIFY_PYTHON_TO_CREATE_VIRTUALENV_WITH = """\
Create hitch virtualenv using specific python version
(e.g. /usr/bin/python3). Defaults to using python3 on the system path."""


SPECIFY_VIRTUALENV_TO_CREATE_HITCH_WITH = """\
Create hitch virtualenv using specific virtualenv
(e.g. /usr/bin/virtualenv). Defaults to using virtualenv on the system path."""


YOU_MUST_HAVE_VIRTUALENV_INSTALLED = """\
You must have virtualenv installed to use hitch.

Suggestions:

#1 Install via your system's package manager:
  - On Ubuntu/Debian : sudo apt-get install python-virtualenv
  - On Fedora        : sudo yum install python-virtualenv
  - On Arch          : sudo pacman -Sy python-virtualenv
  - On Mac OS X      : pip install --upgrade virtualenv

#2 Install via pip, e.g.:
  - sudo pip3 install --upgrade virtualenv"""


YOU_MUST_HAVE_PYTHON3_INSTALLED = """\
To use HitchKey, you must have python 3 installed.

To install:
  - On Ubuntu/Debian : sudo apt-get install python3
  - On Fedora        : sudo yum install python3
  - On Arch          : sudo pacman -Sy python3
  - On Mac OS X      : brew install python3
"""

YOU_MUST_HAVE_VERSION_ABOVE_PYTHON33 = """\
Hitch must have python 3.3 or higher installed to run.
Your app can run with earlier versions of python, but the
testing environment cannot.

Suggestions:

#1 You may need to run a sytem upgrade or upgrade your OS.
"""


HITCH_DIRECTORY_MOVED = """\
The hitch directory '{0}' was moved.
"Run 'hitch clean' then run 'hitch init' in this directory:
==> {1}
"""


HITCH_NOT_INITIALIZED = """\
Hitch has not been initialized in this directory,
or any of the directories beneath it:\n"""


SOMETHING_CORRUPTED = """\
WARNING: Hitch directory was corrupted. Run 'hitch clean' and hitch init again.
Please, if you think this is a bug, raise an issue at:\n

http://github.com/hitchtest/hitchkey/issues/
"""


SPACES_NOT_ALLOWED = """\
Spaces not allowed anywhere in the genpath:

{0}
"""
