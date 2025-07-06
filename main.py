# system imports
import os
import psutil
import subprocess
from datetime import datetime, timedelta
import argparse
import time


# Local Utility imports
import modules.utils as ut
from modules.logger import setup_logger



# Constants
CURRENT_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")


config = ut.load_config()

LOG_PATH = config["log_dir"] + f"branch_and_bound_{CURRENT_TIME}.log"
logger = setup_logger(LOG_PATH)


logger.info(f"Log file created at: {LOG_PATH}")

# Local File Handling imports
import modules.read_file as file_module
file_module.logger = logger


def main():
    
    logger.info("getting files from dataset and optimal directories...")
    file_names = file_module.get_files(
            dataset_dir=config["dataset_dir"],
            optimum_dir=config["optimal_dataset_dir"]
        )

    logger.info(f"main function ended successfully, returning 0")
    return 0
        
if __name__ == "__main__":
    logger.info("Starting the branch and bound algorithm...")
    start_time = datetime.now()
    success = True
    try:
        success = (main() == 0)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        success = False
        
    logger.debug(f"Script execution success status: {success}")
    if success:
        logger.info("Script completed successfully.")
    else:
        logger.error("Script encountered an error during execution.")
    final_time = datetime.now()
    elapsed_time = final_time - start_time
    logger.info(f"Script completed in {elapsed_time}.")
    
    logger.info("Branch and bound algorithm finished.")