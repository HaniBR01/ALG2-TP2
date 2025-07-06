import pandas as pd
import time
import sys

import logging
logger = logging.getLogger(__name__)

# Set a higher recursion limit for deep search trees, common in Branch and Bound
# Be cautious with very large datasets, as this can still lead to StackOverflowError
sys.setrecursionlimit(20000) # Increased from default 1000

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

def _knapsack_bnb_recursive(level, current_profit, current_weight, capacity, items, current_selection):
    """
    Recursive function for the Branch and Bound algorithm (Depth-First Search).

    Args:
        level (int): The index of the item currently being considered.
        current_profit (float): The total profit of items selected so far in this path.
        current_weight (float): The total weight of items selected so far in this path.
        capacity (float): The maximum capacity of the knapsack.
        items (list): A list of tuples (profit, weight, original_index) for all items,
                      sorted by profit/weight ratio in descending order.
        current_selection (list): A boolean list representing the selection of items
                                  for the current path, indexed by original_index.
    """
    global max_profit, optimal_items_selection

    # Pruning 1: If current weight exceeds capacity, this path is invalid.
    if current_weight > capacity:
        return

    # Base Case: If all items have been considered
    if level == len(items):
        # If this is a valid solution and better than the best found so far
        if current_weight <= capacity and current_profit > max_profit:
            max_profit = current_profit
            # Store a copy of the current selection as the new optimal
            optimal_items_selection = list(current_selection)
        return

    # Pruning 2: Calculate upper bound for the current node
    # If the upper bound of this node is less than or equal to the best profit found so far,
    # then this branch cannot lead to a better solution, so we prune it.
    upper_bound = calculate_bound(level, current_profit, current_weight, capacity, items)
    if upper_bound <= max_profit:
        return

    # Branching: Consider the current item (items[level])
    item_profit, item_weight, original_index = items[level]

    # Branch 1: Include the current item
    # Temporarily mark the item as taken in the current_selection
    current_selection[original_index] = True
    _knapsack_bnb_recursive(level + 1, current_profit + item_profit, current_weight + item_weight, capacity, items, current_selection)

    # Branch 2: Exclude the current item
    # Reset the selection for this item for the "exclude" branch
    current_selection[original_index] = False
    _knapsack_bnb_recursive(level + 1, current_profit, current_weight, capacity, items, current_selection)


def solve_knapsack_bnb(items_data, capacity):
    """
    Main function to solve the knapsack problem using Branch and Bound.

    Args:
        items_data (list): A list of tuples, where each tuple is (profit, weight).
        capacity (float): The maximum capacity of the knapsack.

    Returns:
        tuple: (optimal_profit, selected_items_list, time_taken)
               optimal_profit (float): The maximum profit achievable.
               selected_items_list (list): A list of (profit, weight) tuples for the selected items.
               time_taken (float): The time taken to execute the algorithm in seconds.
    """
    global max_profit, optimal_items_selection
    max_profit = 0
    # Initialize optimal_items_selection with False for each item based on its original index
    optimal_items_selection = [False] * len(items_data)

    # Sort items by profit/weight ratio in descending order.
    # This heuristic helps the bounding function to be more effective and
    # potentially find good solutions earlier in the DFS.
    # We also store the original index to reconstruct the solution correctly.
    indexed_items = []
    for i, (p, w) in enumerate(items_data):
        if w > 0: # Avoid division by zero for ratio
            indexed_items.append((p / w, p, w, i))
        else: # Handle items with zero weight (if allowed, they can always be taken for free profit)
            indexed_items.append((float('inf'), p, w, i)) # Assign infinite ratio for zero weight

    sorted_items = sorted(indexed_items, key=lambda x: x[0], reverse=True)
    # Convert back to (profit, weight, original_index) for easier recursive function arguments
    processed_items = [(item[1], item[2], item[3]) for item in sorted_items]

    # --- Optimization: Initialize max_profit with a greedy heuristic ---
    # This helps prune branches earlier by starting with a better lower bound.
    greedy_current_weight = 0
    greedy_current_profit = 0
    for item_ratio, item_profit, item_weight, original_idx in sorted_items:
        if greedy_current_weight + item_weight <= capacity:
            greedy_current_weight += item_weight
            greedy_current_profit += item_profit
    # Set the initial max_profit to the profit found by the greedy heuristic
    max_profit = greedy_current_profit
    # Note: We don't need to store the greedy selection in optimal_items_selection yet,
    # as the B&B will find and store the true optimal.
    # ------------------------------------------------------------------

    start_time = time.time()

    # Start the recursive Branch and Bound process
    # current_selection is passed as a mutable list to track selections across recursive calls
    _knapsack_bnb_recursive(0, 0, 0, capacity, processed_items, [False] * len(items_data))

    end_time = time.time()
    time_taken = end_time - start_time

    # Reconstruct the list of selected items based on the optimal_items_selection
    final_selected_items = []
    for i, taken in enumerate(optimal_items_selection):
        if taken:
            final_selected_items.append(items_data[i])

    return max_profit, final_selected_items, time_taken

def read_items_from_csv(filepath):
    """
    Reads item data (profit, weight) and knapsack capacity from a CSV file.
    The first line of the CSV is expected to contain:
    [number_of_items], [knapsack_capacity]
    Subsequent lines contain:
    [profit], [weight] for each item.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        tuple: (items_data, capacity)
               items_data (list): A list of tuples, where each tuple is (profit, weight).
               capacity (float): The maximum capacity of the knapsack.
              Returns ([], 0.0) if there's an error.
    """
    items_data = []
    capacity = 0.0
    try:
        with open(filepath, 'r') as f:
            # Read the first line for number of items and capacity
            first_line = f.readline().strip()
            parts = first_line.split(' ')
            if len(parts) != 2:
                logger.info("Error: First line of CSV must contain 'number_of_items knapsack_capacity'.")
                return [], 0.0
            
            num_items_expected = int(parts[0].strip())
            capacity = float(parts[1].strip())

            # Read the remaining lines for item data
            for line_num, line in enumerate(f, 2): # Start line_num from 2 for error messages
                line = line.strip()
                if not line: # Skip empty lines
                    continue
                row_parts = line.split(' ')
                if len(row_parts) != 2:
                    logger.info(f"Warning: Skipping malformed line {line_num} in CSV: '{line[:30]}...'. Expected 'profit weight'.")
                    continue
                
                try:
                    profit = float(row_parts[0].strip())
                    weight = float(row_parts[1].strip())
                    items_data.append((profit, weight))
                except ValueError:
                    logger.info(f"Warning: Skipping line {line_num} with non-numeric profit/weight: '{line}'.")
                    continue
        
        if len(items_data) != num_items_expected:
            logger.info(f"Warning: Expected {num_items_expected} items based on first line, but found {len(items_data)} items.")

        return items_data, capacity
    except FileNotFoundError:
        logger.info(f"Error: CSV file not found at {filepath}")
        return [], 0.0
    except Exception as e:
        logger.info(f"Error reading CSV file: {e}")
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
