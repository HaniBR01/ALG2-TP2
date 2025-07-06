import pandas as pd
import time
import sys

from tqdm import tqdm

import logging


# Global variables to store the best solution found so far
# Using globals for simplicity in this recursive example, but for larger applications
# consider passing these through function arguments or using a class.
max_profit = 0
optimal_items_selection = [] # Stores boolean indicating if item at original index is taken

def calculate_bound(level, current_profit, current_weight, capacity, items):
    """
    Calculates the upper bound for the current node using the fractional knapsack approach.
    This is a crucial part for pruning branches effectively.

    Args:
        level (int): The current item index being considered.
        current_profit (float): Profit accumulated so far.
        current_weight (float): Weight accumulated so far.
        capacity (float): Maximum knapsack capacity.
        items (list): List of items, each a tuple (profit, weight, original_index).
                      Assumes items are sorted by profit/weight ratio.

    Returns:
        float: The calculated upper bound.
    """
    remaining_capacity = capacity - current_weight
    bound_profit = current_profit

    # Greedily add remaining items (or fractions) based on profit/weight ratio
    for i in range(level, len(items)):
        item_profit, item_weight, _ = items[i]
        if remaining_capacity >= item_weight:
            # If the whole item fits, add its profit and reduce capacity
            bound_profit += item_profit
            remaining_capacity -= item_weight
        else:
            # If only a fraction fits, add its proportional profit and break
            if item_weight > 0: # Avoid division by zero
                bound_profit += (item_profit / item_weight) * remaining_capacity
            break # Knapsack is full or no more items can fit

    return bound_profit


def _knapsack_bnb_iterative(capacity, items, time_limit_seconds):
    """
    Iterative function for the Branch and Bound algorithm using an explicit stack (DFS).

    Args:
        capacity (float): The maximum capacity of the knapsack.
        items (list): A list of tuples (profit, weight, original_index) for all items,
                      sorted by profit/weight ratio in descending order.
        time_limit_seconds (float): The maximum time allowed for execution in seconds.
    """
    global max_profit, optimal_items_selection, pbar

    # Stack will store tuples: (level, current_profit, current_weight, current_selection_copy)
    # We push the "exclude" branch first, so "include" branch is processed first (DFS behavior)
    stack = []
    
    # Initial state for the "exclude" branch of the first item
    initial_selection = [False] * len(items)
    # The initial node to push onto the stack represents starting before the first item
    # We push the "exclude" branch first so that the "include" branch for the current level
    # is explored first when we pop from the stack (LIFO behavior of stack).
    # This means the first branch considered will be to *include* the first item.
    stack.append((0, 0, 0, initial_selection)) 

    start_time = time.time()
    nodes_explored = 0 # For potential alternative progress tracking

    logger.debug(f"Starting iterative B&B. Initial max_profit: {max_profit}")

    while stack:
        # Check time limit periodically (e.g., every 10,000 nodes)
        nodes_explored += 1
        if nodes_explored % 10000 == 0: # Check every 10,000 nodes
            elapsed_time = time.time() - start_time
            logger.debug(f"Elapsed time: {elapsed_time:.2f}s, Nodes explored: {nodes_explored}, max_profit: {max_profit:.2f}, Stack size: {len(stack)}, Current level: {stack[-1][0] if stack else 'N/A'}")
            if elapsed_time > time_limit_seconds:
                logger.info(f"\nTime limit ({time_limit_seconds:.2f}s) exceeded after {elapsed_time:.2f}s. Terminating Branch and Bound search.")
                # Ensure the progress bar is closed if it's active
                if pbar:
                    pbar.close()
                return # Exit the function, current max_profit is the best found so far

        level, current_profit, current_weight, current_selection = stack.pop()

        # Update tqdm progress bar (based on level)
        # Only update if the current level is higher than what tqdm has recorded
        if pbar and pbar.n < level: # Use 'level' not 'level + 1' for item index
            pbar.update(level - pbar.n)


        # Pruning 1: If current weight exceeds capacity, this path is invalid.
        if current_weight > capacity:
            # logger.debug(f"Pruning at level {level}: weight {current_weight:.2f} > capacity {capacity:.2f}")
            continue # Go to the next node in the stack

        # Base Case: If all items have been considered
        if level == len(items):
            if current_weight <= capacity and current_profit > max_profit:
                # logger.debug(f"Found new best solution at level {level}: Profit {current_profit:.2f}, Weight {current_weight:.2f}")
                max_profit = current_profit
                optimal_items_selection = list(current_selection) # Store a copy
            continue # Go to the next node in the stack

        # Pruning 2: Calculate upper bound for the current node
        upper_bound = calculate_bound(level, current_profit, current_weight, capacity, items)
        if upper_bound <= max_profit:
            # logger.debug(f"Pruning at level {level}: bound {upper_bound:.2f} <= max_profit {max_profit:.2f}")
            continue # Go to the next node in the stack

        # Branching: Consider the current item (items[level])
        item_profit, item_weight, original_index = items[level]

        # Branch 2: Exclude the current item
        # Push the "exclude" branch first, so "include" branch is processed later (DFS)
        # Create a copy of the selection for this branch
        next_selection_exclude = list(current_selection)
        next_selection_exclude[original_index] = False # Ensure it's not taken
        stack.append((level + 1, current_profit, current_weight, next_selection_exclude))
        # logger.debug(f"Pushed exclude branch for item {level+1}. Stack size: {len(stack)}")


        # Branch 1: Include the current item
        # Only push if it's potentially valid (weight constraint)
        if current_weight + item_weight <= capacity:
            # Create a copy of the selection for this branch
            next_selection_include = list(current_selection)
            next_selection_include[original_index] = True
            stack.append((level + 1, current_profit + item_profit, current_weight + item_weight, next_selection_include))
            # logger.debug(f"Pushed include branch for item {level+1}. Stack size: {len(stack)}")
        # else:
            # logger.debug(f"Skipped include branch for item {level+1}: weight {current_weight + item_weight:.2f} > capacity {capacity:.2f}")



