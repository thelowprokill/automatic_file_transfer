from paramiko   import SSHClient, AutoAddPolicy
from getpass    import getuser
from datetime   import datetime
import os
import sys
import stat
import file_downloader as fd
import file_uploader   as fu
import time_stamp      as ts
import time

class transporter:
    def __init__(self, message, config, set_mode):
        self.message  = message
        self.config   = config
        self.set_mode = set_mode
        self.has_lock = False
        self.active_upload   = False
        self.file_downloader = fd.file_downloader(self.config, self.message, self.mode)
        self.file_uploader   = fu.file_uploader  (self.config, self.message, self.mode)
        self.current_time = ts.grab(config, self.message)
        self.running = True
        self.temp_restrictions = []

    def kill(self):
        self.running = False

    def run(self):
        if self.active_upload:
            return

        self.active_upload = True
        self.temp_restrictions = []
        self.mode('cu')
        diff, version, exists = self.scp_check_version()
        if exists:
            files = self.find_changed_files()
            if len(files) > 0:
                if diff == 0:
                    self.bump_version()
                    diff = -1
                elif diff > 0:
                    self.temp_restrictions = files
                    self.mode('du')
                    self.download()
                    self.bump_version()
                    self.mode('uf')
                    self.upload(files)
                    diff = 0


            if diff > 0:
                self.mode('du')
                self.download()
            elif diff < 0 and len(files) > 0:
                self.mode('uf')
                self.upload(files)
            elif diff < 0:
                self.mode('uf')
                self.upload(upload_all = True)
            else:
                self.mode('up')
                self.message(2, "Up to date")
            diff, version, exists = self.scp_check_version()
            if diff != 0:
                self.message(0, "Failed to update")
            else:
                self.current_time = datetime.now()
                ts.push(self.current_time, self.config, self.message)
        self.active_upload = False

    def waiting(self):
        self.message(0, "Waiting...")
        self.mode('w')
        for i in range(self.config.UPDATE_DELAY):
            if not self.running:
                return
            time.sleep(1)

    def tick(self):
        while self.running:
            if not self.active_upload:
                self.run()
            self.waiting()
        self.message(0, "Final Upload")
        self.run()

    def find_changed_files(self, directory=""):
        files = []
        cur_dir = self.config.LOCAL_DIR[:len(self.config.LOCAL_DIR) - 1] + directory
        print(cur_dir)
        for item in os.listdir(cur_dir):
            if item not in self.config.IGNORE_FILES + [self.config.LOCK_FILE, self.config.VERSION_INFO]:
                if os.path.isfile(cur_dir + "/" + item):
                    file_time = datetime.fromtimestamp(os.path.getmtime(cur_dir + "/" + item))
                    new_file = directory + "/" + item
                    if file_time > self.current_time and new_file not in files:
                        files.append(new_file)
                        self.message(3, "Files {} added".format(cur_dir + "/" + item))
                elif os.path.isdir(cur_dir + "/" + item):
                    new_files = self.find_changed_files(directory + "/" + item)
                    self.message(3, "{} Files added from {}".format(len(new_files), cur_dir + "/" + item))
                    files = files + new_files
                else:
                    self.message(0, "What is that file? " + item)

        return files

    def close_connection(self):
        if self.has_lock:
            self.unlock()
        try:
            self.ssh.close()
            self.scp.close()
            self.message(1, "Connection closed")
        except:
            self.message(0, "Error: Failed to close ssh connection")

    def mode(self, m):
        try:
            self.set_mode(m)
        except:
            pass

    def scp_connect(self):
        self.mode('con')
        try:
            self.ssh = SSHClient()
            self.ssh.load_system_host_keys(self.config.SSH_KEYS)
            self.ssh.set_missing_host_key_policy(AutoAddPolicy())
            if self.config.USE_PASSWORD != 1:
                self.ssh.connect(self.config.SSH_HOST, username=self.config.SSH_USER, port=self.config.SSH_PORT)
            else:
                self.ssh.connect(self.config.SSH_HOST, username=self.config.SSH_USER, password=self.config.PASSWORD, port=self.config.SSH_PORT)
            self.scp = self.ssh.open_sftp()
            return 0
        except:
            self.message(0, "Error, Failed to establish connection to server at {}@{}".format(self.config.SSH_USER, self.config.SSH_HOST))
            return -1


    def lock(self):
        self.message(1, "Checking for lock")
        try:
            item = self.scp.listdir_attr(self.config.SSH_DIR)
            if not (stat.S_ISDIR(item[0].st_mode) or stat.S_ISREG(item[0].st_mode)):
                self.message(0, "Error: remote directory {} does not exist".format(self.config.SSH_DIR))
                return False
        except:
            self.message(0, "Error: remote directory {} does not exist".format(self.config.SSH_DIR))
            return False
        try:
            lock = self.scp.open(self.config.SSH_DIR + self.config.LOCK_FILE, 'r')
            self.message(0, "Error: lock file exists. Another machine is connected to server using username {}.\nIf you belive this to be in error.\nVerify no other machine is connected then manually delete lock file.\nWARNING: manually removing lock file can cause loss of data.".format(lock.readline()))
            return False
        except:
            pass
        try:
            lock = self.scp.open(self.config.SSH_DIR + self.config.LOCK_FILE, 'w+')
            lock.write(getuser())
            lock.close()
        except:
            self.message(0, "Error: lock file exists. Another machine is connected to server.\nIf you belive this to be in error.\nVerify no other machine is connected then manually delete lock file.\nWARNING: manually removing lock file can cause loss of data.")
            return False
        try:
            lock = self.scp.open(self.config.SSH_DIR + self.config.LOCK_FILE, 'r')
            lock_contents = lock.readline()
            if lock_contents == getuser():
                self.message(1, "Lock obtained")
                self.has_lock = True
                return True
        except:
            self.message(0, "Error: Lock file corrupted")
        return False

    def unlock(self):
        try:
            self.scp.remove(self.config.SSH_DIR + self.config.LOCK_FILE)
            self.message(1, "Lock Removed")
            self.has_lock = False
            return True
        except:
            self.message(0, "Error: Lock Removal Failed")
            return False


    # 0 is success
    # > 0 is working
    # < 0 is error
    def download(self, force=False):
        return_value = 0
        self.mode('c')
        tmp = self.scp_connect()
        if tmp == -1:
            self.close_connection()
            return -1

        self.mode('l')
        if force:
            self.unlock()
        if not self.lock():
            self.close_connection()
            return -2

        try:
            self.file_downloader.download_files(self.scp, self.current_time, temp_restrictions = self.temp_restrictions)
            self.message(0, "Download Successful")
            self.close_connection()
            return 0
        except:
            self.message(0, "Download Failed")
            self.close_connection()
            return -3
        self.close_connection()
        return -4


    def upload(self, files = [], upload_all=False, force=False):
        return_value = 0
        self.mode('c')
        tmp = self.scp_connect()
        if tmp == -1:
            self.close_connection()
            return -1

        self.mode('l')
        if force:
            self.unlock()
        if not self.lock():
            self.close_connection()
            return -2

        if len(files) > 0:
            self.bump_version()

        if upload_all:
            try:
                self.file_uploader.upload_files(self.scp)
                self.message(0, "Upload Successful")
                self.close_connection()
                return 0
            except:
                self.message(0, "Upload Failed")
                self.close_connection()
                return -3

        #files = self.find_changed_files()
        if len(files) > 0:
            self.bump_version()
            try:
            #if True:
                self.file_uploader.upload_files(self.scp, files)
                self.message(0, "Upload Successful")
                self.close_connection()
                return 0
            except:
                self.message(0, "Upload Failed")
                self.close_connection()
                return -3
        else:
            self.message(0, "No changes detected")
        self.close_connection()
        return -4

    # > 0 download
    # < 0 upload
    # highest version number
    # true false remote exists
    def scp_check_version(self):
        self.message(1, "Checking for new version")
        tmp = self.scp_connect()
        if tmp == -1:
            self.close_connection()
            return 0, -1, False
        try:
            item = self.scp.listdir_attr(self.config.SSH_DIR)
            if not (stat.S_ISDIR(item[0].st_mode) or stat.S_ISREG(item[0].st_mode)):
                self.message(0, "Error: remote directory {} does not exist".format(self.config.SSH_DIR))
                return 0, -1, False
        except:
            self.message(0, "Error: remote directory {} does not exist".format(self.config.SSH_DIR))
            return 0, -1, False
        try:
            remote = self.scp.open(self.config.SSH_DIR + self.config.VERSION_INFO, 'r')
        except:
            print(self.config.SSH_DIR + self.config.VERSION_INFO)
            self.message(0, "Error: Failed to read remote version info")
            return 0, -1, False
        try:
            self.remote_version_number = int(remote.readline())
        except:
            self.message(0, "Error: Failed to cast remote version\nversion errors may exist\ntry downloading update manually if auto download is unsuccessful")
            remote.close()
            local.close()
            return 0, self.remote_version_number, True
        try:
            local = open(self.config.LOCAL_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message(0, "Error: Failed to read local version info. Downloading Files")
            remote.close()
        try:
            local_version_number = int(local.readline())
        except:
            local_version_number = 0

        self.message(1, "Remote has version {}".format(self.remote_version_number))
        self.message(1, "Local has version {}".format(local_version_number))
        try:
            remote.close()
        except:
            pass
        try:
            local.close()
        except:
            pass
        self.close_connection()
        return self.remote_version_number - local_version_number, self.remote_version_number if self.remote_version_number > local_version_number else local_version_number, True

    def bump_version(self):
        try:
            local = open(self.config.LOCAL_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message(0, "Error: Failed to read local version info.")
            return -1
        try:
            local_version_number = int(local.readline())
        except:
            self.message(0, "Error: Failed to cast local version info.")
            return -1

        local.close()
        local = open(self.config.LOCAL_DIR + self.config.VERSION_INFO, 'w+')
        local.write(str(local_version_number + 1))
        local.close()
        return 0
