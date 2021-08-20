###################################################
#                                                 #
# Program: update_ui                              #
#                                                 #
# Purpose: This program creates a UI for the auto #
#          update program                         #
#                                                 #
# Input:                                          #
#      none:                                      #
#                                                 #
# Output:                                         #
#      A new UI                                   #
#                                                 #
# Author: Jonathan Hull         Date: 16 Nov 2020 #
#                                                 #
###################################################

from PyQt5.QtWidgets import QListWidget, QLabel, QApplication, QDialog
from PyQt5.QtCore    import *
from PyQt5.QtGui     import QIcon, QFont, QPixmap
from time            import sleep
from subprocess      import call
import sys
import os
from threading import Thread
import config_loader as cl
import logwriter     as lw
import transporter   as tp

DOTS_OFFSET_X = 332
DOTS_OFFSET_Y = 2

############################################
#                                          #
# class: ui_dialog                         #
#                                          #
# Purpose: displays info to user           #
#                                          #
############################################
class ui_dialog(object):
    ############################################
    #                                          #
    # Function: setup_ui                       #
    #                                          #
    # Purpose: add UI elements to UI           #
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def setup_ui(self, Dialog):
        Dialog.setObjectName("Auto Update")
        Dialog.resize(512, 556)
        icon = QIcon()
        icon.addPixmap(QPixmap("images/icon.ico"), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.list_widget = QListWidget(Dialog)
        self.list_widget.setGeometry(QRect(0, 44, 512, 512))
        self.list_widget.setAutoScroll(True)
        font = QFont()
        font.setPointSize(8)
        self.list_widget.setFont(font)
        self.label = QLabel(Dialog)
        self.label.setObjectName("status")
        self.label.setGeometry(QRect(0,0, 512, 44))
        self.label.setAlignment(Qt.AlignCenter)
        self.dot_label = QLabel(Dialog)
        self.dot_label.setGeometry(QRect(DOTS_OFFSET_X, DOTS_OFFSET_Y, 44, 44))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        Dialog.setWindowTitle("Auto Update")
        self.closed = False
        self.set_mode('con')
        #Dialog.setWindowFlags(Qt.WindowTitleHint)
        self.thread = Thread(target = self.tick)
        self.thread.start()

    ############################################
    #                                          #
    # Function: set_mode                       #
    #                                          #
    # Purpose: changes the UI title            #
    #                                          #
    # args:                                    #
    #   m: new mode                            #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def set_mode(self, m):
        self.m = m

    ############################################
    #                                          #
    # Function: add_text                       #
    #                                          #
    # Purpose: adds item to display widget     #
    #                                          #
    # args:                                    #
    #   s: string to be added                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def add_text(self, s):
        item = self.list_widget.insertItem(0, s)

    ############################################
    #                                          #
    # Function: tick                           #
    #                                          #
    # Purpose: updates dots, location and title#
    #                                          #
    # args:                                    #
    #   self:                                  #
    #                                          #
    # outputs:                                 #
    #   none:                                  #
    #                                          #
    ############################################
    def tick(self):
        dots = ''
        while(not self.closed):
            sleep(1)
            try:
                dots = dots + '.'
                if dots == '....':
                    dots = ''
                if self.m == 'con':
                    text = "Connecting to Server"
                elif self.m == 'l':
                    text = "Acquiring Lock"
                elif self.m == 'cu':
                    text = "Checking for Updates"
                elif self.m == 'r':
                    text = "Removing Old Version"
                elif self.m == 'du':
                    text = "Downloading Update"
                elif self.m == 'uf' or self.m == 'u':
                    text = "Uploading Files"
                elif self.m == 'up':
                    text = "Up to Date"
                elif self.m == 'w':
                    text = "Waiting"
                elif self.m == 'sa':
                    text = "Starting Application"
                else:
                    text = "Searching"
                self.label.setText(text + " " + dots)
                #self.dot_label.setText(dots)
                #self.dot_label.setGeometry(QRect(DOTS_OFFSET_X + position, DOTS_OFFSET_Y, 44, 44))

            except:
                self.closed = True


############################################
#                                          #
# class: ui_handler                        #
#                                          #
# Purpose: controller behind UI            #
#                                          #
############################################
class ui_handler(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = ui_dialog()
        self.ui.setup_ui(self)
        self.show()
        self.app_started = False
        self.log = lw.logwriter()
        self.config = cl.config_loader(self.log.write)
        self.log.construct(self.config.LOG_FILE, self.config.PROGRAM_TITLE, self.config.VERSION, self.add_text, self.config.LOG_LEVEL)
        self.main_thread = Thread(target = self.start_program)
        self.main_thread.start()
        self.update_thread = Thread(target = self.start_update)
        self.update_thread.start()

    def add_text(self, s):
        self.ui.add_text(s)

    def closeEvent(self, event):
        try:
            print("Window Closed")
            print("Shutting down program")
            self.trans.kill()
            self.update_thread.join()
            print("Final Upload")
            self.stupid_thread = Thread(target = self.trans.run)
            self.stupid_thread.start()
            self.stupid_thread.join()
            print("Done")
        except:
            print("Exception Thrown while shutting down")
            try:
                self.trans.running = False
            except:
                pass

    def shut_down(self):
        if not self.trans.active_upload:
            sys.exit()
        else:
            sleep(1)
            self.shut_down()

    def start_program(self):
        self.trans = tp.transporter(self.log.write, self.config, self.ui.set_mode)
        self.trans.run()
        self.app_started = True
        try:
            self.ui.set_mode('sa')
            print(sys.platform)
            if sys.platform == "win32":
                os.chdir(self.config.EXE_DIR)
                call([self.config.EXE])
            else:
                os.system(self.config.EXE)
        except:
            try:
                self.trans.running = False
            except:
                pass
            self.log.write(0, "Error: Failed to launch program {}".format(self.config.EXE_DIR + self.config.EXE))

    def start_update(self):
        if not self.app_started:
            sleep(5)
            self.start_update()
        else:
            #self.trans = tp.transporter(self.log.write, self.config, self.ui.set_mode)
            self.trans.tick()

############################################
#                                          #
# Function: make_ui                        #
#                                          #
# Purpose: main function, makes the UI     #
#                                          #
# args:                                    #
#   self:                                  #
#                                          #
# outputs:                                 #
#   none:                                  #
#                                          #
############################################
def make_ui():
    app = QApplication(sys.argv)
    w = ui_handler()
    w.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    make_ui()
