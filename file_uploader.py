import stat
import os
import errno

class file_uploader:
    def __init__(self, config, message):
        self.config  = config
        self.message = message

    def upload_files(self, scp_connection, specific_files=['']):
        self.scp = scp_connection
        self.message(0, "Uploading Files")
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
                self.message(2, "Uploaded: " + item + "\nfrom: " + self.config.LOCAL_DIR)
            except:
                dirs = item.split('/')
                dirs = dirs[1:]
                dirs = dirs[:len(dirs) - 1]
                print("dirs split {}".format(dirs))
                self.remote_mkdir(self.config.SSH_DIR[:len(self.config.SSH_DIR) - 1], dirs)
                self.message(2, "Directory made")
                self.scp.put(self.config.LOCAL_DIR + item, self.config.SSH_DIR + item)
                self.message(2, "Uploaded " + self.config.LOCAL_DIR + item)


    def remote_mkdir(self, directory, dirs):
        print("dirs {}".format(dirs[0]))
        print("directory " + directory)
        if dirs[0] != "." and dirs[0] != "" and dirs[0] not in self.config.IGNORE_FILES + [self.config.VERSION_INFO]:
            directory = directory + "/" + dirs[0]
            print("cur_dir {}".format(directory))
            try:
                self.scp.mkdir(directory)# + "/" + dirs[0])
                self.message(2, "New Directory made " + directory)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    self.message(0, "Error: Failed to make directory " + directory)
                pass
            if len(dirs) > 1:
                self.remote_mkdir(directory, dirs[1:])

    def scp_recurse(self, directory=""):
        for item in os.listdir(self.config.LOCAL_DIR + directory):
            if item not in (self.config.IGNORE_FILES + [self.config.LOCK_FILE, self.config.VERSION_INFO]):
                if os.path.isfile(self.config.LOCAL_DIR + directory + item):
                    try:
                        self.scp.put(self.config.LOCAL_DIR + directory + item, self.config.SSH_DIR + directory + item)
                        self.message(2, "Uploaded " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message(0, "Error: Failed to upload file " + self.config.SSH_DIR + directory + item)
                elif os.path.isdir(self.config.LOCAL_DIR + directory + item):
                    try:
                        self.scp.mkdir(self.config.SSH_DIR + directory + item)
                        self.message(2, "New Directory made " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message(0, "Error: Failed to make new Directory {}".format(self.config.LOCAL_DIR + directory + item))
                    try:
                        self.scp_recurse(directory + item + "/")
                        self.message(2, "New Directory filled " + self.config.LOCAL_DIR + directory + item)
                    except:
                        self.message(0, "Error: Failed to fill directory " + self.config.LOCAL_DIR + directory + item)
