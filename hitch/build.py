from commandlib import Command
import hitchbuild
import os


class HitchKeyBuild(hitchbuild.HitchBuild):
    def __init__(self, paths):
        self._path = paths
        self._docker = Command("podman")
        self.example_dir = self._path.gen / "example"
    
    def build(self):
        self._docker(
            "build", self._path.project,
            "--network=host",
            "-f", "hitch/Dockerfile_test",
            "-t", "hitchkey_test",
        ).in_dir(self._path.project).run()
    
    @property
    def project_dir(self):
        return self._path.gen / "project"

    def cmd(self, args):
        return self._docker(
            "run",
            "-it",
            "-v", f"{self.project_dir}/:/home/example/project",
            "--user", "{uid}:{uid}".format(uid=os.getuid()),
            "hitchkey_test",
            "bash", "-c",
            args,
        )
