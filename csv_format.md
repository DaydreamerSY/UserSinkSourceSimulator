# **CSV Data Formats for Game Simulator**

This document outlines the required CSV formats to load data into the game economy simulator. The system is designed around an item-centric architecture, with a master items.csv file defining all in-game resources.

## **1\. Items (items.csv)**

This file serves as the master definition for all resources available in the game, including currencies and boosters. It is the single source of truth for all items.

### **Format**

| item\_name | item\_type | price | effectiveness |
| :---- | :---- | :---- | :---- |
| string | string | int | float |

### **Column Descriptions**

* **item\_name**: The unique string identifier for the item (e.g., "Speedy Time", "coins").  
* **item\_type**: The item's category. Use **currency** for monetary items and **booster** for items that provide a gameplay advantage.  
* **price**: The item's value in the game's base currency. For the base currency itself (e.g., coins), this value should be 1\.  
* **effectiveness**: For items of type booster, this is a float value between 0.0 and 1.0 representing the percentage of time reduction it provides. For all other item types, this should be 0.0.

### **Example: items.csv**

item\_name,item\_type,price,effectiveness  
coins,currency,1,0.0  
Speedy Time,booster,50,0.2  
Mega Clear,booster,75,0.35

## **2\. Levels (levels.csv)**

This file defines the properties and rewards for each level in the game.

### **Format**

| level\_id | base\_duration | difficulty | reward\_1\_name | reward\_1\_amount | reward\_2\_name | reward\_2\_amount |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| int | int | float | string | int | string | int |

### **Column Descriptions**

* **level\_id**: The unique integer ID for the level.  
* **base\_duration**: The expected completion time in seconds for a player of average skill without using any boosters.  
* **difficulty**: A float between 0.0 and 1.0 representing the level's challenge.  
* **reward\_\[N\]\_name**: The name of the Nth reward granted upon level completion. This name must correspond to an item\_name in the items.csv file.  
* **reward\_\[N\]\_amount**: The quantity of the Nth reward to be granted.

### **Example: levels.csv**

level\_id,base\_duration,difficulty,reward\_1\_name,reward\_1\_amount,reward\_2\_name,reward\_2\_amount  
1,60,0.1,coins,50,,  
2,75,0.15,coins,75,Speedy Time,1

## **3\. Players (players.csv)**

This file defines the different player archetypes for the simulation. The initial inventory for all archetypes is standardized within the simulation script and is not defined in this file.

### **Format**

| player\_id | skill\_potential | booster\_tendency | daily\_playtime\_budget |
| :---- | :---- | :---- | :---- |
| string | float | float | int |

### **Column Descriptions**

* **player\_id**: A unique string identifier for the player archetype.  
* **skill\_potential**: A float between 0.0 and 1.0 representing the player's innate skill level.  
* **booster\_tendency**: A float between 0.0 and 1.0 representing the player's baseline willingness to use boosters.  
* **daily\_playtime\_budget**: The total number of seconds the player archetype is expected to play per day.

### **Example: players.csv**

player\_id,skill\_potential,booster\_tendency,daily\_playtime\_budget  
Frugal\_Expert,0.8,0.1,1800  
Average\_Joe,0.5,0.5,1800  
Rich\_Spender,0.2,0.9,1800  
