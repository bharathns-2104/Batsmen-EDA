import requests
from bs4 import BeautifulSoup
import pandas as pd

# Set headers for the HTTP request
request_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Initialize a list to store rows
all_rows = []

# Loop through the pages (change the range according to the number of pages)
for i in range(1, 124):  # Adjust the range if necessary
    url = f"https://stats.espncricinfo.com/ci/engine/stats/index.html?class=6;filter=advanced;orderby=player;page={i};size=200;template=results;trophy=117;type=batting;view=innings"
    
    response = requests.get(url, headers=request_headers)
    print(f"Page {i} - Response OK: {response.ok}")
    
    # If response is successful
    if response.ok:
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        
        # Find all tables in the page
        tables = soup.find_all('table')
        
        # Check if the 3rd table exists
        if len(tables) >= 3:
            table_data = tables[2]  # Access the 3rd table (index 2)

            # Get table headers (rename the variable to avoid overwriting request headers)
            table_headers = [header.text.strip() for header in table_data.find_all('th')]

            # Get rows from the table
            for row in table_data.find_all('tr'):
                columns = row.find_all('td')
                if columns:
                    row_data = [col.text.strip() for col in columns]
                    all_rows.append(row_data)
        else:
            print(f"Page {i} does not have 3 tables")

# Create a DataFrame from the collected rows
if all_rows:
    df = pd.DataFrame(all_rows, columns=table_headers)

    # Save the DataFrame to a CSV file
    df.to_csv('Scraped_Dataset.csv', index=False)
    print("Data has been successfully scraped and saved to Scraped_Dataset.csv")
else:
    print("No data was scraped.")
