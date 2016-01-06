import random
from time import sleep
from datetime import datetime
from __init__ import Logist

l = Logist()
types = ["SUCCESS", "ERROR", "INFO", "WARNING"]
sub_types = ["ACCESS", "WRITE", "READ", "EDIT", "DELETE"]
descriptions = ["d1", "d2", "d3", "d4", "d5", "d6"]
start = datetime.now()
for log in xrange(100000):
    # sleep(random.random()/10000)
    log_type = types[random.randint(0, 3)]
    log_sub_type = sub_types[random.randint(0, 4)]
    description = descriptions[random.randint(0, 5)]
    l.log(log_type, log_sub_type, description)
print(datetime.now() - start)
