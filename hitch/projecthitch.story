Project hitch:
  scenario:
    - Run:
       cmd: cd /hitchkey/tests/projecthitch/projectdir ; h cat file.txt
       expect: project file contents
       timeout: 120
