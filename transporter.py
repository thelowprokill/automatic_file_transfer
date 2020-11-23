from paramiko import SSHClient, AutoAddPolicy
from getpass  import getuser
from datetime import datetime
import os
import sys
import stat
import file_downloader as fd
import file_uploader   as fu
import time

class transporter:
    def __init__(self, message, config, set_mode):
        self.message  = message
        self.config   = config
        self.set_mod  = set_mode
        self.has_lock = False
        self.file_downloader = fd.file_downloader(self.config, self.message, self.mode)
        self.file_uploader   = fu.file_uploader  (self.config, self.message, self.mode)
        self.current_time = datetime.now()

    def tick(self):
        pass

    def find_changed_files(self):
        ts = os.path.getmtime(self.config.LOCAL_DIR + "version.info")
        self.message("og timestamp = {}".format(ts))
        dt = datetime.fromtimestamp(ts)
        self.message("dt           = {}".format(dt))
        dt_ts = time.mktime(dt.timetuple())
        self.message("dt timestamp = {}".format(dt_ts))
        return []

    def close_connection(self):
        if self.has_lock:
            self.unlock()
        try:
            self.ssh.close()
            self.scp.close()
            self.message("Connection closed")
        except:
            self.message("Error: Failed to close ssh connection")

    def mode(self, m):
        try:
            self.set_mode(m)
        except:
            pass

    def scp_connect(self):
        try:
            self.ssh = SSHClient()
            self.ssh.load_system_host_keys(self.config.SSH_KEYS)
            self.ssh.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh.connect(self.config.SSH_HOST, username=self.config.SSH_USER, port=self.config.SSH_PORT)
            self.scp = self.ssh.open_sftp()
            return 0
        except:
            self.message("Error, Failed to establish connection to server at {}@{}".format(self.config.SSH_USER, self.config.SSH_HOST))
            return -1


    def lock(self):
        self.message("Checking for lock")
        try:
            item = self.scp.listdir_attr(self.config.SSH_DIR)
            if not (stat.S_ISDIR(item[0].st_mode) or stat.S_ISREG(item[0].st_mode)):
                self.message("Error: remote directory {} does not exist".format(self.config.SSH_DIR))
                return False
        except:
            self.message("Error: remote directory {} does not exist".format(self.config.SSH_DIR))
            return False
        try:
            lock = self.scp.open(self.config.SSH_DIR + self.config.LOCK_FILE, 'r')
            self.message("Error: lock file exists. Another machine is connected to server using username {}.\nIf you belive this to be in error.\nVerify no other machine is connected then manually delete lock file.\nWARNING: manually removing lock file can cause loss of data.".format(lock.readline()))
            return False
        except:
            pass
        try:
            lock = self.scp.open(self.config.SSH_DIR + self.config.LOCK_FILE, 'w+')
            lock.write(getuser())
            lock.close()
        except:
            self.message("Error: lock file exists. Another machine is connected to server.\nIf you belive this to be in error.\nVerify no other machine is connected then manually delete lock file.\nWARNING: manually removing lock file can cause loss of data.")
            return False
        try:
            lock = self.scp.open(self.config.SSH_DIR + self.config.LOCK_FILE, 'r')
            lock_contents = lock.readline()
            if lock_contents == getuser():
                self.message("Lock obtained")
                self.has_lock = True
                return True
        except:
            self.message("Lock file corrupted")
        return False

    def unlock(self):
        try:
            self.scp.remove(self.config.SSH_DIR + self.config.LOCK_FILE)
            self.message("Lock Removed")
            self.has_lock = False
            return True
        except:
            self.message("Lock Removal Failed")
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
            self.file_downloader.download_files(self.scp)
            self.message("Download Successful")
            self.colse_connection()
            return 0
        except:
            self.message("Download Failed")
            self.close_connection()
            return -3
        self.close_connection()
        return -4


    def upload(self, force=False):
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

        #files = ['hota_random/jon_naomi/save_01', 'hota_random/jon_naomi/save_02', 'hota_random/jon_naomi/save_03']
        files = self.find_changed_files()
        if len(files) > 0:
            try:
                self.file_uploader.upload_files(self.scp, files)
                self.message("Upload Successful")
                self.close_connection()
                return 0
            except:
                self.message("Upload Failed")
                self.close_connection()
                return -3
        else:
            self.message("No changes detected")
        self.close_connection()
        return -4

    # > 0 download
    # < 0 upload
    # highest version number
    # true false remote exists
    def scp_check_version(self):
        self.message("Checking for new version")
        try:
            item = self.scp.listdir_attr(self.config.SSH_DIR)
            if not (stat.S_ISDIR(item[0].st_mode) or stat.S_ISREG(item[0].st_mode)):
                self.message("Error: remote directory {} does not exist".format(self.config.SSH_DIR))
                return 0, False
        except:
            self.message("Error: remote directory {} does not exist".format(self.config.SSH_DIR))
            return 0, False
        try:
            remote = self.scp.open(self.config.SSH_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message("Error: Failed to read remote version info")
            return 0, False
        try:
            self.remote_version_number = int(remote.readline())
        except:
            self.message("Failed to cast remote version\nversion errors may exist\ntry downloading update manually if auto download is unsuccessful")
            remote.close()
            local.close()
            return 0, True
        try:
            local = open(self.config.LOCAL_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message("Failed to read local version info. Downloading Files")
            remote.close()
        try:
            local_version_number = int(local.readline())
        except:
            local_version_number = 0

        self.message("Remote has version {}".format(self.remote_version_number))
        self.message("Local has version {}".format(local_version_number))
        try:
            remote.close()
        except:
            pass
        try:
            local.close()
        except:
            pass
        return self.remote_version_number - local_version_number, self.remote_version_number if self.remote_version_number > local_version_number else local_version_number, True
