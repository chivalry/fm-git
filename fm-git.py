#!/usr/bin/env python

__version__ = ['1.0.0', 'Charles Ross', '17-11-17']

import sys, tempfile, shutil, subprocess, pwd, getpass, logging, os, time, argparse

logging.basicConfig(format='%(levelname)s %(asctime)s: %(message)s',
                    level=logging.INFO,
                    datefmt='%m/%d/%Y %I:%M:%S %p')

def commit_to_repository(filename, repository, path, comment, username, password):
    '''Use parameters to commit the file to a git repository.
    
    Create a backup of the served file, move the backup to the repository folder,
    and commit the repository using the provided comment, and push to the server'''

    filename = filename if filename.endswith('.fmp12') else filename + '.fmp12'
    startup_vol = startup_drive_name()

    create_ddr(repository)
    
    cmd = 'fmsadmin backup {} --dest filemac:/{}{} --keep 0 --username {} --password {}'
    cmd = cmd.format(filename, startup_vol, repository, username, password)
    subprocess.call(cmd, shell=True)

    db_path = os.path.join(repository, 'Databases')
    src_path = os.path.join(db_path, path, filename)
    trg_path = os.path.join(repository, filename)
    shutil.move(src_path, trg_path)
    shutil.rmtree(db_path)

    cmd = 'git add * ; git commit -m "{}" ; git push'.format(comment)
    subprocess.call(cmd, shell=True)

def startup_drive_name():
    '''Use AppleScript to return the name of the startup drive.'''

    ascript = 'tell application "System Events" to get (name of startup disk)'
    cmd = "osascript -e '{}'".format(ascript)
    return subprocess.check_output(cmd, shell=True).splitlines()[0]

def create_ddr(repository):
    '''Use AppleScript to create the DDR and return the timestamp name.'''
    
    parent_folder = os.path.dirname(os.path.realpath(__file__))
    ddr_script_path = os.path.join(parent_folder, 'create-ddr.applescript')
    cmd = 'osascript ' + ddr_script_path
    ddr_name = subprocess.check_output(cmd, shell=True).splitlines()[0]

    # Move to repository's DDR folder.
    src_ddr = os.path.join(os.path.expanduser("~/Desktop"), ddr_name)
    time.sleep(0.25)
    trg_ddr = os.path.join(repository, 'DDR')
    move_files(src_ddr, trg_ddr)

def move_files(src, dest):
    '''Move all the files in src to dest and delete src.'''

    for filename in os.listdir(src):
        filepath = os.path.join(src, filename)
        shutil.copy(filepath, dest)
    shutil.rmtree(src)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    if len(sys.argv) != 7:
        sys.exit('Usage: fm-git filename repository path comment username password')
    commit_to_repository(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
