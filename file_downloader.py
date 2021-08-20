import stat
import os
from datetime   import datetime

class file_downloader:
    def __init__(self, config, message, set_mode):
        self.config  = config
        self.message = message
        self.mode = set_mode

    def download_files(self, scp_connection, current_timestamp, temp_restrictions = []):
        self.scp = scp_connection
        self.mode('d')
        self.message(0, "Downloading Files")
        self.scp_recurse(current_timestamp, temp_restrictions=temp_restrictions)
        self.scp.get(self.config.SSH_DIR + self.config.VERSION_INFO, self.config.LOCAL_DIR + self.config.VERSION_INFO)

    def scp_recurse(self, current_timestamp, directory="", temp_restrictions = []):
        for item_attr in self.scp.listdir_attr(self.config.SSH_DIR + directory):
            item = item_attr.filename
            whole_thing = self.config.LOCAL_DIR + directory + item
            if item not in (self.config.IGNORE_FILES + [self.config.VERSION_INFO, self.config.LOCK_FILE]) and whole_thing not in temp_restrictions:
                if stat.S_ISREG(item_attr.st_mode):
                    file_time = datetime.fromtimestamp(stat.ST_MTIME)
                    try:
                        print("")
                        print("")
                        print("stat modified time         = {}".format(file_time))
                        print("current timestamp          = {}".format(current_timestamp))
                        print("modified_time > timestamp? = {}".format(file_time > current_timestamp))
                        print("")
                        print("")
                        print("Local {}\nSSH {}".format(self.config.SSH_DIR, self.config.LOCAL_DIR))
                    except:
                        print("failed to convert timestamp")

                    if file_time > current_timestamp:
                        try:
                            self.scp.get(self.config.SSH_DIR + directory + item, self.config.LOCAL_DIR + directory + item)
                            self.message(2, "Downloaded: " + item + "\nfrom: " + self.config.LOCAL_DIR + directory)
                        except:
                            self.message(0, "Error: Failed to download file " + self.config.SSH_DIR + directory + item)
                elif stat.S_ISDIR(item_attr.st_mode):
                    try:
                        if not os.path.isdir(self.config.LOCAL_DIR + directory + item):
                            os.mkdir(self.config.LOCAL_DIR + directory + item)
                            self.message(2, "New Directory made " + self.config.LOCAL_DIR + directory + item)
                        self.scp_recurse(current_timestamp, directory + item + "/", temp_restrictions)
                        self.message(2, "New Directory filled " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message(0, "Failed to create directory " + self.config.LOCAL_DIR + directory + item)
            else:
                self.message(2, "File excluded {}".format(whole_thing))


