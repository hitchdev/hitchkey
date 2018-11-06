from hitchstory import StoryCollection, BaseEngine, validate, exceptions, no_stacktrace_for
from strictyaml import MapPattern, Map, Str
from hitchrun import expected, DIR
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from icommandlib import ICommandError
from commandlib import Command
from pathquery import pathquery
from strictyaml import Int
from commandlib import python
from templex import Templex
import hitchbuildvagrant
from path import Path
from hashlib import md5
import sys


class Engine(BaseEngine):
    """Engine for running tests and inspecting result."""
    given_definition = GivenDefinition(
        files=GivenProperty(MapPattern(Str(), Str())),
        setup=GivenProperty(Str()),
    )

    def __init__(self, paths, rewrite):
        self.path = paths
        self._rewrite = rewrite

    def set_up(self):
        self.path.state = self.path.gen.joinpath("state")

        self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        self.path.example = self.path.project / "example"

        if self.path.example.exists():
            self.path.example.rmtree()
        self.path.example.makedirs()

        for filename, text in self.given.get("files", {}).items():
            filepath = self.path.example.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(text)

        ubuntu = hitchbuildvagrant.Box("hitchkey", "ubuntu-trusty-64")\
                                  .with_download_path(self.path.share)\
                                  .which_syncs(self.path.project, "/hitchkey")

        setup_code = self.given.get("setup", "")

        class PythonSnapshot(hitchbuildvagrant.Snapshot):
            def setup(self):
                self.cmd(setup_code).run()
                self.cmd("cd /hitchkey/ ; sudo pip install .").run()

        setuphash = md5(setup_code.encode('utf8')).hexdigest()

        self.snapshot = PythonSnapshot("hitchkey_{}".format(setuphash), ubuntu).with_build_path(self.path.gen)
        self.snapshot.ensure_built()

    @validate(timeout=Int(), exit_code=Int())
    @no_stacktrace_for(ICommandError)
    def run(self, cmd=None, will_output=None, timeout=240, exit_code=None):
        process = self.snapshot.cmd(cmd.replace("\n", " ; ")).interact().run()
        process.wait_for_finish(timeout=timeout)

        actual_output = '\n'.join(process.stripshot().split("\n")[:-1])

        if will_output is not None:
            try:
                Templex(will_output).assert_match(actual_output)
            except AssertionError:
                if self._rewrite:
                    self.current_step.update(**{"will output": actual_output})
                else:
                    raise

        if exit_code is not None:
            assert process.exit_code == exit_code, "Exit code should be {} was {}".format(
                exit_code,
                process.exit_code
            )

    def file_exists(self, path):
        self.run("ls {0}".format(path))

    def tear_down(self):
        """Clean out the state directory."""
        if hasattr(self, 'snapshot'):
            self.snapshot.shutdown()


def _story_collection(rewrite=False):
    return StoryCollection(pathquery(DIR.key).ext("story"), Engine(DIR, rewrite))


@expected(exceptions.HitchStoryException)
def bdd(*words):
    """
    Run story.
    """
    _story_collection().shortcut(*words).play()


@expected(exceptions.HitchStoryException)
def rbdd(*words):
    """
    Run story and rewrite.
    """
    _story_collection(rewrite=True).shortcut(*words).play()


def regression():
    """
    Run all stories.
    """
    lint()
    _story_collection().ordered_by_name().play()


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
