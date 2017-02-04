Project hitch:
  scenario:
    - Run:
       cmd: cd /hitchkey/hitch/examples/hitch_subdirectory/projectdir ; h cat file.txt
       expect: project file contents
       timeout: 120
