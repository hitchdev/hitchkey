Quickstart:
  about: |
    Running "hk --quickstart simplekey" will create a template
    with 
  steps:
  - Run:
      cmd: |
        cd /hitchkey/example/
        hk --quickstart simplekey
  - Run:
      cmd: cat /hitchkey/example/hitch/key.py
      will output: |-
        from hitchrun import DIR


        def helloworld():
            """
            Print all of the available directories.
            """
            print(DIR.gen)
            print(DIR.key)
            print(DIR.project)
            print(DIR.share)
            print(DIR.cwd)
