import os
import logging
from datetime import datetime as dt

def get_logger():
    log_filepath = os.path.join('logs', f'log-{dt.now().strftime("%Y-%m-%d-%H-%M-%S")}.log')

    logging.basicConfig(
        filename = log_filepath,
        filemode = 'w', 
        format   = u'%(asctime)s | %(levelname)s | %(message)s', 
        datefmt  = '%H:%M:%S',
        level    = 'INFO'
    )

    return logging.getLogger('coingecko-app')