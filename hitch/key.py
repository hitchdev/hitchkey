from hitchstory import StoryCollection, BaseEngine, validate
from hitchrun import Path, hitch_maintenance
from hitchvm import StandardBox, Vagrant
from commandlib import Command
from pathquery import pathq
from strictyaml import Int
from commandlib import python
import sys
from pexpect import EOF


KEYPATH = Path(__file__).abspath().dirname()
git = Command("git").in_dir(KEYPATH.parent)


class Paths(object):
    def __init__(self, keypath):
        self.keypath = keypath
        self.project = keypath.parent
        self.state = keypath.parent.joinpath("state")


class Engine(BaseEngine):
    def __init__(self, keypath):
        self.path = Paths(keypath)

    def set_up(self):
        box = StandardBox(Path("~/.hitchpkg").expand(), "ubuntu-trusty-64")
        self.vm = Vagrant("hitchkey", box, self.path.state)
        self.vm = self.vm.synced_with(self.path.project, "/hitchkey/")

        if not self.vm.snapshot_exists("ubuntu-1604-ready"):
            self.vm.up()
            self.long_run("sudo apt-get install python-setuptools -y")
            self.long_run("sudo apt-get install build-essential -y")
            self.long_run("sudo apt-get install python-pip -y")
            self.long_run("sudo apt-get install python-virtualenv -y")
            self.long_run("sudo apt-get install python3 -y")
            self.vm.take_snapshot("ubuntu-1604-ready")
            self.vm.halt()

        self.vm.restore_snapshot("ubuntu-1604-ready")
        self.vm.sync()

        self.run("cd /hitchkey ; sudo pip install .")

    def long_run(self, cmd):
        self.run(cmd, timeout=600)

    @validate(timeout=Int())
    def run(self, cmd=None, expect=None, timeout=240):
        self.process = self.vm.cmd(cmd).pexpect()

        if sys.stdout.isatty():
            self.process.logfile = sys.stdout.buffer
        else:
            self.process.logfile = sys.stdout

        if expect is not None:
            self.process.expect(expect, timeout=timeout)
        self.process.expect(EOF, timeout=timeout)
        self.process.close()

    def file_exists(self, path):
        self.run("ls {0}".format(path))

    def tear_down(self):
        """Clean out the state directory."""
        if hasattr(self, 'vm'):
            self.vm.halt()


STORY_COLLECTION = StoryCollection(pathq(KEYPATH).ext("story"), Engine(KEYPATH))


def test(*words):
    """
    Run test with words.
    """
    print(STORY_COLLECTION.shortcut(*words).play().report())


def ci():
    """
    Run all stories.
    """
    lint()
    print(STORY_COLLECTION.ordered_by_name().play().report())


def hitch(*args):
    """
    Hitch maintenance commands.
    """
    hitch_maintenance(*args)


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        KEYPATH.parent.joinpath("hitchkey"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        KEYPATH.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    KEYPATH.joinpath("VERSION").write_text(version)
    git("add", "VERSION").run()
    git("commit", "-m", "RELEASE: Bumped version").run()
    git("push").run()
    git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
    git("push", "origin", version).run()
    python("setup.py", "sdist", "upload").in_dir(KEYPATH.parent).run()


def clean():
    print("destroy all created vms")
