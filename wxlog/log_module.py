import logging


logger = None

def log_init(log_file: str):
    global logger
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('wxbot')

def log_info(message):
    global logger
    if logger:
        logger.info(message)

def log_error(message):
    global logger
    if logger:
        logger.error(message)

if __name__ == '__main__':
    log_init("log.txt")