from hitchtest import monitor
from commandlib import run
from simex import DefaultSimex
from commandlib import Command
import hitchpython
import hitchserve
import hitchtest
import hitchvm
import kaching
import time
from hitchvm import StandardBox, Vagrant
from path import Path
from pexpect import EOF
import sys


class ExecutionEngine(hitchtest.ExecutionEngine):
    """Hitch bootstrap engine tester."""

    def set_up(self):
        self.path.project = self.path.engine.parent
        self.path.state = self.path.engine.parent.joinpath("state")
        self.path.flake8 = Path(sys.argv[0]).abspath().parent.joinpath("flake8")

        box = StandardBox(Path("~/.hitchpkg").expand(), "ubuntu-trusty-64")
        vm = Vagrant(self.path.state, box)
        vm = vm.sync(self.path.project, "/hitchkey/")
        self.running_vm = vm.up()

    def run(self, cmd=None, expect=None, timeout=240):
        self.process = self.running_vm.cmd(cmd).pexpect()

        if sys.stdout.isatty():
            self.process.logfile = sys.stdout.buffer
        else:
            self.process.logfile = sys.stdout


        if expect is not None:
            self.process.expect(expect, timeout=timeout)
        self.process.expect(EOF, timeout=timeout)
        self.process.close()

    def lint(self, args=None):
        """Lint the source code."""
        run(self.pip("install", "flake8"))
        run(self.python_package.cmd.flake8(*args).in_dir(self.path.project))

    def sleep(self, duration):
        """Sleep for specified duration."""
        time.sleep(int(duration))

    def placeholder(self):
        """Placeholder to add a new test."""
        pass

    def flake8(self, directory, args=None):
        # Silently install flake8
        try:
            run(Command(self.path.flake8)(str(self.path.project.joinpath(directory)), *args).in_dir(self.path.project))
        except:
            raise RuntimeError("flake8 failure")

    def pause(self, message=""):
        self.ipython(message=message)

    def on_failure(self):
        self.pause(self.stacktrace.to_template())

    def on_success(self):
        """Ka-ching!"""
        if self.settings.get("kaching", False):
            kaching.win()
        if self.settings.get("pause_on_success", False):
            self.pause(message="SUCCESS")

    def tear_down(self):
        """Clean out the state directory."""
        if hasattr(self, 'running_vm'):
            if self.settings.get("debug", False):
                self.running_vm.halt()
            else:
                self.running_vm.destroy()
