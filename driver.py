from bs4 import BeautifulSoup

input_file = "data/raw/single.html"

def main():
    """Run the main function."""
    with open(input_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "lxml")
        
    table = soup.find("tr")
    cells = table.find_all("td")
    
    cards_data = []
    for cell in cells:
        cards_data.append(cell.text.strip())
        
    print(cards_data)
    
if __name__ == "__main__":
    main()