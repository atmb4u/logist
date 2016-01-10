import json
import os
from datetime import datetime
import gzip
import shutil

from redis import Redis

__version__ = "0.92"


class Logist(object):
    def __init__(self, redis_address="localhost", redis_port=6379, flush_count=10000, file_size=10000000,
                 log_file_name="default", log_folder="", namespace="DEFAULT", compression=True):
        """
        REDIS_ADDRESS: Address to redis server
        REDIS_PORT: redis server port
        FLUSH_COUNT: log count when in-memory logs to be flushed to file
        FILE_SIZE: file size when log file to be split up and compressed
        LOG_FILE_NAME: name of the log file
        LOG_FOLDER: folder for log files
        NAMESPACE: a custom namespace for logs to be kept in redis server
        COMPRESSION: a boolean field to enable/disable compression (True/False)

        Override configuration file format
        logist_config.json
        {
            "REDIS_ADDRESS": "localhost",
            "REDIS_PORT": 6379,
            "FLUSH_COUNT": 10000,
            "FILE_SIZE": 10000000,
            "LOG_FILE_NAME": "",
            "LOG_FOLDER": "",
            "NAMESPACE": "PROJECT_NAME",
            "COMPRESSION": true
        }
        """
        self.log_list = []
        try:
            conf_string = open("logist_config.json", 'r').read()
            config = json.loads(conf_string)
        except (IOError, ValueError):
            print("Using default configuration. For custom configuration create logist_config.json")
            config = {}
        self.REDIS_ADDRESS = config.get("REDIS_ADDRESS") or redis_address
        self.REDIS_PORT = config.get("REDIS_PORT") or redis_port
        self.FLUSH_COUNT = config.get("FLUSH_COUNT") or flush_count
        self.FILE_SIZE = config.get("FILE_SIZE") or file_size
        self.LOG_FILE_NAME = config.get("LOG_FILE_NAME") or log_file_name
        self.LOG_FOLDER = config.get("LOG_FOLDER") or log_folder
        self.NAMESPACE = config.get("NAMESPACE") or namespace
        self.COMPRESSION = config.get("COMPRESSION") or compression
        self.redis_instance = Redis(host=self.REDIS_ADDRESS, port=self.REDIS_PORT)

    def _f_write(self, force_compress=False):
        """
        Private function to flush logs to file once memory reaches self.FLUSH_COUNT
        :param force_compress: will forcefully create a new compressed file
        :return:
        """
        if self.LOG_FOLDER:
            file_location = os.path.join(self.LOG_FOLDER, self.LOG_FILE_NAME)
        else:
            file_location = self.LOG_FILE_NAME
        file_location = "%s.log" % file_location
        file_instance = open(file_location, "a")
        redis_dump = "%s\n" % "\n".join(self.redis_instance.lrange(self.NAMESPACE, 0, -1))
        self.redis_instance.delete(self.NAMESPACE)
        file_instance.write(redis_dump)
        file_instance.close()
        if os.path.getsize(file_location) > self.FILE_SIZE or force_compress:
            self._f_compress(file_location)
        return

    def config(self):
        """
        Print the current configuration of the Logist class
        :return: return conf object
        """
        conf = {
            "REDIS_ADDRESS": self.REDIS_ADDRESS,
            "REDIS_PORT": self.REDIS_PORT,
            "FLUSH_COUNT": self.FLUSH_COUNT,
            "FILE_SIZE": self.FILE_SIZE,
            "LOG_FILE_NAME": self.LOG_FILE_NAME,
            "LOG_FOLDER": self.LOG_FOLDER,
            "NAMESPACE": self.NAMESPACE,
            "COMPRESSION": self.COMPRESSION
        }
        return conf

    def _m_write(self, log_type, sub_type, description, log_time=None):
        """
        Private function to write log to memory
        if log count > FLUSH_COUNT defined in settings(default: 10000), dump logs to file
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        log_time = datetime.strftime(log_time or datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
        self.redis_instance.lpush(self.NAMESPACE, "%s >< %s :: %s || %s" %
                                  (log_time, log_type, sub_type, description))
        if self.redis_instance.llen(self.NAMESPACE) >= self.FLUSH_COUNT:
            self._f_write()
        return

    def _f_compress(self, file_location):
        count = 1
        log_file = file_location
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
        """
        Public function for generic logging
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        self._m_write(log_type, sub_type, description, log_time)
        return

    def error(self, sub_type, description, log_time=None):
        """
        Public function for logging ERROR log type
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        self._m_write("ERROR", sub_type, description, log_time)
        return

    def warning(self, sub_type, description, log_time=None):
        """
        Public function for logging WARNING log type
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        self._m_write("WARNING", sub_type, description, log_time)
        return

    def success(self, sub_type, description, log_time=None):
        """
        Public function for logging SUCCESS log type
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        self._m_write("SUCCESS", sub_type, description, log_time)
        return

    def info(self, sub_type, description, log_time=None):
        """
        Public function for logging INFO log type
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        self._m_write("INFO", sub_type, description, log_time)
        return

    def debug(self, sub_type, description, log_time=None):
        """
        Public function for logging DEBUG log type
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param log_time: time of the logging - else auto populate
        :return: None
        """
        self._m_write("DEBUG", sub_type, description, log_time)
        return

    def _analytics_bootstrap(self, source="memory"):
        """
        Private function for bootstrapping log entries
        :param source: run analytics on logs in memory or in the last created file
        :return: None
        """
        # TODO - analytics is not available over compressed files for now
        self.log_list = []
        if source == "file":
            if self.LOG_FOLDER:
                file_name = "%s.log" % os.path.join(self.LOG_FOLDER, self.LOG_FILE_NAME)
            else:
                file_name = "%s.log" % self.LOG_FILE_NAME
            try:
                log_source = open(file_name).readlines()
            except IOError:
                print("File Not Found: %s" % file_name)
                return
        else:
            log_source = self.redis_instance.lrange(self.NAMESPACE, 0, -1)
        for log in log_source:
            log_time = datetime.strptime(log.split(" ><")[0], "%Y-%m-%dT%H:%M:%SZ")
            log_type = log.split(">< ")[1].split(" :: ")[0]
            sub_type = log.split(":: ")[1].split(" || ")[0]
            description = log.split("|| ")[1]
            self.log_list.append([log_time, log_type, sub_type, description])
        return

    def _m_filter(self, log_type="", sub_type="", description="", force_refresh=False):
        """
        Private function to filter over the logs in memory using log_type, sub_type and description
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param force_refresh : refresh cached log list in memory calling _analytics_bootstrap()
        :return: None
        """
        # TODO - needs to pass ranges of log time to filter logs
        if not self.log_list or force_refresh:
            self._analytics_bootstrap()
        filter_query = []
        for log in self.log_list:
            if (log_type and log_type == log[1]) or (sub_type and sub_type == log[2]) or \
                    (description and description in log[3]):
                filter_query.append(log)
        return filter_query

    def _m_count(self, log_type="", sub_type="", description="", force_refresh=False):
        """
        Private function to count the matching logs in memory with filters log_type, sub_type and description
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param force_refresh : refresh cached log list in memory calling _analytics_bootstrap()
        :return: None
        """
        if not self.log_list or force_refresh:
            self._analytics_bootstrap()
        filter_count = 0
        for log in self.log_list:
            if log_type == log[1] or sub_type == log[2] or description == log[3]:
                filter_count += 1
        return filter_count

    def _f_filter(self, log_type="", sub_type="", description="", force_refresh=False):
        """
        Private function to filter over the logs in last created file using log_type, sub_type and description
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param force_refresh : refresh cached log list in memory calling _analytics_bootstrap()
        :return: None
        """
        # TODO - needs to pass ranges of log time to filter logs
        if not self.log_list or force_refresh:
            self._analytics_bootstrap(source="file")
        filter_query = []
        for log in self.log_list:
            if (log_type and log_type == log[1]) or (sub_type and sub_type == log[2]) or \
                    (description and description in log[3]):
                filter_query.append(log)
        return filter_query

    def _f_count(self, log_type="", sub_type="", description="", force_refresh=False):
        """
        Private function to count the matching logs in last created file with filters log_type, sub_type and description
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param force_refresh : refresh cached log list in memory calling _analytics_bootstrap()
        :return: None
        """
        if not self.log_list or force_refresh:
            self._analytics_bootstrap(source="file")
        filter_count = 0
        for log in self.log_list:
            if log_type == log[1] or sub_type == log[2] or description == log[3]:
                filter_count += 1
        return filter_count

    def count(self, log_type="", sub_type="", description="", log_location="memory", force_refresh=False):
        """
        Function to count the matching logs in last created file with filters log_type, sub_type and description
        :param log_location: memory/file
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param force_refresh : refresh cached log list in memory calling _analytics_bootstrap()
        :return: None
        """
        if log_location == "file":
            return self._f_count(log_type, sub_type, description, force_refresh)
        else:
            return self._m_count(log_type, sub_type, description, force_refresh)

    def filter(self, log_type="", sub_type="", description="", log_location="memory", force_refresh=False):
        """
        Function to count the matching logs in last created file with filters log_type, sub_type and description
        :param log_location: memory/file
        :param log_type: type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG
        :param sub_type: custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE
        :param description: brief log description
        :param force_refresh : refresh cached log list in memory calling _analytics_bootstrap()
        :return: None
        """
        if log_location == "file":
            return self._f_filter(log_type, sub_type, description, force_refresh)
        else:
            return self._m_filter(log_type, sub_type, description, force_refresh)
