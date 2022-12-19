import config_loader as cl
import logwriter     as lw
import transporter   as tp
import update_ui     as ui_handler
from threading import Thread

def main(update_ui, set_mode):
    log = lw.logwriter()
    config = cl.config_loader(log.write)
    log.construct(config.LOG_FILE, config.PROGRAM_TITLE, config.VERSION, update_ui, config.LOG_LEVEL)
    trans = tp.transporter(log.write, config, set_mode)
    update_thread = Thread(target = trans.tick)
    update_thread.start()


if __name__=="__main__":
    main(None, None)
