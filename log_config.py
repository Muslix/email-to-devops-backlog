import logging
import logging.config
import json

def setup_logging():
    try:
        with open('logging_config.json', 'r') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    except Exception as e:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        logger.error("Failed to load configuration file. Using default configs", exc_info=True)
    return logging.getLogger(__name__)