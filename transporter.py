from paramiko import SSHClient, AutoAddPolicy
from getpass  import getuser
import os
import sys
import stat

class transporter:
    def __init__(self, message, config, set_mode):
        self.message  = message
        self.config   = config
        self.set_mod  = set_mode
        self.has_lock = False

    # 0 is success
    # > 0 is working
    # < 0 is error
    def update(self):
        return_value = 0
        self.mode('c')
        tmp = self.scp_connect()
        if tmp == -1:
            self.close_connection()
            return -1
        self.mode('l')
        if not self.lock():
            self.close_connection()
            return -5
        version, file_exists = self.scp_check_version()
        if version and file_exists:
            self.scp_get()
            self.message("Done")
        elif not file_exists:
            self.close_connection()
            return -2
        else:
            self.close_connection()
            self.message("Already have the latest data")
            return_value = 1
        self.close_connection()

        try:
            local = open(self.config.LOCAL_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message("Error: Failed to open local version info after update")
            return -3
        try:
            local_version = int(local.readline())
        except:
            self.message("Error: Failed to read local version info after update")
            return -3

        if local_version != self.remote_version:
            self.message("Local version = {}, Remote version = {}".format(local_version, self.remote_version))
            self.message("Error: Remote and local version numbers do not match")
            return -4

        return return_value


    def close_connection(self):
        if self.has_lock:
            try:
                scp.remove(self.config.SSH_DIR + self.config.LOCK_FILE)
                self.message("Lock freed")
            except:
                self.message("Error: Failed to release lock.")
        try:
            self.ssh.close()
            self.scp.close()
        except:
            self.message("Error: Failed to close ssh connection")

    def mode(self, m):
        try:
            self.set_mode(m)
        except:
            pass

    def scp_connect(self):
        #try:
        if True:
            self.ssh = SSHClient()
            self.ssh.load_system_host_keys(self.config.SSH_KEYS)
            self.ssh.set_missing_host_key_policy(AutoAddPolicy())
            self.ssh.connect(self.config.SSH_HOST, username=self.config.SSH_USER, port=self.config.SSH_PORT)
            self.scp = self.ssh.open_sftp()
            return 0
        #except:
        #    self.message("Error, Failed to establish connection to server at {}@{}".format(self.config.SSH_USER, self.config.SSH_HOST))
        #    return -1

    def scp_get(self):
        self.mode('d')
        self.message("Downloading Update")
        self.scp_recurse()
        try:
            self.scp.get(self.config.SSH_DIR + self.config.VERSION_INFO, self.config.LOCAL_DIR + self.config.VERSION_INFO)
        except:
            self.message("Error, Failed to download version info")


    def scp_recurse(self, directory=""):
        for item_attr in self.scp.listdir_attr(self.config.SSH_DIR + directory):
            item = item_attr.filename
            if item not in self.config.IGNORE_FILES:
                if stat.S_ISREG(item_attr.st_mode):
                    try:
                        self.scp.get(self.config.SSH_DIR + directory + item, self.config.LOCAL_DIR + directory + item)
                        self.message("Downloaded " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message("Error: Failed to download file " + self.config.SSH_DIR + directory + item)
                elif stat.S_ISDIR(item_attr.st_mode):
                    try:
                        if not os.direxists(self.config.LOCAL_DIR + directory + item):
                            os.mkdir(self.config.LOCAL_DIR + directory + item)
                            self.message("New Directory made " + self.config.LOCAL_DIR + directory + item)
                        self.scp_recurse(directory + item + "/")
                        self.message("New Directory filled " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message("Failed to create directory " + self.config.LOCAL_DIR + directory + item)

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
                return True
        except:
            self.message("Lock file corrupted")
        return False



    def scp_check_version(self):
        self.message("Checking for new version")
        try:
            item = self.scp.listdir_attr(self.config.SSH_DIR)
            if not (stat.S_ISDIR(item[0].st_mode) or stat.S_ISREG(item[0].st_mode)):
                self.message("Error: remote directory {} does not exist".format(self.config.SSH_DIR))
                return False, False
        except:
            self.message("Error: remote directory {} does not exist".format(self.config.SSH_DIR))
            return False, False
        try:
            remote = self.scp.open(self.config.SSH_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message("Error: Failed to read remote version info")
            return False, False
        try:
            local = open(self.config.LOCAL_DIR + self.config.VERSION_INFO, 'r')
        except:
            self.message("Failed to read local version info. Downloading Files")
            remote.close()
            return True, True
        try:
            self.remote_version_number = int(remote.readline())
        except:
            self.message("Failed to cast remote version\nversion errors may exist\ntry downloading update manually if auto download is unsuccessful")
            remote.close()
            local.close()
            return True, True
        try:
            local_version_number = int(local.readline())
        except:
            local_version_number = 0

        self.message("Remote has version " + self.remote_version_number)
        self.message("Local has version " + local_version_number)
        remote.close()
        local.close()
        return self.remote_version_number > local_version_number, True

