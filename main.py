import config_loader as cl
import logwriter     as lw
import transporter   as tp
from threading import Thread

def main():
    log = lw.logwriter()
    config = cl.config_loader(log.write)
    log.construct(config.LOG_FILE, config.PROGRAM_TITLE, config.VERSION, None)
    trans = tp.transporter(log.write, config, None)
    update_thread = Thread(target = trans.tick)
    update_thread.start()


main()
