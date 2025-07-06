# system imports
import os
import psutil
import subprocess
from datetime import datetime, timedelta
import argparse
import time

import pandas as pd

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

import modules.branch_and_bound as bb_module
bb_module.logger = logger

def main():
    
    logger.info("getting files from dataset and optimal directories...")
    file_names = file_module.get_files(
            dataset_dir=config["dataset_dir"],
            optimum_dir=config["optimal_dataset_dir"]
        )
    
    optimum = {}
    for file_name in file_names:
        logger.info(f"Processing file: {file_name}")
        file_path = os.path.join(config["dataset_dir"], file_name)
        
        
        # Solve the knapsack problem using branch and bound
        optimal_profit, selected_items, time_taken = bb_module.run_knapsack(file_path)
        logger.info(f"Optimal profit for {file_name}: {optimal_profit} in {time_taken:.4f} seconds")
        logger.debug(f"Selected items: {selected_items}")
        # Store the optimal profit and selected items
        optimum[file_name] = {
            "optimal_profit": optimal_profit,
            "selected_items": selected_items,
            "time_taken": time_taken
        }
    
    # Save the results to a file
    output_file = os.path.join(config["branch_and_bound_results_dir"], f"branch_and_bound_results_{os.path.basename(config["dataset_dir"])}.csv")
    pd.DataFrame.from_dict(optimum, orient='index').to_csv(output_file, sep=config["file_delimiter"])
    logger.info(f"Results saved to {output_file}")
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