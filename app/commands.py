import os
import subprocess
import sys
from pathlib import Path

from .consts import APPEND_MODE, NEW_LINE, WRITE_MODE
from .history import History
from .jobs import Jobs
from .parser import InputParseResult

BUILTIN_COMMANDS = {"echo", "exit", "type", "pwd", "cd", "history", "jobs", "complete"}


class CommandExecutor:
    """Dispatches shell commands to their handlers."""

    def __init__(self, history: History, readline, jobs: Jobs):
        self._handlers = {
            "echo": self._cmd_echo,
            "type": self._cmd_type,
            "pwd": self._cmd_pwd,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
            "history": self._cmd_history,
            "jobs": self._cmd_jobs,
            "complete": self._cmd_complete
        }
        self._history = history
        self._jobs = jobs
        self._readline = readline

    def execute(self, parsed: InputParseResult) -> None:
        """Execute a command from a parsed input result."""
        full_args = [parsed.command] + parsed.args
        commands = self._split_by(full_args, "|")
        if len(commands) > 1:
            self._run_pipeline(commands, parsed)
            return

        handler = self._handlers.get(parsed.command)
        if handler:
            handler(parsed)
        else:
            self._execute_external(parsed)

    def _cmd_echo(self, p: InputParseResult):
        result = " ".join(p.args)
        self._output_result(p.file_to_write, p.std_type, result, "", p.append)

    def _cmd_type(self, p: InputParseResult):
        for name in p.args:
            if name in BUILTIN_COMMANDS:
                print(f"{name} is a shell builtin")
            else:
                full_path = self._get_execute_path(name)
                if full_path is not None:
                    print(f"{name} is {full_path}")
                else:
                    print(f"{name} not found")

    def _cmd_pwd(self, p: InputParseResult):
        print(os.getcwd())

    def _cmd_cd(self, p: InputParseResult):
        if len(p.args) == 0 or p.args[0] == "~":
            os.chdir(Path.home())
            return
        if len(p.args) > 2:
            print("bash: cd: too many arguments")
            return

        path = p.args[0]
        try:
            os.chdir(path)
        except FileNotFoundError:
            print(f"cd: {path}: No such file or directory")

    def _cmd_exit(self, p: InputParseResult):
        self._history.write_to_env_file()
        sys.exit()

    def _cmd_history(self, p: InputParseResult):
        if len(p.args) == 0:
            for i, item in enumerate(self._history):
                print(f"{i + 1} {item}")
            return

        if len(p.args) == 2 and p.args[0] == "-r":
            self._history.read_from_file(p.args[1])
            return

        if len(p.args) == 2 and p.args[0] == '-w':
            self._history.write_to_file(p.args[1], False)
            return

        if len(p.args) == 2 and p.args[0] == '-a':
            self._history.write_to_file(p.args[1], True)
            return

        if len(p.args) == 1 and p.args[0] == "-c":
            self._history.clear()
            return

        count = int(p.args[0])
        start = max(len(self._history) - count, 0)
        for i in range(start, len(self._history)):
            print(f"{i + 1} {self._history[i]}")

    def _cmd_jobs(self, p: InputParseResult):
        self._jobs.list_jobs()

    def _cmd_complete(self, p: InputParseResult):
        pass

    def _execute_external(self, p: InputParseResult):
        full_args = [p.command] + p.args

        if self._get_execute_path(p.command) is not None:
            if p.args[-1] == '&':
                self._jobs.run_job(full_args[:-1])
                return
            result = subprocess.run(
                full_args,
                capture_output=True,
                text=True,
                check=False,
            )
            self._output_result(
                p.file_to_write, p.std_type, result.stdout, result.stderr, p.append
            )
        else:
            print(f"{p.command}: command not found")

    def _run_pipeline(self, commands: list[list[str]], p: InputParseResult):
        """Run a pipeline of commands using fork/pipe."""
        prev_read_fd = None
        pids: list[int] = []

        for i, cmd in enumerate(commands):
            is_last = i == len(commands) - 1

            if not is_last:
                curr_read_fd, curr_write_fd = os.pipe()
                pid = self._fork_child(cmd[0], cmd[1:], prev_read_fd, curr_write_fd)

                if prev_read_fd is not None:
                    os.close(prev_read_fd)

                prev_read_fd = curr_read_fd
                os.close(curr_write_fd)
            else:
                pid = self._fork_child(cmd[0], cmd[1:], prev_read_fd, None)
                if prev_read_fd is not None:
                    os.close(prev_read_fd)

            pids.append(pid)

        os.waitpid(pids[-1], 0)

        for pid in pids[:-1]:
            os.waitpid(pid, 0)

    def _fork_child(
        self, cmd: str, args: list[str], read_fd: int | None, write_fd: int | None
    ) -> int:
        """Fork and execute a command in the child process."""
        pid = os.fork()

        if pid == 0:
            if write_fd is not None:
                os.dup2(write_fd, 1)
                os.close(write_fd)
            if read_fd is not None:
                os.dup2(read_fd, 0)
                os.close(read_fd)

            # Built-ins run in-process then exit
            handler = self._handlers.get(cmd)
            if handler:
                handler(InputParseResult(cmd, args, None, "stdout", False))
                os._exit(0)

            # External command
            try:
                os.execvp(cmd, [cmd] + args)
            except FileNotFoundError:
                print(f"{cmd}: command not found")
                os._exit(1)

        return pid


    def _get_execute_path(self, arg: str) -> str | None:
        PATH = os.environ.get("PATH")
        all_paths = PATH.split(os.pathsep)
        for path in all_paths:
            full_path = path + "/" + arg
            if os.path.exists(full_path) and os.access(full_path, os.X_OK):
                return full_path
        return None


    def _split_by(self, items: list, sep) -> list[list]:
        result = []
        group = []
        for item in items:
            if item == sep:
                result.append(group)
                group = []
            else:
                group.append(item)
        result.append(group)
        return result


    def _output_result(self, file_to_write, std_type, stdout, stderr, append):
        if len(stderr) > 0 and stderr[-1] == NEW_LINE:
            stderr = stderr[:-1]

        if file_to_write is not None:
            output_to_file = stdout if std_type == "stdout" else stderr
            output_to_console = stderr if std_type == "stdout" else stdout
            self._write_to_file(file_to_write, output_to_file, append)
            self._print_res(output_to_console)
        else:
            self._print_res(stdout)

        self._jobs.list_jobs(only_done=True)



    def _print_res(self, res: str):
        if res == "":
            return
        if res[-1] == NEW_LINE:
            print(res, end="")
        else:
            print(res)


    def _write_to_file(self, file_name: str, content: str, append: bool):
        mode = APPEND_MODE if append else WRITE_MODE
        with open(file_name, mode) as file:
            if os.stat(file_name).st_size > 0:
                file.write(NEW_LINE)
            file.write(content)
