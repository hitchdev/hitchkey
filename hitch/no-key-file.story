No key file found:
  based on: prerequisites
  about: |
    When no key.py file is found, say so.
  steps:
  - Run:
      cmd: |
        cd /home/
        hk command
      exit code: 1
      will output: |-
        key.py not found in the following directories:

        /home/hitch
        /home

        Create a key.py file in a convenient project directory to begin.
