import yaml

from datetime import datetime as dt
from dotmap import DotMap

from config.logger import get_logger
from utils.etl import CoinGeckoETL

if __name__ == "__main__":
    YAML_PATH = './config/config.yml'
    with open(YAML_PATH, encoding='utf-8') as f:
        content = DotMap(yaml.safe_load(f), _dynamic=False)

    logger = get_logger()

    logger.info('Extracting crypto data from CoinGecko')
    logger.info(f' > Execution date: {dt.today().strftime("%Y-%m-%d")}')
    logger.info('')

    logger.info('Starting ETL...')
    CoinGeckoETL(logger=logger, url=content.url, paths=content.paths).run_etl()
    logger.info('ETL finished!')
    logger.info('')