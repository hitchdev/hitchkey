Clean hitch gen folder:
  about: |
    hk --clean will remove 
  based on: run hitchkey command
  steps:
  - Run:
      cmd: |
        cd /hitchkey/example/hitch_subdirectory/projectdir
        hk --clean
  - Run:
      cmd: ls ~/.hitch/
      will output: share
