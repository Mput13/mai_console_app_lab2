import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from src.shell import Shell


class TestShell(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir.name)
        self.shell = Shell()

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        self.test_dir.cleanup()

    def capture_output(self, func, *args):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            func(*args)
            return sys.stdout.getvalue().strip()
        finally:
            sys.stdout = old_stdout

    def create_test_files(self):
        os.mkdir('dir1')
        with open('file1.txt', 'w') as f:
            f.write('aboba')
        with open('file2.txt', 'w') as f:
            f.write('aboba aboba')

    def test_execute_command_unknown(self):
        with patch('logging.Logger.info') as mock_log:
            output = self.capture_output(self.shell.execute_command, ["aboba"])
            self.assertIn("Unknown command", output)
            mock_log.assert_called_with("ERROR: Unknown command")

    def test_ls_basic(self):
        self.create_test_files()
        output = self.capture_output(self.shell.ls)
        self.assertEqual(set(output.split()), {"dir1", "file1.txt", "file2.txt"})

    def test_ls_with_path(self):
        self.create_test_files()
        output = self.capture_output(self.shell.ls, ".")
        self.assertEqual(set(output.split()), {"dir1", "file1.txt", "file2.txt"})

    def test_ls_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.ls("wrong_path")

    def test_cd(self):
        os.mkdir('dir1')
        old_pwd = self.shell.pwd
        self.shell.cd("dir1")
        self.assertEqual(self.shell.pwd, old_pwd / "dir1")
        self.shell.cd("..")
        self.assertEqual(self.shell.pwd, old_pwd)
        self.shell.cd("~")
        self.assertEqual(self.shell.pwd, Path.home())

    def test_cd_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.cd("wrong_path")
        with self.assertRaises(ValueError):
            self.shell.cd()
        os.mkdir('dir1')
        with open('file.txt', 'w') as f:
            f.write('aboba')
        with self.assertRaises(NotADirectoryError):
            self.shell.cd("file.txt")

    def test_cat(self):
        with open('file1.txt', 'w') as f:
            f.write('aboba')
        output = self.capture_output(self.shell.cat, "file1.txt")
        self.assertEqual(output, "aboba")

    def test_cat_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.cat("wrong_path")
        os.mkdir('dir1')
        with self.assertRaises(IsADirectoryError):
            self.shell.cat("dir1")
        with self.assertRaises(ValueError):
            self.shell.cat()

    def test_cp_file(self):
        with open('file1.txt', 'w') as f:
            f.write('aboba')
        self.shell.cp("file1.txt", "file2.txt")
        self.assertTrue(os.path.exists('file2.txt'))
        with open('file2.txt', 'r') as f:
            self.assertEqual(f.read(), 'aboba')

    def test_cp_dir(self):
        os.mkdir('dir1')
        with open('dir1/file.txt', 'w') as f:
            f.write('aboba')
        self.shell.cp("-r", "dir1", "dir2")
        self.assertTrue(os.path.exists('dir2/file.txt'))

    def test_cp_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.cp("wrong_path", "dest")
        os.mkdir('dir1')
        with self.assertRaises(IsADirectoryError):
            self.shell.cp("dir1", "dest")
        with self.assertRaises(ValueError):
            self.shell.cp("file", "dest", "extra")

    def test_mv(self):
        with open('file1.txt', 'w') as f:
            f.write('aboba')
        self.shell.mv("file1.txt", "file2.txt")
        self.assertFalse(os.path.exists('file1.txt'))
        self.assertTrue(os.path.exists('file2.txt'))

    def test_mv_dir(self):
        os.mkdir('dir1')
        self.shell.mv("dir1", "dir2")
        self.assertFalse(os.path.exists('dir1'))
        self.assertTrue(os.path.exists('dir2'))

    def test_mv_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.mv("wrong_path", "dest")
        with self.assertRaises(ValueError):
            self.shell.mv("file")

    def test_rm_file(self):
        with open('file1.txt', 'w') as f:
            f.write('aboba')
        self.shell.rm("file1.txt")
        self.assertFalse(os.path.exists('file1.txt'))

    def test_rm_dir(self):
        os.mkdir('dir1')
        with patch('builtins.input', return_value='y'):
            self.shell.rm("-r", "dir1")
        self.assertFalse(os.path.exists('dir1'))

    def test_rm_dir_no_confirm(self):
        os.mkdir('dir1')
        with patch('builtins.input', return_value='n'):
            self.shell.rm("-r", "dir1")
        self.assertTrue(os.path.exists('dir1'))

    def test_rm_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.rm("wrong_path")
        os.mkdir('dir1')
        with self.assertRaises(IsADirectoryError):
            self.shell.rm("dir1")
        with self.assertRaises(ValueError):
            self.shell.rm()
        with self.assertRaises(PermissionError):
            self.shell.rm("/")

    def test_logging_success(self):
        with patch('logging.Logger.info') as mock_log:
            self.shell.execute_command(["ls"])
            mock_log.assert_called_with("ls")

    def test_logging_error(self):
        with patch('logging.Logger.info') as mock_log:
            with self.assertRaises(FileNotFoundError):
                self.shell.execute_command(["ls", "wrong_path"])
            calls = mock_log.call_args_list
            self.assertEqual(calls[0][0][0], "ls nonexistent")  # command attempt
            self.assertEqual(calls[1][0][0], "ERROR: No such file or directory")

    def test_execute_command_empty(self):
        self.shell.execute_command([])


