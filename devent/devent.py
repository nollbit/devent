#coding: UTF-8
from collections import defaultdict
import gevent, gevent.monkey, gevent.event
import sys

gevent.monkey.patch_all()
from logging import getLogger
import logging
import redis

try:
    import cPickle as pickle
except ImportError:
    import pickle

from socket import gethostname

logger = getLogger(__package__)

class Event(object):
    def __init__(self, topic, obj, source):
        self.topic = topic
        self.obj = obj
        self.source = source

    def __repr__(self):
        return "Event(topic=%r, obj=%r, source=%r)" % (self.topic, self.obj, self.source)

class EventNexus(object):
    def __init__(self, redis_host="127.0.0.1", redis_port=6379, redis_channel="devent", source_id=None):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_channel = redis_channel

        self.redis_pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port)

        if source_id is None:
            source_id = gethostname()
        self.source_id = source_id

        self.subscriptions = defaultdict(list)

        self._ready_event = gevent.event.Event()
        gevent.spawn(self._event_handler)

    def _event_handler(self):
        while True:
            redis_client = redis.StrictRedis(connection_pool=self.redis_pool)
            redis_pubsub = redis_client.pubsub()
            redis_pubsub.subscribe(self.redis_channel)
            logger.info("Event handler started (subscribed to %s", self.redis_channel)
            for msg in redis_pubsub.listen():
                logger.debug("Message: %r" % msg)
                if msg['type'] == 'subscribe':
                    # all set up, ready to start publishing
                    self._ready_event.set()
                    del self._ready_event
                elif msg['type'] == 'message':
                    data = msg['data']
                    try:
                        event = pickle.loads(data)
                    except pickle.UnpicklingError:
                        logging.exception("Unable to unpickle message with data %r", data)
                        continue

                    logging.debug("Event %s", event)

                    for fn in self.subscriptions[event.topic]:
                        try:
                            fn(event)
                        except:
                            logging.exception("Exception in subscriber for event %s", event)

    def publish(self, topic, obj):
        if self._ready_event is not None:
            logger.debug("publish(): Stalling publish since we're still starting up")
            # in case we're still starting up, wait
            self._ready_event.wait(timeout=10)
            logger.debug("publish(): Startup is done")

        e = Event(topic, obj, self.source_id)
        e_data = pickle.dumps(e)
        redis_client = redis.StrictRedis(connection_pool=self.redis_pool)
        redis_client.publish(self.redis_channel, e_data)
        logger.debug("Published %s", e)

    def subscribes(self, topic):
        def decorator(f):
            logger.debug("Adding subscriper to topic %s: %r", topic, f)
            self.subscriptions[topic].append(f)
            return f

        return decorator


if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    nexus_out = EventNexus()
    @nexus_out.subscribes("test-topic")
    def test_method(event):
        print "test_method: Got event %s" % event

    @nexus_out.subscribes("test-topic")
    def test_method2(event):
        print "test_method2: Got event %s" % event

    nexus_in = EventNexus()
    nexus_in.publish("test-topic", "hello from the other side!")

    gevent.sleep(10)
