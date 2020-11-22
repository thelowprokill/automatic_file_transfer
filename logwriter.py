###################################################
#                                                 #
# Program: logwriter                              #
#                                                 #
# Purpose: This program writes logs               #
#                                                 #
# Input:                                          #
#      none:                                      #
#                                                 #
# Output:                                         #
#      A log file by specified name               #
#                                                 #
# Author: Jonathan Hull         Date: 16 Nov 2020 #
#                                                 #
###################################################

from datetime import datetime

############################################
#                                          #
# class: logwriter                         #
#                                          #
# Purpose: writes logs                     #
#                                          #
############################################
class logwriter:
    ############################################
    #                                          #
    # Function: __init__                       #
    #                                          #
    # Purpose: init logwriter class            #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def __init__(self):
        self.cue = []

    ############################################
    #                                          #
    # Function: construct                      #
    #                                          #
    # Purpose: constructor for logwriter class #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #   program_title: title to be written     #
    #   version: program version to be written #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def construct(self, fn, program_title, version, update_ui):
        self.fn = fn
        self.program_title = program_title
        self.version = version
        self.update_ui = update_ui
        self.log_file = open(self.fn, "w+")
        self.write("{} {} log {}".format(self.program_title, self.version, datetime.now()))
        self.flush_cue()


    ############################################
    #                                          #
    # Function: re_open                        #
    #                                          #
    # Purpose: open the file for appending     #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def re_open(self):
        self.log_file = open(self.fn, "a")
        self.flush_cue()

    ############################################
    #                                          #
    # Function: flush_cue                      #
    #                                          #
    # Purpose: write cued items to file        #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def flush_cue(self):
        for item in self.cue:
            self.write(item)
    ############################################
    #                                          #
    # Function: cue_outputs                    #
    #                                          #
    # Purpose: add items to cue                #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def cue_output(self, s):
        self.cue.append(s)

    ############################################
    #                                          #
    # Function: write                          #
    #                                          #
    # Purpose: writes data to log file         #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #   s: string to be written                #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def write(self, s):
        try:
            self.log_file.write(s + "\n")
            print(s)
            try:
                self.update_ui(s)
            except:
                pass
        except:
            self.cue_output(s)


    ############################################
    #                                          #
    # Function: clear                          #
    #                                          #
    # Purpose: clears log file                 #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def clear(self):
        self.close()
        self.log_file = open(self.fn, "w+")
        self.wrtie("{} {} log {}".format(self.program_title, self.version, datetime.now()))

    ############################################
    #                                          #
    # Function: close                          #
    #                                          #
    # Purpose: closes log file committing to   #
    #          file                            #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def close(self):
        self.log_file.close()
