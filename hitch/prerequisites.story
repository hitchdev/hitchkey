Prerequisites:
  about:
  given:
    setup: |
      sudo apt-get install python3 python-virtualenv -y

Python 3 not installed:
  based on: prerequisites
  about: |
    When python3 is not accessible on the path,
    a readable, actionable error is shown.
  steps:
  - Run:
      cmd: |
        sudo rm /usr/bin/python3
        hk command
      exit code: 1
      will output: |-
        To use HitchKey, you must have python 3 installed.

        To install:
          - On Ubuntu/Debian : sudo apt-get install python3
          - On Fedora        : sudo yum install python3
          - On Arch          : sudo pacman -Sy python3
          - On Mac OS X      : brew install python3


Virtualenv not installed:
  based on: prerequisites
  about: |
    When virtualenv is not installed, a readable,
    actionable error is shown.
  steps:
  - Run:
      cmd: |
        sudo rm /usr/bin/virtualenv
        hk command
      exit code: 1
      will output: |-
        You must have virtualenv installed to use hitch.

        Suggestions:

        #1 Install via your system's package manager:
          - On Ubuntu/Debian : sudo apt-get install python-virtualenv
          - On Fedora        : sudo yum install python-virtualenv
          - On Arch          : sudo pacman -Sy python-virtualenv
          - On Mac OS X      : pip install --upgrade virtualenv

        #2 Install via pip, e.g.:
