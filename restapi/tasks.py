from queue import SimpleQueue
import threading


import logging
logger = logging.getLogger(__name__)

q = SimpleQueue()


def worker():
    while True:
        item = q.get()
        print(f'Working on {item}')
        item.start()
        item.join()
        print(f'Finished {item}')


threading.Thread(target=worker, daemon=True).start()

logger.info("*-*"*40)
