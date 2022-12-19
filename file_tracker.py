###################################################
#                                                 #
# Program: file_tracker                           #
#                                                 #
# Purpose: keeps track of transferred files       #
#                                                 #
# Input:                                          #
#      none:                                      #
#                                                 #
# Output:                                         #
#      none:                                      #
#                                                 #
# Author: Jonathan Hull         Date: 06 Aug 2021 #
#                                                 #
###################################################

from os import path

class file_tracker:
    ############################################
    #                                          #
    # Function: __init__                       #
    #                                          #
    # Purpose: constructor for file_tracker    #
    #          class                           #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #   config: ref to the active config       #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def __init__(self, config):
        self.file_name = config.TRACKING_FILE


    ############################################
    #                                          #
    # Function: check_file                     #
    #                                          #
    # Purpose: check if file is tracked        #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #   file: string file_name to check        #
    #                                          #
    # outputs:                                 #
    #   bool: weather or not the file exists   #
    #                                          #
    ############################################
    def check_file(self, file):
        try:
            file_pointer = open(self.file_name, "r")
        except:
            return False

        lines = file_pointer.readlines()
        for line in lines:
            if line == file + "\n":
                file_pointer.close()
                return True

        file_pointer.close()
        return False

    ############################################
    #                                          #
    # Function: add_file                       #
    #                                          #
    # Purpose: add a tracked file              #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #   file: string file_name to add          #
    #                                          #
    # outputs:                                 #
    #   bool: success                          #
    #                                          #
    ############################################
    def add_file(self, file):
        if not self.check_file(file):
            file_pointer = open(self.file_name, "a")
            file_pointer.write(file + "\n")
            file_pointer.close()


if __name__ == "__main__":
    import logwriter as lw
    import config_loader as cl

    log = lw.logwriter()
    config = cl.config_loader(log.write)

    ft = file_tracker(config)
    ft.add_file("new_file")
    ft.add_file("again_new_file")

    print(ft.check_file("foo"))
    print(ft.check_file("new_file"))
    print(ft.check_file("again_new_file"))
