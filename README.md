Logist
------

Easy logging system for humans and machines
 
A redis backed logging system with a performance of 6000 logs/second.
 
 
## Documentation

### Installation

```bash
pip install logist
```
    
### Basic Usage

```python
from logist import Logist
logger = Logist()
logger.log(log_type, sub_type, description, log_time)
```

**log_type:** type of log - ERROR, WARNING, SUCCESS, INFO, DEBUG

**sub_type:** custom log sub types for easy tracking - Eg: ACCESS, WRITE, READ, EDIT, DELETE

**description:** brief log description

**log_time:** time of the logging - else auto populate



### Specific Functions

#### Success
```python
logger.success("API_LOOKUP", "20301 bytes of json data served")
```

#### Warning
```python
logger.warning("API_LOOKUP", "301 bytes of json data served")
```

#### Info
```python
logger.info("API_LOOKUP", "20301 bytes of json data served")
```

#### Error
```python
logger.error("API_LOOKUP_ERROR", "0 bytes of json data served")
```

#### Debug
```python
logger.debug("API_LOOKUP_DEBUG", "2301 bytes of csv data served")
```


### Configuration Options

REDIS_ADDRESS: Address to redis server
REDIS_PORT: redis server port
FLUSH_COUNT: log count when in-memory logs to be flushed to file
FILE_SIZE: file size when log file to be split up and compressed
LOG_FILE_NAME: name of the log file
LOG_FOLDER: folder for log files
NAMESPACE: a custom namespace for logs to be kept in redis server
COMPRESSION: a boolean field to enable/disable compression (True/False)


Either, create a configuration file with name ```logist_config.json``` in the pwd, like below

```json
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
```

or

create Logist objects with custom configuration options required as shown below

```python
logger = Logist(redis_address="localhost", redis_port=6379, flush_count=10000, file_size=10000000,
                 log_file_name="default", log_folder="", namespace="DEFAULT", compression=True)
```

### Advanced Features

#### Filter

Advanced feature to filter logs as required based on log_type, sub_type, description and log_location.
force_refresh is used to reload the index from the source file/memory

```python
logger.filter(log_type="", sub_type="", description="", log_location="memory", force_refresh=False)
```
NB: Exact match for ```log_type``` and ```sub_type```. Contains for ```description```


#### Count

Advanced feature to filter logs as required based on log_type, sub_type, description and log_location.
force_refresh is used to reload the index from the source file/memory

```python
logger.count(log_type="", sub_type="", description="", log_location="memory", force_refresh=False)
```