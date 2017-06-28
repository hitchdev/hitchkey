from hitchstory import StoryCollection, StorySchema, BaseEngine, validate, exceptions
from strictyaml import MapPattern, Map, Str
from hitchrun import hitch_maintenance, expected, DIR
from hitchvm import StandardBox, Vagrant
from commandlib import Command
from pathquery import pathq
from strictyaml import Int
from commandlib import python
import sys
from pexpect import EOF
from path import Path


class Engine(BaseEngine):
    """Engine for running tests and inspecting result."""
    schema = StorySchema(
        preconditions=Map({
            "files": MapPattern(Str(), Str()),
        }),
        about={
            "description": Str(),
        },
    )

    def __init__(self, paths):
        self.path = paths

    def set_up(self):
        self.path.state = self.path.gen.joinpath("state")

        self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        for filename, text in self.preconditions.get("files", {}).items():
            filepath = self.path.key.joinpath("examples").joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(text)

        box = StandardBox(Path("~/.hitchpkg").expand(), "ubuntu-trusty-64")
        self.vm = Vagrant("hitchkey", box, self.path.gen)
        self.vm = self.vm.synced_with(self.path.project, "/hitchkey/")

        if not self.vm.snapshot_exists("ubuntu-1604-installed"):
            if not self.vm.snapshot_exists("ubuntu-1604-ready"):
                self.vm.up()
                self.long_run("sudo apt-get install python-setuptools -y")
                self.long_run("sudo apt-get install build-essential -y")
                self.long_run("sudo apt-get install python-pip -y")
                self.long_run("sudo apt-get install python-virtualenv -y")
                self.long_run("sudo apt-get install python3 -y")
                self.run("virtualenv --python python3 ~/hvenv")
                self.vm.take_snapshot("ubuntu-1604-ready")
                self.vm.halt()
            self.vm.restore_snapshot("ubuntu-1604-ready")
            self.vm.sync()
            self.vm.take_snapshot("ubuntu-1604-installed")
            self.vm.halt()

        self.vm.restore_snapshot("ubuntu-1604-installed")
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


def _story_collection():
    return StoryCollection(pathq(DIR.key).ext("story"), Engine(DIR))


@expected(exceptions.HitchStoryException)
def test(*words):
    """
    Run test with words.
    """
    print(_story_collection().shortcut(*words).play().report())


def ci():
    """
    Run all stories.
    """
    lint()
    print(_story_collection().ordered_by_name().play().report())


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("hitchkey"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "hitchkey"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()



def clean():
    print("destroy all created vms")
