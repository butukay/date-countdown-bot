import threading, schedule, logging, json, time, sys, os

from . import main

def worker():
    if '--run-updates-now' in sys.argv:
        logging.info("Running message updates now...")
        main.update_messages()

    while True:
        schedule.run_pending()
        time.sleep(1)


def worker_wrapper():
    # from countdown.chatbot.logic.admin_logs import send_thread_exception, send_thread_restarted

    first_run = True

    WORKER_RESTART_TIMEOUT = int(os.environ.get("WORKER_RESTART_TIMEOUT", "120"))

    while True:
        # if not first_run:
        #     send_thread_restarted("WORKER")

        try:
            worker()
        except Exception as e:
            logging.exception(f"Worker thread exception: {e}")
            # send_thread_exception("WORKER", e)

        first_run = False

        time.sleep(WORKER_RESTART_TIMEOUT)

### called from root main.py
def start():
    logging.info("Setting up worker...")

    if "--no-schedule" not in sys.argv:
        RUN_UPDATES_TIMES = json.loads(os.environ.get("RUN_UPDATES_TIMES", '["00:00"]'))
        for time in RUN_UPDATES_TIMES:
            schedule.every().day.at(time).do(main.update_messages, show_time=False)
            logging.info(f"Scheduled UPDATES for {time} every day")

        RUN_UPDATES_INTERVAL = int(os.environ.get("RUN_UPDATES_INTERVAL", "60"))
        schedule.every(RUN_UPDATES_INTERVAL).minutes.do(main.update_messages, only_with_time=True)
        logging.info(f"Scheduled UPDATES every {RUN_UPDATES_INTERVAL} minutes")

    try:
        worker_thread = threading.Thread(target=worker_wrapper, name="WORKER", daemon=True)
        worker_thread.start()

        logging.info("Worker thread started")
    except Exception as e:
        logging.exception(f"Unable to start worker thread: {e}")

