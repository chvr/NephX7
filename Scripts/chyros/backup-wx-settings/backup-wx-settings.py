__author__ = 'arifal'


INTERVAL_IN_SEC = 60 * 60 * 4  # 4 Hours

HOME_LOCATION = '/home/arifal'
CONFIG_LOCATION = '/home/arifal/k/wx-k/c/home'
config_files = [
    # source filename, relative directory, target relative directory (optional)
    ['Chyros.xml', '.PyCharm40/config/keymaps', 'PyCharm40/config/keymaps']
    , ['settings.json', '.config/Code/User', 'config/Code/User']
    , ['keybindings.json', '.config/Code/User', 'config/Code/User']
]


import os.path
import shutil
import time
import threading


task_backup = None

def backup():
    global task_backup

    print('Task: Backing up WX settings... (recurring)')

    for f in config_files:
        source_path = os.path.join(HOME_LOCATION, f[1], f[0])
        if not os.path.isfile(source_path):
            print('! File \'{}\' not found. Will not be copied.')
            continue

        if len(f) > 2:
            target_dir = os.path.join(CONFIG_LOCATION, f[2])
        else:
            target_dir = os.path.join(CONFIG_LOCATION, f[1])

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
            print('- Created directory \'{}\'.'.format(target_dir))

        target_path = os.path.join(target_dir, f[0])
        shutil.copyfile(source_path, target_path)

        print('- Copied file: {} to {}'.format(source_path, target_path))

    print('Task Complete!')

    task_backup = threading.Timer(INTERVAL_IN_SEC, backup)
    task_backup.start()


def main():
    backup()

    while True:
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:
    pass
finally:
    print('Aborting tasks...')
    task_backup.cancel()
