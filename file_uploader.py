import stat
import os

class file_uploader:
    def __init__(self, config, message, set_mode):
        self.config  = config
        self.message = message
        self.mode = set_mode

    def upload_files(self, scp_connection, specific_files=['']):
        self.scp = scp_connection
        self.mode('u')
        self.message("Uploading Files")
        if specific_files[0] == '':
            self.scp_recurse()
        else:
            self.upload_specific_files(specific_files)
        self.scp.put(self.config.LOCAL_DIR + self.config.VERSION_INFO, self.config.SSH_DIR + self.config.VERSION_INFO)

    def upload_specific_files(self, files):
        for item in files:
            print(item)
            try:
                self.scp.put(self.config.LOCAL_DIR + item, self.config.SSH_DIR + item)
                self.message("Uploaded " + self.config.LOCAL_DIR + item)
            except:
                dirs = item.split('/')
                print("dirs split " + dirs)
                self.remote_mkdir(self.config.SSH_DIR, dirs)
                self.scp.put(self.config.LOCAL_DIR + item, self.config.SSH_DIR + item)
                self.message("Uploaded " + self.config.LOCAL_DIR + item)


    def remote_mkdir(self, directory, dirs):
        print("dirs "+dirs[0])
        print("directory " + directory)
        print("cur_dir " + directory + dirs[0])
        if dirs[0] != "." and dirs[0] != "" and dirs[0] not in self.config.IGNORE_FILES + [self.config.VERSION_INFO]:
            directory = directory + "/" + dirs[0]
            try:
                self.scp.mkdir(directory + "/" + dirs[0])
                self.message("New Directory made " + directory)
            except:
                self.message("Failed to make directory " + directory)
            if len(dirs) > 1:
                self.remote_mkdir(directory + "/", dirs[1:])

    def scp_recurse(self, directory=""):
        for item in os.listdir(self.config.LOCAL_DIR + directory):
            if item not in (self.config.IGNORE_FILES + [self.config.LOCK_FILE, self.config.VERSION_INFO]):
                if os.path.isfile(self.config.LOCAL_DIR + directory + item):
                    try:
                        self.scp.put(self.config.LOCAL_DIR + directory + item, self.config.SSH_DIR + directory + item)
                        self.message("Uploaded " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message("Error: Failed to upload file " + self.config.SSH_DIR + directory + item)
                elif os.path.isdir(self.config.LOCAL_DIR + directory + item):
                    try:
                        #if not os.direxists(self.config.LOCAL_DIR + directory + item):
                        #    os.mkdir(self.config.LOCAL_DIR + directory + item)
                        #    self.message("New Directory made " + self.config.LOCAL_DIR + directory + item)
                        self.scp.mkdir(self.config.SSH_DIR + directory + item)
                        self.message("New Directory made " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message("Failed to make new Directory {}".format(self.config.LOCAL_DIR + directory + item))
                    try:
                        self.scp_recurse(directory + item + "/")
                        self.message("New Directory filled " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message("Failed to fill directory " + self.config.LOCAL_DIR + directory + item)
