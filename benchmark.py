import time

__author__ = 'johanm'
from devent.devent import EventNexus, Event
import gevent

if __name__ == "__main__":
    nexus = EventNexus()

    start = time.clock()
    num_items = 50000

    @nexus.subscribes("benchmark")
    def consumer(event):
        if event.obj == num_items:
            duration = time.clock() - start
            eps = float(num_items) / duration
            print "Consumed %d items in %fs (%f items/second)" % (num_items, duration, eps)


    def publisher():
        for i in range(num_items):
            nexus.publish("benchmark", i+1)

    publisher()
    gevent.sleep(10)

