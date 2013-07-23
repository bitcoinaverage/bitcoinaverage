import Queue
import threading

from bitcoinaverage.config import CURRENCY_LIST, DEC_PLACES, EXCHANGE_LIST
from bitcoinaverage import api_parsers

in_queue = Queue.Queue()
out_queue = Queue.Queue()

class ThreadApiCall(threading.Thread):
    def __init__(self, exchange_name, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.exchange_name = exchange_name

    def run(self):
        host = self.in_queue.get()

        result = getattr(api_parsers, self.exchange_name+'ApiCall')(**EXCHANGE_LIST[self.exchange_name])


        #signals to queue job is done
        self.out_queue.put(result)
        self.in_queue.task_done()




for exchange_name in EXCHANGE_LIST:
    t = ThreadApiCall(exchange_name)
    t.setDaemon(True)
    t.start()

    in_queue.put(exchange_name)

in_queue.join()

