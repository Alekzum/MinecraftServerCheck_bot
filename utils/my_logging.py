import logging


FORMAT = '%(asctime)s - %(levelname)s (%(name)s) - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
