import json
import pandas as pd
import utils

input_json_path = "data/raw_from_web.json"
flattend_csv_path = "data/flattened_pokemon.csv"
cleaned_csv_path = "data/cleaned_pokemon.csv"


def flatten_pokemon_data(input_json_path, list_key="moves"):
    # 1. Load the JSON data
    with open(input_json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Extract the main card list
    cards = raw_data.get("cardArraySchema", {}).get("cards", [])
    if not cards:
        print("No cards found in the JSON.")
        return

    # 2. Determine the maximum number of nested items (e.g., moves)
    # This ensures we create enough columns for the card with the MOST moves.
    max_items = 0
    nested_keys = set()

    for card in cards:
        nested_list = card.get(list_key, [])
        max_items = max(max_items, len(nested_list))
        # Identify all keys inside the nested objects (e.g., name, damage, etc.)
        for item in nested_list:
            if isinstance(item, dict):
                nested_keys.update(item.keys())

    # 3. Flatten the data
    flattened_list = []

    for card in cards:
        # Create a copy of the card excluding the nested list
        flat_card = {k: v for k, v in card.items() if k != list_key}

        # Get the actual moves for this card
        current_nested_list = card.get(list_key, [])

        # Loop through every possible slot up to the global maximum
        for i in range(max_items):
            slot_num = i + 1

            if i < len(current_nested_list):
                # Card has a move at this index
                move_data = current_nested_list[i]
                for key in nested_keys:
                    # Column name format: move1_name, move1_damage, etc.
                    flat_card[f"{list_key}{slot_num}_{key}"] = move_data.get(key, "")
            else:
                # Card doesn't have a move at this index; fill with empty strings
                for key in nested_keys:
                    flat_card[f"{list_key}{slot_num}_{key}"] = ""

        flattened_list.append(flat_card)

    print(f"Done! Processed {len(cards)} cards. Max {list_key} found: {max_items}")

    # Return the DataFrame
    df = pd.DataFrame(flattened_list)
    return df


def clean_csv(df):
    if df is None:
        df = pd.read_csv(flattend_csv_path)

    # Remove unnecessary columns
    columns_to_remove = [
        "owned",
        "trainer_type",
        "moves3_damage",
        "moves3_energy_cost",
        "moves3_name",
        "moves3_description",
    ]
    df = df.drop(columns=columns_to_remove, errors="ignore")

    # Rename columns
    renamed_columns = {
        "evolution_stage": "stage",
        "ability": "ability_name",
        "image_url": "image",
        "archive_url": "page",
        "moves1_damage": "move1_damage",
        "moves1_energy_cost": "move1_cost",
        "moves1_name": "move1_name",
        "moves1_description": "move1_description",
        "moves2_damage": "move2_damage",
        "moves2_energy_cost": "move2_cost",
        "moves2_name": "move2_name",
        "moves2_description": "move2_description",
    }
    df = df.rename(columns=renamed_columns)

    # Reorder columns
    desired_order = [
        "id",
        "name",
        "card_type",
        "pokemon_type",
        "hp",
        "ex",
        "stage",
        "rarity",
        "set",
        "subset",
        "ability_name",
        "move1_name",
        "move1_cost",
        "move1_damage",
        "move1_description",
        "move2_name",
        "move2_cost",
        "move2_damage",
        "move2_description",
        "image",
        "page",
    ]
    df = df[[col for col in desired_order if col in df.columns]]

    # Clean up the ex column
    def convert_ex(value):
        if value == "ex":
            return 2
        elif value == "Mega Evolution ex":
            return 3
        else:
            return 1

    df["ex"] = df["ex"].apply(convert_ex)
    # Update ex column based on card_type
    df.loc[(df["ex"] == 1) & (df["card_type"] != "Pokemon"), "ex"] = 0

    # Clean up move_cost columns by converting energy text to symbols
    def energy_text_to_symbols(text):
        if text:
            textlist = text.split(":") if ":" in text else text.split(";")
            return "".join([utils.parse_energy_cost(x.strip()) for x in textlist])
        else:
            return ""

    # Update move cost columns
    df["move1_cost"] = df["move1_cost"].apply(energy_text_to_symbols)
    df["move2_cost"] = df["move2_cost"].apply(energy_text_to_symbols)
    df.loc[df["card_type"] == "Trainer", "move1_cost"] = ""
    df.loc[df["card_type"] == "Trainer", "move2_cost"] = ""

    # Update stage column
    df.loc[df["card_type"] == "Trainer", "stage"] = ""

    # Update pokemon_type column
    df.loc[df["pokemon_type"] == "Tool", "pokemon_type"] = "Pokemon Tool"

    # Misc corrections
    df.loc[df["id"] == "A4 177", "hp"] = "60"

    # Return final cleaned df
    return df


if __name__ == "__main__":
    print("Starting json converstion!")
    df = flatten_pokemon_data(input_json_path)
    df.to_csv(flattend_csv_path, index=False, encoding="utf-8")
    print(f"Flattened {len(df)} rows!")

    df = clean_csv(df)
    df.to_csv(cleaned_csv_path, index=False, encoding="utf-8")
    print(f"Cleaned {len(df)} rows!")
