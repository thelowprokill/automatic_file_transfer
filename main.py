import config_loader as cl
import logwriter     as lw
import transporter   as tp

def main():
    log = lw.logwriter()
    config = cl.config_loader(log.write)
    log.construct(config.LOG_FILE, config.PROGRAM_TITLE, config.VERSION, None)
    trans = tp.transporter(log.write, config, None)
    trans.update(True)


main()
