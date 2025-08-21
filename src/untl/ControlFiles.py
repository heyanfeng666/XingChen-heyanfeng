import os

import src.State
from pathlib import Path


class CtrlFiles:
    name: str = None
    FilePath: str = None

    file = None

    def __init__(self, name, filepath, mode):
        self.name = name
        self.FilePath = filepath

        if Path(filepath).exists():
            open(self.FilePath, 'w', encoding='utf-8').close()
        file = open(self.FilePath, mode)
        self.file = file

    def WriteInFiles(self, content, seek=0):
        try:
            self.file.seek(seek)
            self.file.write(content)
        except IOError as e:
            raise e
        except Exception as e:
            raise e
        return src.State.ReturnState.SUCCESS

    def ReadInFiles(self, seek=0, count=None):
        try:
            self.file.seek(seek)
            return self.file.read(count), src.State.ReturnState.SUCCESS
        except IOError as e:
            raise e
        except Exception as e:
            raise e

    def CloseFiles(self):
        try:
            self.file.close()
        except IOError as e:
            raise e
        except Exception as e:
            raise e
        return src.State.ReturnState.SUCCESS

    def CheckFiles(self, filepath):
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return src.State.ReturnState.SUCCESS
        else:
            return src.State.ReturnState.FAIL



def CreateDirs(dirspath: str):
    os.makedirs(dirspath, exist_ok=True)
    return src.State.ReturnState.SUCCESS


def DeleteDirs(dirspath: str):
    os.rmdir(dirspath)
    return src.State.ReturnState.SUCCESS


def CheckDirs(dirspath: str):
    if os.path.exists(dirspath) and os.path.isdir(dirspath):
        return src.State.ReturnState.SUCCESS
    else:
        return src.State.ReturnState.FAIL
