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
import sys
#import update
from threading import Thread

DOTS_OFFSET_X = 195
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
        Dialog.resize(256, 300)
        icon = QIcon()
        icon.addPixmap(QPixmap("images/icon.ico"), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.list_widget = QListWidget(Dialog)
        self.list_widget.setGeometry(QRect(0, 44, 256, 256))
        self.list_widget.setAutoScroll(True)
        font = QFont()
        font.setPointSize(8)
        self.list_widget.setFont(font)
        self.label = QLabel(Dialog)
        self.label.setObjectName("status")
        self.label.setGeometry(QRect(0,0, 240, 44))
        self.label.setAlignment(Qt.AlignCenter)
        self.dot_label = QLabel(Dialog)
        self.dot_label.setGeometry(QRect(DOTS_OFFSET_X, DOTS_OFFSET_Y, 44, 44))
        font = QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        Dialog.setWindowTitle("Auto Update")
        self.closed = False
        self.set_mode('c')
        Dialog.setWindowFlags(Qt.WindowTitleHint)
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
                if self.m == 'c':
                    text = "Connecting to Server"
                    position = 0
                elif self.m == 'u':
                    text = "Checking for Updates"
                    position = 2
                elif self.m == 'r':
                    text = "Removing Old Version"
                    position = 5
                elif self.m == 'd':
                    text = "Downloading Update"
                    position = 0
                elif self.m == 's':
                    text = "Starting Application"
                    position = -5
                else:
                    text = "Searching"
                    position = 0
                self.label.setText(text)
                self.dot_label.setText(dots)
                self.dot_label.setGeometry(QRect(DOTS_OFFSET_X + position, DOTS_OFFSET_Y, 44, 44))

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
        #self.thread = Thread(target = self.start_update)
        #self.thread.start()

    def add_text(self, s):
        self.ui.add_text(s)

    #def start_update(self):
    #    self.add_text("update started")
    #    update.update_program(self.add_text, self.ui.set_mode)
    #    self.close()

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
