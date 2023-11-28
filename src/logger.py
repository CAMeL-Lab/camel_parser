
import functools
import logging
import os
import time
from datetime import datetime

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger()

log_path = f'{os.getcwd()}/logs.txt'
    
with open(log_path, 'a') as f:
    f.write(f'[{datetime.now().strftime("%d/%b/%Y %H:%M:%S")}]\n')

def map_function_to_phrase(function_name):
    """Replace logged function name with a proper phrase.
    """
    if function_name == "parse":
        return "parsing duration"
    elif function_name == "get_disambiguator":
        return "disambiguator setup duration"
    else:
        return function_name

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:

            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            with open(log_path, 'a') as f:
                f.write(f'{map_function_to_phrase(func.__name__)}: {round(end_time - start_time, 2)}s\n')
            return result
        except Exception as e:
            logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
            raise e

    return wrapper
