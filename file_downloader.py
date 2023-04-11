import stat
import os
from datetime   import datetime

##################################################
#                                                #
# class: file_downloader                         #
#                                                #
# purpose: download files from scp server to     #
#   local machine                                #
#                                                #
##################################################
class file_downloader:
    ##############################################
    #                                            #
    # function: init                             #
    #                                            #
    # purpose: initialize the file_downloader    #
    #                                            #
    # args:                                      #
    #   config: reference to config class        #
    #   message: reference to text output        #
    #     function                               #
    #                                            #
    ##############################################
    def __init__(self, config, message):
        self.config  = config
        self.message = message

    ##############################################
    #                                            #
    # function download_files                    #
    #                                            #
    # purpose: download files from scp server to #
    #   local machine                            #
    #                                            #
    # args:                                      #
    #   scp_connection: reference to the scp     #
    #     connection                             #
    #   current_timestamp: datetime of last      #
    #     transfer                               #
    #   temp_restrictions: list of files to      #
    #     ignore                                 #
    #                                            #
    ##############################################
    def download_files(self, scp_connection, current_timestamp, temp_restrictions = []):
        self.scp = scp_connection
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
                        if file_time > datetime(2021, 1, 1):
                            print("")
                            print("")
                            print("stat modified time         = {}".format(file_time))
                            print("current timestamp          = {}".format(current_timestamp))
                            print("modified_time > timestamp? = {}".format(file_time > current_timestamp))
                            print("")
                            print("")
                            print("Local {}\nSSH {}".format(self.config.SSH_DIR + item, self.config.LOCAL_DIR + item))
                    except:
                        print("failed to convert timestamp")

                    if file_time > current_timestamp or self.check_if_file_exists(self.config.SSH_DIR + item):
                        try:
                            self.scp.get(self.config.SSH_DIR + directory + item, self.config.LOCAL_DIR + directory + item)
                            self.message(2, "Downloaded: " + item + "\nfrom: " + directory)
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

    def check_if_file_exists(self, item):
        return not os.path.exists(item)