def solve_knapsack_bnb(items_data, capacity, time_limit_seconds=10*60): # Default 30 minutes
    """
    Main function to solve the knapsack problem using Branch and Bound.

    Args:
        items_data (list): A list of tuples, where each tuple is (profit, weight).
        capacity (float): The maximum capacity of the knapsack.
        time_limit_seconds (float): Optional. The maximum time allowed for execution in seconds.

    Returns:
        tuple: (optimal_profit, selected_items_list, time_taken)
               optimal_profit (float): The maximum profit achievable.
               selected_items_list (list): A list of (profit, weight) tuples for the selected items.
               time_taken (float): The time taken to execute the algorithm in seconds.
    """
    global max_profit, optimal_items_selection, pbar
    max_profit = 0
    optimal_items_selection = [False] * len(items_data)

    indexed_items = []
    for i, (p, w) in enumerate(items_data):
        if w > 0:
            indexed_items.append((p / w, p, w, i))
        else:
            indexed_items.append((float('inf'), p, w, i))

    sorted_items = sorted(indexed_items, key=lambda x: x[0], reverse=True)
    processed_items = [(item[1], item[2], item[3]) for item in sorted_items]

    # --- Optimization: Initialize max_profit with a greedy heuristic ---
    greedy_current_weight = 0
    greedy_current_profit = 0
    for item_ratio, item_profit, item_weight, original_idx in sorted_items:
        if greedy_current_weight + item_weight <= capacity:
            greedy_current_weight += item_weight
            greedy_current_profit += item_profit
    max_profit = greedy_current_profit
    # ------------------------------------------------------------------

    start_time = time.time()

    # --- TQDM Initialization ---
    with tqdm(total=len(items_data), desc="Processing Items (Iterative B&B)", unit="item") as bar:
        pbar = bar
        _knapsack_bnb_iterative(capacity, processed_items, time_limit_seconds)
    pbar = None

    end_time = time.time()
    time_taken = end_time - start_time

    logger.info(f"Branch and Bound completed in {time_taken:.4f} seconds with {len(items_data)} items processed.")
    final_selected_items = []
    for i, taken in enumerate(optimal_items_selection):
        if taken:
            final_selected_items.append(items_data[i])

    logger.info(f"Max Profit: {max_profit:.2f} with {len(final_selected_items)} items selected.")
    return max_profit, final_selected_items, time_taken

