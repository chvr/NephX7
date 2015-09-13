import os
import shutil

__author__ = 'Chyros'

import sys


# ConfigEntry class =========================================================

class ConfigEntry:

    def __init__(self, name, source, destination, recursive=False):
        self._name = name
        self._source = source
        self._destination = destination
        self._recursive = recursive

    @property
    def get_name(self):
        return self._name

    @property
    def get_source(self):
        return self._source

    @property
    def get_destination(self):
        return self._destination

    @property
    def get_recursive(self):
        return self._recursive

    def __repr__(self):
        return self._tostring()

    def __str__(self):
        return self._tostring()

    def _tostring(self):
        return '{} [Name={}, Source={}, Destination={}, Recursive={}]'.format(ConfigEntry.__name__, self._name, self._source, self._destination, self._recursive)

# End of ConfigEntry class ==================================================


config_entries = [
    ConfigEntry('PyCharm Keymap Files', r'C:/Users/Chyros/.PyCharm40/config/keymaps/', r'C:/Users/Chyros/OneDrive/Config/PyCharm/keymaps/')
    , ConfigEntry('DarkSouls2 Saved Game Files', r'C:/Users/Chyros/AppData/Roaming/DarkSoulsII/011000010611cfdd/', r'C:/Users/Chyros/OneDrive/Config/DarkSouls2/savegames/')
    , ConfigEntry('Insanity Episode 01', r'C:/Users/Chyros/Desktop/insanity_ep01.txt', r'C:/Users/Chyros/OneDrive/Config/Workout/')
    , ConfigEntry('Insanity Episode 02', r'C:/Users/Chyros/Desktop/insanity_ep02.txt', r'C:/Users/Chyros/OneDrive/Config/Workout/')
    , ConfigEntry('Insanity General', r'C:/Users/Chyros/Desktop/insanity_general.xlsx', r'C:/Users/Chyros/OneDrive/Config/Workout/')
]


def main():
    print("Backup HX Settings v1.0.0")

    for entry in config_entries:
        backup_files(entry)

    sys.exit()


def backup_files(config_entry):
    """Backup file(s) to OneDrive"""
    print('Backing up {}...'.format(config_entry))
    _copy(config_entry.get_source, config_entry.get_destination, config_entry.get_recursive)


def _copy(src, dest, recursive=False, depth=0):
    if os.path.isfile(src):
        print('    {}'.format(os.path.dirname(src)))
        _copy_file(src, dest)
    elif os.path.isdir(src):
        if not recursive and depth > 0:
            print('        - Skipped directory \'{}\''.format(src))
            return
        else:
            print('    {}'.format(src))

        files = []
        dirs = []

        paths = os.listdir(src)
        for p in paths:
            if os.path.isfile(os.path.join(src, p)):
                files.append(os.path.join(src, p))
            else:
                dirs.append(os.path.join(src, p))

        for f in files:
            _copy_file(f, dest)

        for d in dirs:
            _copy(d, dest, recursive, depth=depth + 1)
    else:
        raise FileNotFoundError('source file \'{}\' not found'.format(src))


def _copy_file(src_path, dest):
    if not os.path.isfile(src_path):
        raise FileNotFoundError('source file \'{}\' not found'.format(src_path))

    src_file = os.path.basename(src_path)
    dest_path = dest
    dest_dir, dest_file = os.path.split(dest)
    if os.path.isfile(dest_dir):
        raise Exception('cannot create directory \'{}\' - a file with the same name exists'.format(dest_dir))

    if dest_file == '':
        dest_path = os.path.join(dest_dir, src_file)

    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)

    dest_path = shutil.copy(src_path, dest_path)
    print('        - Copied file \'{}\' as \'{}\''.format(
        src_file
        , dest_path
    ))


main()
