import datetime
import logging.config
import os
import shutil
import stat
from pathlib import Path
from typing import List

from common.config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("shell")


class Shell:
    def __init__(self):
        self.pwd = Path.cwd()
        self.commands = {
            "ls": self.ls,
            "cd": self.cd,
            "cat": self.cat,
            "cp": self.cp,
            "mv": self.mv,
            "rm": self.rm,
        }

    def parse_command(self, line: str):
        return line.strip().split()

    def execute_command(self, tokens: List[str]):
        if not tokens:
            return
        line = " ".join(tokens)
        cmd = tokens[0]
        args = tokens[1:]
        logger.info(line)
        if cmd in self.commands:
            try:
                self.commands[cmd](*args)
            except Exception as e:
                print(str(e))
                logger.info(f"ERROR: {str(e)}")
        else:
            error = "Unknown command"
            print(error)
            logger.info(f"ERROR: {error}")

    def ls(self, *args: str):
        detailed = False
        path_str = None
        for arg in args:
            if arg == "-l":
                detailed = True
            else:
                path_str = arg
        path = self.pwd / Path(path_str) if path_str else self.pwd
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError("No such file or directory")
        if not path.is_dir():
            raise NotADirectoryError("Not a directory")
        for item in sorted(path.iterdir()):
            if detailed:
                st = item.stat()
                mode = stat.filemode(st.st_mode)
                owner = st.st_uid
                group = st.st_gid
                size = st.st_size
                mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%b %d %H:%M")
                print(f"{mode} {owner} {group} {size:>8} {mtime} {item.name}")
            else:
                print(item.name)

    def cd(self, *args: str):
        if len(args) != 1:
            raise ValueError("cd takes exactly one argument")
        arg = args[0]
        if arg == "~":
            new_path = Path.home()
        elif arg == "..":
            new_path = self.pwd.parent
        else:
            new_path = self.pwd / Path(arg)
        new_path = new_path.resolve()
        if not new_path.exists():
            raise FileNotFoundError("No such file or directory")
        if not new_path.is_dir():
            raise NotADirectoryError("Not a directory")
        self.pwd = new_path

    def cat(self, *args: str):
        if len(args) != 1:
            raise ValueError("cat takes exactly one argument")
        path = self.pwd / Path(args[0])
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError("No such file or directory")
        if path.is_dir():
            raise IsADirectoryError("Is a directory")
        with open(path, "r") as f:
            print(f.read(), end="")

    def cp(self, *args: str):
        r = False
        if len(args) > 0 and args[0] == "-r":
            r = True
            args = args[1:]
        if len(args) != 2:
            raise ValueError("cp requires source and destination")
        source = self.pwd / Path(args[0])
        dest = self.pwd / Path(args[1])
        source = source.resolve()
        dest = dest.resolve()
        if not source.exists():
            raise FileNotFoundError("No such file or directory")
        if source.is_dir() and not r:
            raise IsADirectoryError("omit -r for directories")
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy(source, dest)

    def mv(self, *args: str):
        if len(args) != 2:
            raise ValueError("mv requires source and destination")
        source = self.pwd / Path(args[0])
        dest = self.pwd / Path(args[1])
        source = source.resolve()
        dest = dest.resolve()
        if not source.exists():
            raise FileNotFoundError("No such file or directory")
        shutil.move(source, dest)

    def rm(self, *args: str):
        r = False
        if len(args) > 0 and args[0] == "-r":
            r = True
            args = args[1:]
        if len(args) != 1:
            raise ValueError("rm takes exactly one argument")
        path = self.pwd / Path(args[0])
        path = path.resolve()
        if str(path) == "/":
            raise PermissionError("cannot remove root directory")
        if path == self.pwd.parent.resolve():
            raise PermissionError("cannot remove parent directory")
        if not path.exists():
            raise FileNotFoundError("No such file or directory")
        if path.is_dir() and not r:
            raise IsADirectoryError("omit -r for directories")
        if path.is_dir():
            confirm = input(f"Remove directory '{path}'? (y/n) ")
            if confirm.lower() != "y":
                return
            shutil.rmtree(path)
        else:
            os.remove(path)

    # def grep(self, *args):
    #     r =

