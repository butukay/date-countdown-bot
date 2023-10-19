import logging, datetime, signal, gzip, time, sys, os
import threading

import nest_asyncio
nest_asyncio.apply()

def archive_prev_log():
    if not os.path.exists("logs/latest.log"):
        return

    with open("logs/latest.log", "rb") as f_in, gzip.open(f"logs/logs-{datetime.datetime.now().strftime('%d-%m-%Y-%H%M%S')}.gz", "wb") as f_out:
        f_out.write(f_in.read())


def setup_logging():
    logger_format = "%(asctime)s : %(threadName) 7s : %(message)s"
    logging.basicConfig(
        format=logger_format,
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="logs/latest.log",
        filemode="w",
    )

    if "--full-debug" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)


def setup_files():
    required_dirs = [
        "logs",
        "data"
    ]

    required_files = {
        "data/executed_mailings.json": "{}",
    }

    for d in required_dirs:
        if not os.path.isdir(d):
            os.mkdir(d)

    for path, default_content in required_files.items():
        if not os.path.exists(path):
            with open(path, "w") as new_file:
                new_file.write(default_content)


if __name__ == "__main__":
    thread = threading.current_thread()
    thread.name = "MAIN"

    setup_files()

    archive_prev_log()
    setup_logging()

    logging.info(f"Запускаюсь с аргументами: {sys.argv}")
    import countdown.chatbot, countdown.worker

    threads = []

    if "--no-worker" not in sys.argv:
        countdown.worker.start()
    else:
        logging.info("Worker thread disabled")

    if "--no-chatbot" not in sys.argv:
        countdown.chatbot.start()
    else:
        logging.info("Chatbot thread disabled")

    def exit_signal_handler(signum, frame):
        logging.debug("Exited with signum: %s, frame: %s", signum, frame)
        print("Exiting....")
        exit(0)

    signal.signal(signal.SIGINT, exit_signal_handler)
    signal.signal(signal.SIGTERM, exit_signal_handler)

    while True:
        time.sleep(10)
