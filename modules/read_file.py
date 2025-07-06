# System imports
import os

# Logging import 
import logging


def get_files(dataset_dir: str, optimum_dir: str):
    logger.debug(f"getting files from dataset directory: {dataset_dir} and optimum directory: {optimum_dir}")
    try:
        dataset_files = [
            file
            for file in os.listdir(dataset_dir)
            if os.path.isfile(os.path.join(dataset_dir, file))
        ]
    except Exception as e:
        logger.error(f"Error reading dataset directory '{dataset_dir}': {e}")
        raise

    try:
        optimal_files = [
            file
            for file in os.listdir(optimum_dir)
            if os.path.isfile(os.path.join(optimum_dir, file))
        ]
    except Exception as e:
        logger.error(f"Error reading optimum directory '{optimum_dir}': {e}")
        raise

    logger.info(f"Found {len(dataset_files)} files in dataset directory: {dataset_dir}"
                f" and {len(optimal_files)} files in optimum directory: {optimum_dir}")
    if set(optimal_files) != set(dataset_files):
        logger.error("Dataset and optimal files do not match. Please check the directories.")
        logger.debug(f"Dataset files: {dataset_files}")
        logger.debug(f"Optimal files: {optimal_files}")
        raise FileNotFoundError("Dataset and optimal files do not match. Please check the directories.")

    logger.info(f"Checking if dataset and optimal files match...")
    logger.debug(f"Dataset files: {dataset_files}")
    logger.debug(f"Optimal files: {optimal_files}")
    if set(optimal_files) != set(dataset_files):
        logger.error("Dataset and optimal files do not match. Please check the directories.")
        logger.debug(f"Dataset files: {dataset_files}")
        logger.debug(f"Optimal files: {optimal_files}")
        raise AssertionError("Dataset and optimal files do not match. Please check the directories.")

    logger.info(f"Dataset and optimal files match. Proceeding with {len(dataset_files)} files.")
    return dataset_files