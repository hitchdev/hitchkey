Normal setup:
  description: |
    Demonstrate a simple example of running a command.
  preconditions:
    files:
      key.py: |
        def command():
            print("Command ran")
  scenario:
    - Run:
       cmd: cd /hitchkey/hitch/examples/ ; h command
       expect: Command ran

#mycomputer.ini setup:
  #scenario:
    #- Run:
       #cmd: cd /hitchkey/hitch/examples/mycomputer ; h command
       #expect: Command ran
    #- File exists: /home/vagrant/customgenpath/hvenv/bin/hitchrun

Project hitch:
  description: |
    Demonstrate a simple example of running a command in
    a hitch subdirectory.
  preconditions:
    files:
      hitch_subdirectory/hitch/key.py: |
        from hitchrun import DIR

        def cat(filename):
            print(DIR.cur.joinpath(filename).bytes().decode('utf8'))
      hitch_subdirectory/projectdir/file.txt: |
        project file contents
  scenario:
    - Run:
       cmd: cd /hitchkey/hitch/examples/hitch_subdirectory/projectdir ; h cat file.txt
       expect: project file contents
       timeout: 120

Python 3 not installed:
  description: |
    When python3 is not installed, a readable, actionable error should
    be thrown.
  scenario:
    - Run: sudo rm /usr/bin/python3
    - Run: cd /hitchkey ; sudo pip install .
    - Run:
       cmd: cd /hitchkey/hitch/examples ; h command
       expect: you must have python 3 installed

Virtualenv not installed:
  description: |
    When virtualenv is not installed, a readable, actionable error should
    be thrown.
  scenario:
    - Run: cd /hitchkey ; sudo pip install .
    - Run: sudo rm /usr/bin/virtualenv
    - Run:
       cmd: cd /hitchkey/hitch/examples ; h command
       expect: You must have virtualenv

No key file found:
  description: |
    When no key.py file is found, say so.
  scenario:
    - Run:
       cmd: h command
       expect: key.py not found in the following directories
