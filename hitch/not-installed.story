Python 3 not installed:
  scenario:
    - Run: sudo rm /usr/bin/python3
    - Run: cd /hitchkey ; sudo pip install .
    - Run:
       cmd: cd /hitchkey/tests/simple ; h command
       expect: you must have python 3 installed

Virtualenv not installed:
  description: If virtualenv is not found, say so and abort.
  scenario:
    - Run: sudo rm /usr/bin/virtualenv
    - Run:
       cmd: cd /hitchkey/tests/simple ; h command
       expect: You must have virtualenv
