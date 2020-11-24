import stat
import os

class file_downloader:
    def __init__(self, config, message, set_mode):
        self.config  = config
        self.message = message
        self.mode = set_mode

    def download_files(self, scp_connection, temp_restrictions = []):
        self.scp = scp_connection
        self.mode('d')
        self.message(0, "Downloading Files")
        self.scp_recurse(temp_restrictions=temp_restrictions)
        self.scp.get(self.config.SSH_DIR + self.config.VERSION_INFO, self.config.LOCAL_DIR + self.config.VERSION_INFO)

    def scp_recurse(self, directory="", temp_restrictions = []):
        for item_attr in self.scp.listdir_attr(self.config.SSH_DIR + directory):
            item = item_attr.filename
            if item not in (self.config.IGNORE_FILES + [self.config.VERSION_INFO, self.config.LOCK_FILE]):
                whole_thing = "/" + directory + item
                print("########################################\n")
                print("### new = {}".format(whole_thing))
                for i in temp_restrictions:
                    print("### {}".format(i))
                print("########################################\n")
                if whole_thing not in temp_restrictions:
                    if stat.S_ISREG(item_attr.st_mode):
                        try:
                            self.scp.get(self.config.SSH_DIR + directory + item, self.config.LOCAL_DIR + directory + item)
                            self.message(2, "Downloaded " + self.config.LOCAL_DIR + directory + item)
                        except:
                            self.message(0, "Error: Failed to download file " + self.config.SSH_DIR + directory + item)
                    elif stat.S_ISDIR(item_attr.st_mode):
                        #try:
                        if True:
                            if not os.path.isdir(self.config.LOCAL_DIR + directory + item):
                                os.mkdir(self.config.LOCAL_DIR + directory + item)
                                self.message(2, "New Directory made " + self.config.LOCAL_DIR + directory + item)
                            self.scp_recurse(directory + item + "/")
                            self.message(2, "New Directory filled " + self.config.LOCAL_DIR + directory + item)
                        #except:
                        #    self.message(0, "Failed to create directory " + self.config.LOCAL_DIR + directory + item)
                else:
                    print("File excluded")


