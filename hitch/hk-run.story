Run hitchkey command:
  based on: prerequisites
  about: |
    HitchKey will look for a key.py file in:
    
    1) current directory
    2) current directory/hitch directory
    3) parent directory
    4) parent directory/hitch directory
    5) parent's parent directory
    6) parent's parent directory/hitch directory
    etc.

    If the key.py file is found in one of those
    directories, an environment will be built to
    run the command and the command will be run.
  given:
    files:
      hitch_subdirectory/hitch/key.py: |
        from hitchrun import DIR

        def cat(filename):
            print(DIR.cur.joinpath(filename).bytes().decode('utf8'))

      hitch_subdirectory/projectdir/file.txt: |
        project file contents
  steps:
  - Run:
      cmd: echo hello
  - Run:
      cmd: |
        cd /hitchkey/example/hitch_subdirectory/projectdir
        hk --folder
        hk cat file.txt
      will output: project file contents
