devent
======

Distributed event handling under gevent using redis, inspired by the Planet Framework.

Huh?
----
It uses a redis channel to transport the events across processes and instances 

Example using a localhost redis at 6379
-------
```python
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
```
The code above would yield

```python
test_method: Got event Event(topic='test-topic', obj='hello from the other side!', source='johanm-vm')
test_method2: Got event Event(topic='test-topic', obj='hello from the other side!', source='johanm-vm')
```

License
-------
Apache 2.0