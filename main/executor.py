import queue
import subprocess


class Executor():
    def execute(self, commands):
        pass


class DefaultExecutor(Executor):
    def execute(self, commands):
        # Execute the command
        for cmd in commands:
            if len(cmd) > 0:
                if cmd[0] == "/usr/bin/xdotool":
                    subprocess.call(cmd)
                else:
                    # print(cmd)
                    subprocess.Popen(
                        cmd,
                        shell=False,
                        stdin=None,
                        stdout=None,
                        stderr=None,
                        close_fds=True)
