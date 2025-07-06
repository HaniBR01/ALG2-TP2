

def load_config(config_path: str = "config.json") -> dict:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path (str): Path to the configuration file.
        
    Returns:
        dict: Configuration settings.
    """
    import json
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config