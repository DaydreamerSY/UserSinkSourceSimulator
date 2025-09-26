import pandas as pd
from typing import List, Dict, Any
# The classes will now be imported from the refactored simulator
from game_simulator import Item, Level, Player

def _parse_dynamic_item_columns(row: pd.Series, prefix: str, item_definitions: Dict[str, Item]) -> Dict[str, Any]:
    """
    Parses dynamic columns for rewards or inventory based on a master item list.
    """
    parsed_data = {'coins': 0, 'boosters': {}}
    i = 1
    while f'{prefix}{i}_name' in row and pd.notna(row[f'{prefix}{i}_name']):
        item_name = row[f'{prefix}{i}_name']
        item_amount = int(row[f'{prefix}{i}_amount'])
        
        # Look up the item type from our master list
        if item_name in item_definitions:
            item_info = item_definitions[item_name]
            if item_info.item_type == 'currency':
                parsed_data['coins'] += item_amount
            elif item_info.item_type == 'booster':
                parsed_data['boosters'][item_name] = parsed_data['boosters'].get(item_name, 0) + item_amount
        
        i += 1
    return parsed_data

def load_simulation_data(items_path: str, levels_path: str, players_path: str, default_inventory: Dict) -> tuple:
    """
    Reads CSV files and populates the simulation with Item, Level, and Player objects.
    """
    try:
        # 1. Load Master Item List (replaces boosters)
        items_df = pd.read_csv(items_path)
        item_list = [Item(**row) for _, row in items_df.iterrows()]
        item_definitions = {item.name: item for item in item_list}
        
        # 2. Load Levels
        levels_df = pd.read_csv(levels_path)
        level_list = []
        for _, row in levels_df.iterrows():
            # Use the item definitions to parse rewards correctly
            rewards = _parse_dynamic_item_columns(row, prefix='reward_', item_definitions=item_definitions)
            level = Level(
                level_id=int(row['level_id']),
                base_duration=int(row['base_duration']),
                difficulty=float(row['difficulty']),
                rewards=rewards
            )
            level_list.append(level)

        # 3. Load Players (without inventory from CSV)
        players_df = pd.read_csv(players_path)
        player_list = []
        for _, row in players_df.iterrows():
            player = Player(
                player_id=row['player_id'],
                skill_potential=float(row['skill_potential']),
                booster_tendency=float(row['booster_tendency']),
                daily_playtime_budget=int(row['daily_playtime_budget']),
                # Assign the default inventory passed to the function
                initial_inventory=default_inventory
            )
            player_list.append(player)
            
        print("Successfully loaded all data from CSV files.")
        return item_definitions, level_list, player_list

    except FileNotFoundError as e:
        print(f"Error: Could not find a required data file: {e.filename}")
        return {}, [], []
    except KeyError as e:
        print(f"Error: A required column is missing from a CSV file: {e}")
        return {}, [], []

