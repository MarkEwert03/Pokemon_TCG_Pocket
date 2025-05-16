# Pokemon_TCG_Pocket

A small Python utility to parse HTML tables containing [Pokémon TCG (Trading Card Game) card data](https://game8.co/games/Pokemon-TCG-Pocket/archives/482685) and export them into a structured CSV format.

---

## 🚀 Features

- Parses `<table>` elements with card data from raw HTML files
- Extracts card attributes such as number, name, type, HP, image URL, rarity, and more
- Outputs the data to a well-formatted CSV file
- Supports multiple rows (multiple cards) per HTML file
- Uses `pathlib` for robust, cross-platform file handling
- Designed for easy modular extension

---

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MarkEwert03/Pokemon_TCG_Pocket
   cd Pokemon_TCG_Pocket
   ```

2. (Optional but recommended) Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate # On Windows use: .venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install beautifulsoup4 lxml
   ```

---

## 📥 Input Format
Place HTML files containing the TCG card tables in the `data/raw/` directory.

Each file should contain a table with the class "a-table" and follow the structure of Pokémon TCG tables on game8.co.

---

## 🧾 Output Format
A CSV file with the same base name as the input HTML is written to `data/processed/`.

Columns include:
- number
- name
- image
- rarity
- pack_name
- type
- HP
- stage
- pack_points

---

## 🧪 How to Run
From the project root directory:
   `python run.py`


