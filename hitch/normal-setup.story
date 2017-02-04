Normal setup:
  scenario:
    - Run:
       cmd: cd /hitchkey/hitch/examples/normal ; h command
       expect: Command ran

mycomputer.ini setup:
  scenario:
    - Run:
       cmd: cd /hitchkey/hitch/examples/mycomputer ; h command
       expect: Command ran
    - File exists: /home/vagrant/customgenpath/hvenv/bin/hitchrun