if __name__ == '__main__':
    unittest.main()


class TestShell(unittest.TestCase):
    def setUp(self) -> None:
        self.test_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir.name)
        self.shell = Shell()

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        self.test_dir.cleanup()

    def capture_output(self, func, *args):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            func(*args)
            return sys.stdout.getvalue().strip()
        finally:
            sys.stdout = old_stdout

    def create_test_files(self):
        os.mkdir('dir1')
        with open('file1.txt', 'w') as f:
            f.write('aboba')
        with open('file2.txt', 'w') as f:
            f.write('aboba aboba')

    def test_execute_command_unknown(self):
        with patch('logging.Logger.info') as mock_log:
            output = self.capture_output(self.shell.execute_command, ["unknown"])
            self.assertIn("Unknown command", output)
            mock_log.assert_called_with("ERROR: Unknown command")

    def test_ls_basic(self):
        self.create_test_files()
        output = self.capture_output(self.shell.ls)
        self.assertEqual(set(output.split()), {"dir1", "file1.txt", "file2.txt"})

    def test_ls_detailed(self):
        self.create_test_files()
        with patch('datetime.datetime') as mock_dt:
            mock_dt.fromtimestamp.return_value.strftime.return_value = "Oct 01 12:00"
            output = self.capture_output(self.shell.ls, "-l")
            lines = output.split('\n')
            self.assertEqual(len(lines), 3)  # dir1, file1, file2
            # Check format, e.g., starts with 'd' for dir, '-' for file, has uid/gid, size, time, name

    def test_ls_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.ls("nonexistent")

    def test_cd(self):
        os.mkdir('dir1')
        old_pwd = self.shell.pwd
        self.shell.cd("dir1")
        self.assertEqual(self.shell.pwd, old_pwd / "dir1")
        self.shell.cd("..")
        self.assertEqual(self.shell.pwd, old_pwd)
        self.shell.cd("~")
        self.assertEqual(self.shell.pwd, Path.home())

    def test_cd_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.cd("nonexistent")
        with self.assertRaises(ValueError):
            self.shell.cd()

    def test_cat(self):
        with open('file1.txt', 'w') as f:
            f.write('content')
        output = self.capture_output(self.shell.cat, "file1.txt")
        self.assertEqual(output, "content")

    def test_cat_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.cat("nonexistent")
        os.mkdir('dir1')
        with self.assertRaises(IsADirectoryError):
            self.shell.cat("dir1")

    def test_cp_file(self):
        with open('file1.txt', 'w') as f:
            f.write('content')
        self.shell.cp("file1.txt", "file2.txt")
        self.assertTrue(os.path.exists('file2.txt'))
        with open('file2.txt', 'r') as f:
            self.assertEqual(f.read(), 'content')

    def test_cp_dir(self):
        os.mkdir('dir1')
        with open('dir1/file.txt', 'w') as f:
            f.write('content')
        self.shell.cp("-r", "dir1", "dir2")
        self.assertTrue(os.path.exists('dir2/file.txt'))

    def test_cp_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.cp("nonexistent", "dest")
        os.mkdir('dir1')
        with self.assertRaises(IsADirectoryError):
            self.shell.cp("dir1", "dest")

    def test_mv(self):
        with open('file1.txt', 'w') as f:
            f.write('content')
        self.shell.mv("file1.txt", "file2.txt")
        self.assertFalse(os.path.exists('file1.txt'))
        self.assertTrue(os.path.exists('file2.txt'))

    def test_mv_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.mv("nonexistent", "dest")

    def test_rm_file(self):
        with open('file1.txt', 'w') as f:
            f.write('content')
        self.shell.rm("file1.txt")
        self.assertFalse(os.path.exists('file1.txt'))

    def test_rm_dir(self):
        os.mkdir('dir1')
        with patch('builtins.input', return_value='y'):
            self.shell.rm("-r", "dir1")
        self.assertFalse(os.path.exists('dir1'))

    def test_rm_dir_no_confirm(self):
        os.mkdir('dir1')
        with patch('builtins.input', return_value='n'):
            self.shell.rm("-r", "dir1")
        self.assertTrue(os.path.exists('dir1'))

    def test_rm_invalid(self):
        with self.assertRaises(FileNotFoundError):
            self.shell.rm("nonexistent")
        os.mkdir('dir1')
        with self.assertRaises(IsADirectoryError):
            self.shell.rm("dir1")

    def test_logging_success(self):
        with patch('logging.Logger.info') as mock_log:
            self.shell.execute_command(["ls"])
            mock_log.assert_called_with("ls")

    def test_logging_error(self):
        with patch('logging.Logger.info') as mock_log:
            try:
                self.shell.execute_command(["ls", "nonexistent"])
            except:
                pass
            mock_log.assert_called_with("ERROR: No such file or directory")


if __name__ == '__main__':
    unittest.main()
