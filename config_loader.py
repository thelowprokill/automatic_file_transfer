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
        self.SSH_HOST_d        = '192.168.0.134'
        self.SSH_USER_d        = 'user'
        self.SSH_PORT_d        = '22'
        self.SSH_DIR_d         = path.expanduser("~")
        self.SSH_KEYS_d        = path.expanduser(path.join("~", ".ssh", "known_hosts"))
        self.LOCK_FILE_d       = ".lock"
        self.LOCAL_DIR_d       = './test/'
        self.IGNORE_FILES_d    = ['ignore_me']
        self.UPDATE_DELAY_d    = "60"
        self.VERSION_INFO_d    = "version.info"
        self.TIME_STAMP_FILE_d = ""
        self.USE_PASSWORD_d    = "0"
        self.PASSWORD_d        = "null"
        self.VERSION_d         = "1.1.1"
        self.LOG_LEVEL_d       = "3"
        self.PROGRAM_TITLE_d   = "automatic file transfer"
        self.CONFIG_FILE_d     = ".config"
        self.LOG_FILE_d        = ".log"
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
        config.write("ssh_port      =" + self.SSH_PORT_d + "\n")
        config.write("ssh_dir       =" + self.SSH_DIR_d + "\n")
        config.write("ssh_keys      =" + self.SSH_KEYS_d + "\n")
        config.write("lock_file     =" + self.LOCK_FILE_d + "\n")
        config.write("local_dir     =" + self.LOCAL_DIR_d + "\n")
        config.write("ignore_files  =" + self.IGNORE_FILES_d[0] + "\n")
        config.write("update_delay  =" + self.UPDATE_DELAY_d + "\n")
        config.write("version_file  =" + self.VERSION_INFO_d + "\n")
        config.write("time_stamp    =" + self.TIME_STAMP_FILE_d + "\n")
        config.write("use_password  =" + self.USE_PASSWORD_d + "\n")
        config.write("password      =" + self.PASSWORD_d + "\n")
        config.write("version       =" + self.VERSION_d + "\n")
        config.write("log_level     =" + self.LOG_LEVEL_d + "\n")
        config.write("program_title =" + self.PROGRAM_TITLE_d + "\n")
        config.write("log file name =" + self.LOG_FILE_d + "\n")
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
            ssh_port      = self.read_config_line(config)
            ssh_dir       = self.read_config_line(config)
            ssh_keys      = self.read_config_line(config)
            lock_file     = self.read_config_line(config)
            local_dir     = self.read_config_line(config)
            ignore_files  = self.read_config_line(config).replace('\n', '').split(',')
            update_delay  = int(self.read_config_line(config))
            version_info  = self.read_config_line(config)
            time_stamp    = self.read_config_line(config)
            use_password  = int(self.read_config_line(config))
            password      = self.read_config_line(config)
            version       = self.read_config_line(config)
            log_level     = int(self.read_config_line(config))
            program_title = self.read_config_line(config)
            log_file      = self.read_config_line(config)
            config.close()

            self.SSH_HOST      = ssh_host
            self.SSH_USER      = ssh_user
            self.SSH_PORT      = ssh_port
            self.SSH_DIR       = ssh_dir
            self.SSH_KEYS      = ssh_keys
            self.LOCK_FILE     = lock_file
            self.LOCAL_DIR     = local_dir
            self.IGNORE_FILES  = ignore_files
            self.UPDATE_DELAY  = update_delay
            self.VERSION_INFO  = version_info
            self.TIME_STAMP    = time_stamp
            self.USE_PASSWORD  = use_password
            self.PASSWORD      = password
            self.VERSION       = version
            self.LOG_LEVEL     = log_level
            self.PROGRAM_TITLE = program_title
            self.LOG_FILE      = log_file
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
