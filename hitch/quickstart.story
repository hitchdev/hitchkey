Quickstart Skeleton:
  about: |
    Running "hk --skeleton key" will create a template
    with a basic key.py file.
  steps:
  - Run:
      cmd: |
        cd /hitchkey/example/
        hk --skeleton key
  - Run:
      cmd: cat /hitchkey/example/hitch/key.py
      will output: |-
        from commandlib import CommandError, Command
        from hitchrun import DIR, expected


        @expected(CommandError)
        def helloworld():
            """
            Say hello world.
            """
            DIR.gen.joinpath("hello.txt").write_text("Hello world")
            Command("cat", "hello.txt").in_dir(DIR.gen).run()


Quickstart Tutorial:
  about: |
    Running "hk --tutorial key" will create a tutorial
    template demonstrating the features of hitchkey.
  steps:
  - Run:
      cmd: |
        cd /hitchkey/example/
        hk --tutorial key
  - Run:
      cmd: ls /hitchkey/example/hitch/
      will output: |-
        hitchreqs.in  key.py  __pycache__
