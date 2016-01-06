import json
import os
from datetime import datetime
import gzip
import shutil

from redis import Redis


class Logist(object):

    def __init__(self):
        try:
            config = json.loads(open("logist_config.json", 'r').read())
        except (IOError, ValueError):
            print("Using default configurations.\n"
                  "Create a logist_config.json for custom configuration.")
            config = {}
        self.REDIS_ADDRESS = config.get("REDIS_ADDRESS") or "localhost"
        self.REDIS_PORT = config.get("REDIS_PORT") or 6379
        self.FLUSH_COUNT = config.get("FLUSH_COUNT") or 10000
        self.FILE_SIZE = config.get("FILE_SIZE") or 1000000
        self.LOG_FILE_NAME = config.get("LOG_FILE_NAME") or "default"
        self.LOG_FOLDER = config.get("LOG_FOLDER")
        self.NAMESPACE = config.get("NAMESPACE") or "LOGIST"
        self.COMPRESSION = config.get("COMPRESSION") or True
        self.redis_instance = Redis(host=self.REDIS_ADDRESS, port=self.REDIS_PORT)

    def f_write(self, force=False):
        if self.LOG_FOLDER:
            file_location = os.path.join(self.LOG_FOLDER, self.LOG_FILE_NAME)
        else:
            file_location = self.LOG_FILE_NAME
        file_location = "%s.log" % file_location
        file_instance = open(file_location, "a")
        redis_dump = "%s\n" % "\n". join(self.redis_instance.lrange(self.NAMESPACE, 0, -1))
        self.redis_instance.delete(self.NAMESPACE)
        file_instance.write(redis_dump)
        file_instance.close()
        if os.path.getsize(file_location) > self.FILE_SIZE or force:
            self.f_compress(file_location)

    def m_write(self, log_type, sub_type, description, log_time=None):
        log_time = datetime.strftime(log_time or datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
        self.redis_instance.lpush(self.NAMESPACE, "%s >< %s :: %s || %s" %
                                  (log_time, log_type, sub_type, description))
        if self.redis_instance.llen(self.NAMESPACE) >= self.FLUSH_COUNT:
            self.f_write()

    def f_compress(self, file_location):
        count = 1
        log_file = file_location
        print log_file
        while 1:
            file_name = "%s_%d" % (self.LOG_FILE_NAME, count)
            if self.COMPRESSION:
                if self.LOG_FOLDER:
                    compressed_file_name = "%s.log.gz" % os.path.join(self.LOG_FOLDER, file_name)
                else:
                    compressed_file_name = "%s.log.gz" % file_name
                if not os.path.isfile(compressed_file_name):
                    with open(log_file, 'rb') as f_in, gzip.open(compressed_file_name, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        open(log_file, 'w').close()
                    return
            else:
                if self.LOG_FOLDER:
                    uncompressed_file_name = "%s.log" % os.path.join(self.LOG_FOLDER, file_name)
                else:
                    uncompressed_file_name = "%s.log" % file_name
                if not os.path.isfile(uncompressed_file_name):
                    with open(log_file, 'r') as f_in, open(uncompressed_file_name, 'w') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        open(log_file, 'w').close()
                    return
            count += 1
        return

    def log(self, log_type, sub_type, description, log_time=None):
        self.m_write(log_type, sub_type, description, log_time)

    def error(self, sub_type, description, log_time=None):
        self.m_write("ERROR", sub_type, description, log_time)

    def warning(self, sub_type, description, log_time=None):
        self.m_write("WARNING", sub_type, description, log_time)

    def success(self, sub_type, description, log_time=None):
        self.m_write("SUCCESS", sub_type, description, log_time)

    def info(self, sub_type, description, log_time=None):
        self.m_write("INFO", sub_type, description, log_time)

    def debug(self, sub_type, description, log_time=None):
        self.m_write("DEBUG", sub_type, description, log_time)

    def m_filter(self, log_type, sub_type="", description=""):
        pass

    def f_filter(self, log_type, sub_type="", description=""):
        pass

    def m_count(self, ):
        pass

    def f_count(self, ):
        pass
