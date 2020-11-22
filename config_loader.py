###################################################
#                                                 #
# Program: config_loader                          #
#                                                 #
# Purpose: Loads config file                      #
#                                                 #
# Input:                                          #
#      none:                                      #
#                                                 #
# Output:                                         #
#      none:                                      #
#                                                 #
# Author: Jonathan Hull         Date: 16 Nov 2020 #
#                                                 #
###################################################

from os import path

############################################
#                                          #
# class: config_loader                     #
#                                          #
# Purpose: load a configuration file       #
#                                          #
############################################
class config_loader:
    ############################################
    #                                          #
    # Function: __init__                       #
    #                                          #
    # Purpose: constructor for config_loader   #
    #          class                           #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #   message: function callback to writ to  #
    #            program log file              #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def __init__(self, message):
        self.message = message
        self.SSH_HOST_d      = '10.1.2.12'
        self.SSH_USER_d      = 'python_update'
        self.SSH_DIR_d       = '/home/python_update/python_auto_update/test/'
        self.SSH_KEYS        = path.expanduser(path.join("~", ".ssh", "known_hosts"))
        self.LOCAL_DIR_d     = './dest/'
        self.FILE_NAME_d     = 'test.py'
        self.VERSION_INFO_d  = 'version.info'
        self.IGNORE_FILES_d  = ['config', 'log.txt', '.git']
        self.VERSION_d       = "1.2.1"
        self.PROGRAM_TITLE_d = "Test Auto Update"
        self.CONFIG_FILE_d   = ".update_config"
        self.UPDATE_DELAY_d  = "1"
        self.read()

    ############################################
    #                                          #
    # Function: write                          #
    #                                          #
    # Purpose: create a new config file based  #
    #          on default values               #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def write(self):
        self.message("config file failed to load. Making new one.")
        config = open(self.CONFIG_FILE_d, "w+")
        config.write("ssh_host      =" + self.SSH_HOST_d + "\n")
        config.write("ssh_user      =" + self.SSH_USER_d + "\n")
        config.write("ssh_dir       =" + self.SSH_DIR_d + "\n")
        config.write("local_dir     =" + self.LOCAL_DIR_d + "\n")
        config.write("file_name     =" + self.FILE_NAME_d + "\n")
        config.write("version_info  =" + self.VERSION_INFO_d + "\n")
        config.write("ignore_files  =" + self.IGNORE_FILES_d[0] + "," + self.IGNORE_FILES_d[1] + "\n")
        config.write("version       =" + self.VERSION_d + "\n")
        config.write("program_title =" + self.PROGRAM_TITLE_d + "\n")
        config.write("update_delay  =" + self.UPDATE_DELAY_d + "\n")
        config.close()
        self.message("Successfully created new config file.")
        self.read()

    ############################################
    #                                          #
    # Function: read                           #
    #                                          #
    # Purpose: read config file                #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def read(self):
        try:
            self.message("Reading config file.")
            config = open(self.CONFIG_FILE_d, "r")
            ssh_host      = self.read_config_line(config)
            ssh_user      = self.read_config_line(config)
            ssh_dir       = self.read_config_line(config)
            local_dir     = self.read_config_line(config)
            file_name     = self.read_config_line(config)
            version_info  = self.read_config_line(config)
            ignore_files  = self.read_config_line(config).replace('\n', '').split(',')
            version       = self.read_config_line(config)
            program_title = self.read_config_line(config)
            update_delay  = int(self.read_config_line(config))
            config.close()

            self.SSH_HOST      = ssh_host
            self.SSH_USER      = ssh_user
            self.SSH_DIR       = ssh_dir
            self.LOCAL_DIR     = local_dir
            self.FILE_NAME     = file_name
            self.VERSION_INFO  = version_info
            self.IGNORE_FILES  = ignore_files
            self.VERSION       = version
            self.PROGRAM_TITLE = program_title
            self.IGNORE_FILES.append(self.VERSION_INFO)
            self.UPDATE_DELAY  = update_delay
            self.message("Successfully read config file.")
        except:
            self.write()


    ############################################
    #                                          #
    # Function: read_config_line               #
    #                                          #
    # Purpose: read after '=' in line          #
    #                                          #
    # args:                                    #
    #   fp = file pointer                      #
    #                                          #
    # outputs:                                 #
    #   line                                   #
    #                                          #
    ############################################
    def read_config_line(self, fp):
        line = fp.readline()
        return line[line.rfind("=") + 1:].replace('\n','')