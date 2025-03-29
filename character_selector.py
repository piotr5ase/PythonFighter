import os

def load_available_characters():
    characters_dir = "assets/characters"
    characters = [d for d in os.listdir(characters_dir) if os.path.isdir(os.path.join(characters_dir, d))]
    return characters

def load_available_maps():
    maps_dir = "assets/stages"
    maps = [d for d in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, d))]
    return maps

def character_selector(player_num):
    available_characters = load_available_characters()
    print(f"Player {player_num}, select your character:")
    for i, character in enumerate(available_characters):
        print(f"{i + 1}. {character}")
    choice = int(input(f"Enter the number of your choice (1-{len(available_characters)}): ")) - 1
    return os.path.join("assets/characters", available_characters[choice], "character.json")

def map_selector():
    available_maps = load_available_maps()
    print("Select a map:")
    for i, map_name in enumerate(available_maps):
        print(f"{i + 1}. {map_name}")
    choice = int(input(f"Enter the number of your choice (1-{len(available_maps)}): ")) - 1
    return os.path.join("assets/stages", available_maps[choice], "map.json")
