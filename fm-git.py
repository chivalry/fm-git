#!/usr/bin/env python

__version__ = ['1.0.0', 'Charles Ross', '17-11-17']

import sys, tempfile, shutil, subprocess, pwd, getpass, logging, os, time

logging.basicConfig(format='%(levelname)s %(asctime)s: %(message)s',
                    level=logging.INFO,
                    datefmt='%m/%d/%Y %I:%M:%S %p')

def commit_to_repository(filename, repository, path, comment, username, password):
    '''Use parameters to commit the file to a git repository.
    
    Create a back of the served file, move the backup to the repository folder,
    prompt the user for a comment if one isn't provided, and commit the repository,
    and push to the server'''

    # Fix any missing characters at the end of the parameters.
    filename   = cond_append(filename, '.fmp12')
    repository = cond_append(repository, '/')
    path       = cond_append(path, '/')

    startup_vol = startup_drive_name()

    # Use absolute path, assuming applescript is in same directory.
    cmd = 'osascript ' + os.path.dirname(os.path.realpath(__file__)) + '/create-ddr.applescript'
    ddr_folder = subprocess.check_output(cmd, shell=True).splitlines()[0]
    time.sleep(0.5)
    shutil.move(os.path.expanduser("~/Desktop") + "/" + ddr_folder, repository + 'DDR/' + ddr_folder)

    cmd = 'fmsadmin backup {} -d filemac:/{}{} -k 0 -u {} -p {}'
    cmd = cmd.format(filename, startup_vol, repository, username, password)
    subprocess.call(cmd, shell=True)

    db_path = repository + 'Databases/'
    src_path = db_path + path + filename
    trg_path = repository + filename
    shutil.move(src_path, trg_path)
    shutil.rmtree(db_path)

    cmd = 'git add * ; git commit -m "{}" ; git push'.format(comment)
    subprocess.call(cmd, shell=True)

def startup_drive_name():
    '''Use AppleScript to return the name of the startup drive.'''
    ascript = 'tell application "System Events" to get (name of startup disk)'
    cmd = "osascript -e '{}'".format(ascript)
    return subprocess.check_output(cmd, shell=True).splitlines()[0]

def cond_append(string, suffix):
    '''Append the suffix if it doesn't already end the string.'''
    return string if string.endswith(suffix) else string + suffix

if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.exit('Usage: fm-git filename repository path comment username password')
    commit_to_repository(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
