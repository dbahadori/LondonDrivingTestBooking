import logging
import os

import src.utils.app_utils
from config.config_loader import load_config
from src.infrastructure.database.database_factory import DatabaseFactory
from src.infrastructure.database.repositories.repository_factory import RepositoryFactory
from src.infrastructure.messaging.publisher_factory import PublisherFactory
from src.pipelines.data_pipeline_manager import DataPipelineManager
from src.loading.data_ingestion_service import DataIngestionService
from src.loading.cleaning.cleaner_factory import CleanerFactory
from src.loading.cleaning.similarity_deduplication_strategy import SimilarityDeduplicationStrategy
from src.utils.browser_utils import BrowserUtils
from src.utils.url_utils import URLChecker

if __name__ == "__main__":
    # Get the directory of the current script (app_manager.py)
    base_dir = src.utils.app_utils.get_project_root()

    # Construct the path relative to the script's directory
    config_path = os.path.join(base_dir, "config/base_url_config.yaml")

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Base directory: {base_dir}")
    logging.info(f"Config path: {config_path}")

    # Load the config
    config = load_config(config_path)

    # Initialize necessary components

    url_checker = URLChecker()

    database_factory = DatabaseFactory(config=config.DataBase)
    db_client = database_factory.create_client()
    repository_factory = RepositoryFactory(client=db_client)
    browser_utils = BrowserUtils()

    # use PublisherFactory to get the correct publisher based on config
    publisher_factory = PublisherFactory(config.MessageBroker)
    publisher = publisher_factory.get_publisher()

    data_ingestion_service = DataIngestionService(publisher)

    data_cleaner_directory_path = os.path.join("CleanedFundData",
                                               URLChecker.extract_domain(config.Settings.base_urls[0].url))
    cleaner_factory = CleanerFactory(SimilarityDeduplicationStrategy(), data_cleaner_directory_path)

    # Create an AppManager instance
    pipeline_manager = DataPipelineManager(config=config,
                                      url_checker=url_checker,
                                      browser_utils=browser_utils,
                                      cleaner_factory=cleaner_factory,
                                      data_ingestion_service=data_ingestion_service,
                                      repository_factory=repository_factory)

    # Run the ETL process
    pipeline_manager.run_etl()
