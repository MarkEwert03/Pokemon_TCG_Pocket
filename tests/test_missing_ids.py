import pandas as pd
import pytest
from collections import defaultdict

PACK_MAX_IDS = {
    "A1": "286",  # Gold Mewtwo
    "A1a": "086",  # Gold Mew
    "A2": "207",  # Gold Dialga
    "A2a": "096",  # Gold Arceus
    "A2b": "111",  # Gold Poke Ball
    "A3": "239",  # Gold Solgaleo
    "A3a": "103",  # Gold Nihilego
    "P-A": "073",  # Toucannon
}


def get_ids_from_csv(path: str = "data/full.csv") -> list[str]:
    """
    Returns set of missing ids (numbers) from full pokemon TCG dataset.

    Parameters
    ----------
        path : str
            The path to the data set. (Usually `data/full.csv`)

    Returns
    -------
        missing_ids : list[str]
            A list containing all missing pokemon card IDs (if any).
    """
    # Load CSV
    df = pd.read_csv(path)

    # Extract prefix and numeric part as strings
    df[["prefix", "id_str"]] = df["number"].str.extract(r"([A-Za-z0-9-]+) (\d{3})")

    # Define expected maximum ID (inclusive as string) per prefix
    # NOTE needs to be updated when new set gets released

    # Collect missing IDs
    missing_ids = []

    for prefix, max_str in PACK_MAX_IDS.items():
        max_int = int(max_str)
        expected = {f"{i:03d}" for i in range(1, max_int + 1)}  # from "001" to max_str
        actual = set(df.loc[df["prefix"] == prefix, "id_str"])
        missing = sorted(expected - actual)
        missing_ids.extend([f"{prefix} {i}" for i in missing])

    return missing_ids


# Group by prefix
missing_ids = get_ids_from_csv()
prefix_to_missing = defaultdict(list)
for card_id in missing_ids:
    prefix = card_id.split()[0]
    prefix_to_missing[prefix].append(card_id)

# Create full list of (prefix, [missing IDs]), including ones with 0 missing
parametrized_data = []
for prefix in sorted(PACK_MAX_IDS.keys()):
    missing = prefix_to_missing.get(prefix, [])
    parametrized_data.append((prefix, missing))


@pytest.mark.parametrize("prefix,missing_ids", parametrized_data)
def test_pack_has_no_missing_cards(prefix, missing_ids):
    assert not missing_ids, f"{len(missing_ids)} missing for {prefix}:\n" + "\n".join(missing_ids)