def read_items_from_csv(filepath):
    """
    Reads item data (profit, weight) and knapsack capacity from a CSV file.
    The first line of the CSV is expected to contain:
    [number_of_items] [knapsack_capacity] (space-separated)
    Subsequent lines contain:
    [profit] [weight] (space-separated) for each item.
    This function is specifically tailored for the 'large_scale' dataset format where
    item data is space-separated and there might be additional lines after the items.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        tuple: (items_data, capacity)
               items_data (list): A list of tuples, where each tuple is (profit, weight).
               capacity (float): The maximum capacity of the knapsack.
              Returns ([], 0.0) if there's an error or if no valid items are found.
    """
    items_data = []
    capacity = 0.0
    num_items_expected = 0
    
    try:
        with open(filepath, 'r') as f:
            # Read the first line for number of items and capacity
            first_line = f.readline().strip()
            # Split by any whitespace (robust for single or multiple spaces)
            parts = first_line.split() 
            
            if len(parts) == 2:
                try:
                    num_items_expected = int(parts[0].strip())
                    capacity = float(parts[1].strip())
                    logger.info(f"Read header: Expected {num_items_expected} items, Capacity: {capacity}")
                except ValueError:
                    logger.error(f"Could not parse number of items or capacity from first line: '{first_line}'.")
                    return [], 0.0
            else:
                logger.error(f"First line of CSV must contain 'number_of_items capacity'. Found: '{first_line}'.")
                return [], 0.0

            # Read exactly 'num_items_expected' lines for item data
            for i in range(num_items_expected):
                line = f.readline().strip()
                if not line: # Handle case where file ends prematurely
                    logger.warning(f"File ended prematurely. Expected {num_items_expected} items, but found only {len(items_data)}.")
                    break # Stop reading items

                # Split by any whitespace
                row_parts = line.split()
                
                # Filter out empty strings that might result from multiple spaces
                row_parts = [p for p in row_parts if p]

                if len(row_parts) == 2:
                    try:
                        profit = float(row_parts[0].strip())
                        weight = float(row_parts[1].strip())
                        items_data.append((profit, weight))
                    except ValueError:
                        logger.warning(f"Skipping line {i+2} with non-numeric profit/weight: '{line}'.")
                        # Continue to next line even if this one is malformed, to try and get other items
                        continue
                else:
                    logger.warning(f"Skipping malformed line {i+2} in CSV: '{line}'. Expected 'profit weight'.")
                    # Continue to next line even if this one is malformed
                    continue
        
        if len(items_data) != num_items_expected:
            logger.warning(f"Actual items loaded ({len(items_data)}) does not match expected ({num_items_expected}). Some item lines might have been malformed or skipped.")

        return items_data, capacity
    except FileNotFoundError:
        logger.error(f"CSV file not found at {filepath}")
        return [], 0.0
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return [], 0.0


def run_knapsack(csv_file):
    """
    Example function to run the knapsack solver with a given CSV file.
    This is for demonstration purposes and can be modified as needed.
    
    Args:
        csv_file (str): Path to the CSV file containing items and knapsack capacity.
        
    Returns:
        tuple: (optimal_profit, selected_items, time_taken)
    """
    items, capacity = read_items_from_csv(csv_file)
    if not items:
        logger.info("No items to process or error reading CSV. Exiting.")
        return

    logger.info(f"Knapsack Capacity: {capacity}")
    logger.info(f"{len(items)} items loaded from CSV: {csv_file}")
    optimal_profit, selected_items, time_taken = solve_knapsack_bnb(items, capacity)

    logger.info("\n--- Results ---")
    logger.info(f"Optimal Profit: {optimal_profit:.2f}")
    if selected_items:
        logger.info(f"{len(selected_items)} Selected Items")
    else:
        logger.info("  No items selected (perhaps capacity is too low or no items fit).")

    logger.info(f"Time Taken: {time_taken:.4f} seconds")
    
    return optimal_profit, selected_items, time_taken

# --- Example Usage ---
def test():
    # Create a dummy CSV file for demonstration purposes
    # First line: number_of_items, knapsack_capacity
    dummy_csv_content = "6,50\n"+\
                        "60,10\n"+\
                        "100,20\n"+\
                        "120,30\n"+\
                        "70,15\n"+\
                        "90,25\n"+\
                        "150,35"
    csv_filename = "knapsack_items.csv"
    with open(csv_filename, "w") as f:
        f.write(dummy_csv_content)

    logger.info(f"--- Starting Knapsack Branch and Bound Solver ---")
    logger.info(f"CSV File: {csv_filename}\n")

    # Read items and capacity from the CSV file
    items, knapsack_capacity = read_items_from_csv(csv_filename)

    if not items:
        logger.info("No items to process or error reading CSV. Exiting.")
    else:
        logger.info(f"Knapsack Capacity read from CSV: {knapsack_capacity}")
        logger.info("Items loaded from CSV (Profit, Weight):")
        for i, item in enumerate(items):
            logger.info(f"  Item {i+1}: {item}")
        logger.info("\nSolving...")

        # Solve the knapsack problem
        optimal_profit, selected_items, time_taken = solve_knapsack_bnb(items, knapsack_capacity)

        logger.info("\n--- Results ---")
        logger.info(f"Optimal Profit: {optimal_profit:.2f}")
        logger.info(f"Selected Items (Profit, Weight):")
        if selected_items:
            for item in selected_items:
                logger.info(f"  {item}")
        else:
            logger.info("  No items selected (perhaps capacity is too low or no items fit).")

        logger.info(f"Time Taken: {time_taken:.4f} seconds")

        # As per the problem description, check for the 30-minute limit
        thirty_minutes_in_seconds = 30 * 60
        if time_taken > thirty_minutes_in_seconds:
            logger.info(f"\nWARNING: Execution time ({time_taken:.2f}s) exceeded the 30-minute limit.")
            logger.info("According to the problem statement, results for this run should be marked as 'NA'.")
