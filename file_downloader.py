import stat
import os

class file_downloader:
    def __init__(self, config, message, set_mode):
        self.config  = config
        self.message = message
        self.mode = set_mode

    def download_files(self, scp_connection):
        self.scp = scp_connection
        self.mode('d')
        self.message("Downloading Files")
        self.scp_recurse()
        self.scp.get(self.config.SSH_DIR + self.config.VERSION_INFO, self.config.LOCAL_DIR + self.config.VERSION_INFO)

    def scp_recurse(self, directory=""):
        for item_attr in self.scp.listdir_attr(self.config.SSH_DIR + directory):
            item = item_attr.filename
            if item not in (self.config.IGNORE_FILES + [self.config.VERSION_INFO, self.config.LOCK_FILE]):
                if stat.S_ISREG(item_attr.st_mode):
                    try:
                        self.scp.get(self.config.SSH_DIR + directory + item, self.config.LOCAL_DIR + directory + item)
                        self.message("Downloaded " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message("Error: Failed to download file " + self.config.SSH_DIR + directory + item)
                elif stat.S_ISDIR(item_attr.st_mode):
                    #try:
                    if True:
                        if not os.path.isdir(self.config.LOCAL_DIR + directory + item):
                            os.mkdir(self.config.LOCAL_DIR + directory + item)
                            self.message("New Directory made " + self.config.LOCAL_DIR + directory + item)
                        self.scp_recurse(directory + item + "/")
                        self.message("New Directory filled " + self.config.LOCAL_DIR + directory + item)
                    #except:
                    #    self.message("Failed to create directory " + self.config.LOCAL_DIR + directory + item)


