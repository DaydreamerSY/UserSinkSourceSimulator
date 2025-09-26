import random
import math
import os
from typing import List, Dict, Any
from data_loader import load_simulation_data

# ==============================================================================
# 1. CORE DATA MODELS (Refactored to be Item-centric)
# ==============================================================================

class Item:
    """Represents a single type of item (currency or booster) with its properties."""
    def __init__(self, item_name: str, item_type: str, price: int, effectiveness: float):
        self.name = item_name
        self.item_type = item_type
        self.price = price
        self.effectiveness = effectiveness

    def __repr__(self) -> str:
        return f"Item(name='{self.name}', type='{self.item_type}')"

class Level:
    """Represents a single level in the game. (No changes needed here)"""
    def __init__(self, level_id: int, base_duration: int, difficulty: float, rewards: Dict[str, Any]):
        self.level_id = level_id
        self.base_duration = base_duration
        self.difficulty = difficulty
        self.rewards = rewards
    def __repr__(self) -> str: return f"Level(id={self.level_id}, difficulty={self.difficulty:.2f})"

class Player:
    """Represents a player archetype with their stats and inventory."""
    def __init__(self, player_id: str, skill_potential: float, booster_tendency: float, daily_playtime_budget: int, initial_inventory: Dict[str, Any]):
        self.player_id = player_id
        self.skill_potential = skill_potential
        self.booster_tendency = booster_tendency
        self.initial_playtime = daily_playtime_budget
        self.daily_playtime_budget = daily_playtime_budget
        self.inventory = { 'coins': initial_inventory.get('coins', 0), 'boosters': initial_inventory.get('boosters', {}).copy() }
        self.current_level = 0
        self.days_to_reach_target = None
        
    def get_total_boosters(self) -> int:
        return sum(self.inventory['boosters'].values())

    def has_boosters(self) -> bool:
        return self.get_total_boosters() > 0

    def consume_boosters(self, quantity: int, item_definitions: Dict[str, Item]):
        total_effectiveness = 0.0
        consumed_count = 0
        owned_boosters = [b for b, count in self.inventory['boosters'].items() if count > 0]
        random.shuffle(owned_boosters)
        for booster_name in owned_boosters:
            if consumed_count >= quantity: break
            self.inventory['boosters'][booster_name] -= 1
            total_effectiveness += item_definitions[booster_name].effectiveness
            consumed_count += 1
        return total_effectiveness

    def add_rewards(self, rewards: Dict[str, Any]):
        self.inventory['coins'] += rewards.get('coins', 0)
        booster_rewards = rewards.get('boosters', {})
        for name, count in booster_rewards.items(): self.inventory['boosters'][name] = self.inventory['boosters'].get(name, 0) + count
    def reset_daily_playtime(self): self.daily_playtime_budget = self.initial_playtime
    def __repr__(self) -> str: return f"Player(id='{self.player_id}', level={self.current_level}, coins={self.inventory['coins']}, boosters={self.get_total_boosters()})"

# ==============================================================================
# 2. THE SIMULATOR ENGINE
# ==============================================================================

