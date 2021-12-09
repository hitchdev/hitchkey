from hitchstory import StoryCollection, BaseEngine, validate, exceptions, no_stacktrace_for
from strictyaml import MapPattern, Map, Str
from hitchrun import expected, DIR
from hitchstory import GivenDefinition, GivenProperty, InfoDefinition, InfoProperty
from icommandlib import ICommandError
from commandlib import Command, CommandError
from pathquery import pathquery
from strictyaml import Int
from commandlib import python
from templex import Templex
import hitchbuildvagrant
from path import Path
from hashlib import md5
import sys

def _current_version():
    return DIR.project.joinpath("VERSION").bytes().decode("utf8").rstrip()


class Engine(BaseEngine):
    """Engine for running tests and inspecting result."""
    given_definition = GivenDefinition(
        files=GivenProperty(MapPattern(Str(), Str())),
        setup=GivenProperty(Str()),
    )

    def __init__(self, paths, rewrite, debug):
        self.path = paths
        self._rewrite = rewrite
        self._debug = debug

    def set_up(self):
        from build import HitchKeyBuild
        self._build = HitchKeyBuild(self.path)
        self._build.ensure_built()

        self.path.state = self.path.gen.joinpath("state")

        self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        self.path.example = self.path.gen / "example"

        if self.path.example.exists():
            self.path.example.rmtree()
        self.path.example.makedirs()

        for filename, text in self.given.get("files", {}).items():
            filepath = self.path.example.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(text)

        #ubuntu = hitchbuildvagrant.Box("hitchkey", "ubuntu-trusty-64")\
                                  #.with_download_path(self.path.share)\
                                  #.which_syncs(self.path.project, "/hitchkey")

        #setup_code = self.given.get("setup", "")

        #class PythonSnapshot(hitchbuildvagrant.Snapshot):
            #def setup(self):
                #self.cmd(setup_code).run()
                #self.cmd("sudo apt-get install python-setuptools -y").run()
                #self.cmd("sudo apt-get install build-essential -y").run()
                #self.cmd("sudo apt-get install python-pip -y").run()
                #self.cmd("sudo apt-get install python-virtualenv -y").run()
                #self.cmd("sudo apt-get install python3 -y").run()
                #self.cmd("cd /hitchkey/ ; sudo pip install .").run()

        #setuphash = md5(setup_code.encode('utf8')).hexdigest()

        #self.snapshot = PythonSnapshot("hitchkey_{}".format(setuphash), ubuntu).with_build_path(self.path.gen)
        #self.snapshot.ensure_built()
        #self.snapshot.box.vagrant("rsync").run()
        #self.snapshot.cmd("cd /hitchkey/ ; sudo pip uninstall hitchkey -y ; sudo pip install .").run()

    @validate(timeout=Int(), exit_code=Int())
    @no_stacktrace_for(ICommandError)
    @no_stacktrace_for(AssertionError)
    def run(self, cmd=None, will_output=None, timeout=240, exit_code=0):
        process = self._build.cmd(cmd).interact().screensize(160, 100).run()
        process.wait_for_finish(timeout=timeout)

        actual_output = process.stripshot()

        if will_output is not None:
            try:
                assert will_output in actual_output
            except AssertionError:
                if self._rewrite:
                    self.current_step.update(**{"will output": actual_output})
                else:
                    raise

        assert process.exit_code == exit_code, "Exit code should be {} was {}, output:\n{}".format(
            exit_code,
            process.exit_code,
            actual_output,
        )

    def pause(self):
        import IPython
        IPython.embed()

    def on_failure(self, reason):
        if self._debug:
            import IPython
            IPython.embed()

    def tear_down(self):
        """Clean out the state directory."""
        pass


def _story_collection(rewrite=False, debug=False):
    return StoryCollection(pathquery(DIR.key).ext("story"), Engine(DIR, rewrite, debug))


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


@expected(exceptions.HitchStoryException)
def dbdd(*words):
    """
    Run story and rewrite in debug mode.
    """
    _story_collection(debug=True).shortcut(*words).play()


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


def clean():
    print("destroy all created vms")


def bash():
    """Run bash in podman."""
    from build import HitchKeyBuild
    hkb = HitchKeyBuild(DIR)
    hkb.ensure_built()
    hkb.cmd("bash").run()
    


def buildhk():
    from build import HitchKeyBuild
    hkb = HitchKeyBuild(DIR)
    hkb.ensure_built()
    hkb.cmd("hk", "--help").run()

@expected(CommandError)
def dogfoodhk():
    """Compile and install new bootstrap to dogfood."""
    bootstrap_path = DIR.project / "bootstrap"
    Command("go")("build", "hk.go").in_dir(bootstrap_path).run()
    bootstrap_path.joinpath("hk").copy("/home/colm/bin/hk")


DEBIAN = """Package: hitchkey
Version: {version}
Section: custom
Priority: optional
Architecture: amd64
Essential: no
Installed-Size: 3072
Maintainer: hitchdev.com
Description: HitchKey bootstrapper
"""

def debian():
    """Build debian package"""
    debdir = DIR.gen.joinpath("deb")
    version = _current_version()
    if debdir.exists():
        debdir.rmtree()
    packagedir = debdir / "hitchkey"
    packagedir.makedirs()
    packagedir.joinpath("DEBIAN").mkdir()
    packagedir.joinpath("DEBIAN", "control").write_text(DEBIAN.format(version=version))
    bindir = packagedir.joinpath("usr", "bin")
    bindir.makedirs()
    DIR.project.joinpath("bootstrap", "hk-linux-amd64").copy(bindir)
    Command("dpkg-deb", "--build", "hitchkey").in_dir(debdir).run()
    debdir.joinpath("hitchkey.deb").copy(
        DIR.project / "dist" / "hitchkey-{}.deb".format(version)
    )

@expected(CommandError)
def multiarch():
    """Build hk for multiple architectures."""
    bootstrap_path = DIR.project / "bootstrap"
    go = Command(bootstrap_path / "go" / "bin" / "go").in_dir(bootstrap_path)
    tar = Command("tar").in_dir(bootstrap_path)
    
    if not Path(go).exists():
        wget = Command("wget").in_dir(bootstrap_path)
        wget("wget", "-c", "https://dl.google.com/go/go1.14.2.linux-amd64.tar.gz").ignore_errors().run()
        tar("xvzf", "go1.14.2.linux-amd64.tar.gz").run()
    
    dist_path = DIR.project / "dist"
    
    if not dist_path.exists():
        dist_path.mkdir()

    print("Building for linux...")
    go("build", "-o", "hk-linux-amd64", "hk.go").with_env(GOOS="linux", GOARCH="amd64").run()
    bootstrap_path.joinpath("hk-linux-amd64").copy(dist_path)
    
    print("Building for mac...")
    go("build", "-o", "hk-darwin-amd64", "hk.go").with_env(GOOS="darwin", GOARCH="amd64").run()
    bootstrap_path.joinpath("hk-darwin-amd64").copy(dist_path)
    
    print("Building for windows...")
    go("build", "-o", "hk.exe", "hk.go").with_env(GOOS="windows", GOARCH="amd64").run()
    bootstrap_path.joinpath("hk.exe").copy(dist_path)
    
    print("Building debian installer...")
    debian()
    
    #print("Building MSI For windows...")
    #Command("wixl", "-v", "hk.wxs").in_dir(bootstrap_path).run()
    #bootstrap_path.joinpath("hk.msi").copy(dist_path)
