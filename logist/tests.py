import random
from datetime import datetime
from __init__ import Logist

l = Logist()
types = ["SUCCESS", "ERROR", "INFO", "WARNING"]
sub_types = ["ACCESS", "WRITE", "READ", "EDIT", "DELETE"]
descriptions = ["d1", "d2", "d3", "d4", "d5", "d6"]
start = datetime.now()
log_count = 105500
for log in xrange(log_count):
    log_type = types[random.randint(0, 3)]
    log_sub_type = sub_types[random.randint(0, 4)]
    description = descriptions[random.randint(0, 5)]
    l.log(log_type, log_sub_type, description)
time_delta = datetime.now() - start
print("Benchmark\n%d requests in %s\n %f logs/second" % (log_count, time_delta, log_count/time_delta.seconds))


# TODO - tests for compression switch, memory/file switch, filters, count