class GameSimulator:
    MAX_BOOSTERS_PER_LEVEL = 3
    def __init__(self, players: List[Player], levels: List[Level], item_definitions: Dict[str, Item]):
        self.players = players
        self.levels = sorted(levels, key=lambda lvl: lvl.level_id)
        self.item_definitions = item_definitions
        self.log = []

    def _simulate_level_attempt(self, player: Player, level: Level):
        struggle_score = max(0, level.difficulty - player.skill_potential)
        prob_to_use = player.booster_tendency + (struggle_score * (1 - player.booster_tendency))
        boosters_to_use = 0
        booster_effectiveness = 0.0

        # The core logic now correctly checks if the player has any items of type 'booster'
        if player.has_boosters() and random.random() < prob_to_use:
            scores = [(1 + struggle_score) ** k for k in range(1, self.MAX_BOOSTERS_PER_LEVEL + 1)]
            chosen_quantity = random.choices(population=range(1, self.MAX_BOOSTERS_PER_LEVEL + 1), weights=scores, k=1)[0]
            boosters_to_use = min(chosen_quantity, player.get_total_boosters())
        
        base_time_cost = level.base_duration * (1 + struggle_score)
        if boosters_to_use > 0:
            booster_effectiveness = player.consume_boosters(boosters_to_use, self.item_definitions)

        final_playtime = math.ceil(base_time_cost * (1 - booster_effectiveness))
        return { "playtime": final_playtime, "boosters_used": boosters_to_use, "struggle_score": struggle_score }

    # The run_simulation and summary methods remain largely the same, so they are condensed for brevity.
    def _run_simulation_to_level(self, target_level: int):
        day = 0
        while any(p.current_level < target_level for p in self.players):
            day += 1; print(f"\n==================== DAY {day} ====================")
            if all(p.current_level >= len(self.levels) for p in self.players if p.current_level < target_level): print("\n[STOP] All players have run out of available levels before reaching the target."); break
            for player in self.players:
                if player.current_level >= target_level: continue
                player.reset_daily_playtime()
                print(f"\n[SIMULATING] Player: {player.player_id} (Target: Lv.{target_level})")
                while player.daily_playtime_budget > 0 and player.current_level < target_level and player.current_level < len(self.levels):
                    current_level_obj = self.levels[player.current_level]
                    attempt_result = self._simulate_level_attempt(player, current_level_obj)
                    playtime_cost = attempt_result["playtime"]
                    if player.daily_playtime_budget < playtime_cost: break
                    player.daily_playtime_budget -= playtime_cost
                    player.add_rewards(current_level_obj.rewards)
                    player.current_level += 1
                    if player.current_level == target_level and player.days_to_reach_target is None: player.days_to_reach_target = day
                    log_entry = { "day": day, "player_id": player.player_id, "level_id": current_level_obj.level_id, "struggle_score": f"{attempt_result['struggle_score']:.2f}", "boosters_used": attempt_result['boosters_used'], "playtime_cost": playtime_cost, "playtime_left": player.daily_playtime_budget, "final_coins": player.inventory['coins'], "final_boosters": player.get_total_boosters()}
                    self.log.append(log_entry)
    def run_simulation(self, target_level: int):
        self.log = []; print("--- Starting Game Simulation ---")
        if not self.players or not self.levels: print("No player or level data loaded. Aborting simulation."); return
        self._run_simulation_to_level(target_level)
        print("\n--- Simulation Complete ---"); return self.log
    def print_player_information_summary(self):
        print("\n--- Final Player Information Summary ---")
        for player in self.players:
            print(f"Player: {player.player_id}\n  - Archetype Stats:\n    - Skill Potential: {player.skill_potential}\n    - Booster Tendency: {player.booster_tendency}\n  - Final State:\n    - Reached Level: {player.current_level}")
            if player.days_to_reach_target: print(f"    - Days to Reach Target: {player.days_to_reach_target}")
            print(f"    - Final Coins:   {player.inventory['coins']}\n    - Final Boosters:")
            if not player.inventory['boosters'] or all(v == 0 for v in player.inventory['boosters'].values()): print("      - None")
            else:
                for name, count in player.inventory['boosters'].items():
                    if count > 0: print(f"      - {name}: {count}")
            print("-" * 30)

# ==============================================================================
# 3. SIMULATION SETUP & EXECUTION
# ==============================================================================

def create_dummy_csv_files():
    """Generates example CSV files with the new item-centric format."""
    
    # --- items.csv (NEW) ---
    items_csv = "item_name,item_type,price,effectiveness\ncoins,currency,1,0.0\nSpeedy Time,booster,50,0.2\nMega Clear,booster,75,0.35\n"
    with open("items.csv", "w") as f: f.write(items_csv)

    # --- levels.csv (simplified rewards) ---
    levels_csv = "level_id,base_duration,difficulty,reward_1_name,reward_1_amount,reward_2_name,reward_2_amount\n"
    for i in range(1, 101):
        rewards = [f"coins,{10 + i * 2}"]
        if i % 5 == 0: rewards.append(f"Speedy Time,1")
        line = f"{i},{60 + i * 5},{0.1 + (i / 100) * 0.8},{','.join(rewards)}"
        if len(rewards) == 1: line += ",,"
        levels_csv += line + "\n"
    with open("levels.csv", "w") as f: f.write(levels_csv)

    # --- players.csv (simplified - no inventory) ---
    players_csv = "player_id,skill_potential,booster_tendency,daily_playtime_budget\nFrugal_Expert,0.8,0.1,1800\nAverage_Joe,0.5,0.5,1800\nRich_Spender,0.2,0.9,1800\n"
    with open("players.csv", "w") as f: f.write(players_csv)

    print("Created dummy CSV files: items.csv, levels.csv, players.csv")

if __name__ == "__main__":
    
    # Define the default inventory that all players will start with
    DEFAULT_INIT_INVENTORY = {
        'coins': 100,
        'boosters': {
            'Speedy Time': 3,
            'Mega Clear': 1
        }
    }

    create_dummy_csv_files()

    item_definitions, level_list, player_archetypes = load_simulation_data(
        items_path="items.csv",
        levels_path="levels.csv",
        players_path="players.csv",
        default_inventory=DEFAULT_INIT_INVENTORY
    )

    if item_definitions: # Check if data loaded successfully
        TARGET_LEVEL = 54
        simulator = GameSimulator(player_archetypes, level_list, item_definitions)
        simulation_log = simulator.run_simulation(target_level=TARGET_LEVEL)
        simulator.print_player_information_summary()

    # Clean up the created CSV files
    for f in ["items.csv", "levels.csv", "players.csv"]:
        if os.path.exists(f): os.remove(f)
    print("\nCleaned up temporary CSV files.")

