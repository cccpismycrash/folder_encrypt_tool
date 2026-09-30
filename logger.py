import logging
from pathlib import Path


util_name = Path(__file__).parent.name

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s\t%(name)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(util_name)