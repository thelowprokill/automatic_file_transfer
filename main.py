import config_loader as cl
import logwriter     as lw
import transporter   as tp
import update_ui     as ui_handler
import sys
from threading import Thread
from time import sleep

from PyQt5.QtWidgets import QListWidget, QLabel, QApplication, QDialog

class main:
    def __init__(self):
        app = QApplication(sys.argv)
        self.ui = ui_handler.ui_handler()
        self.ui.show()
        update_thread = Thread(target = self.start)
        update_thread.start()

        sys.exit(app.exec_())

    def start(self):
        sleep(2)
        log = lw.logwriter()
        config = cl.config_loader(log.write)
        log.construct(config.LOG_FILE, config.PROGRAM_TITLE, config.VERSION, self.ui.add_text, config.LOG_LEVEL)
        trans = tp.transporter(log.write, config, self.ui.ui.set_mode)
        update_thread = Thread(target = trans.tick)
        update_thread.start()





main()
