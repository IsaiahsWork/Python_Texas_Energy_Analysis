import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Set Up
API_KEY = "V2DzV4qAHep4uWOEgoXvKRAUfi9TXodBhS0EUxhm"
API_URL = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data"

# Fetch_Params
params = {
    "api_key": API_KEY,
    "frequency": "monthly",
    "data[0]": ["generation"],
    "facets[location][]": "TX",
    "facets[sectorid][]": "99",
    "start": "2020-01",
    "sort[0][column]": "period",
    "sort[0][direction]": "asc",
    "offset": 0,
    "length": 5000
}

# Fetch
print("Fetching 5 Years Worth of Data...")
response = requests.get(API_URL, params=params)
data = response.json()

if 'response' in data:
    df = pd.DataFrame(data['response']['data'])
    
    # Convert text to number and date/time
    print("Converting Data...")
    df['generation'] = pd.to_numeric(df['generation'])
    df['period'] = pd.to_datetime(df['period'])
    
    # Select Fuel types
    print("Selecting Data...")
    important_fuels = ['NG', 'WND', 'COW', 'NUC', 'SUN']
    df_filtered = df[df['fueltypeid'].isin(important_fuels)] 
    
    # Map readable names
    name_map = {
        'NG': 'Natural Gas',
        'WND': 'Wind',
        'COW': 'Coal',
        'NUC': 'Nuclear',
        'SUN': 'Solar'
    }
    df_filtered['source'] = df_filtered['fueltypeid'].map(name_map)
    
    print("Pivoting Table...")
    # Pivot on 'source', not 'fueltypeid'
    df_pivot = df_filtered.pivot_table(
        values='generation',
        index='period',
        columns='source',  # This ensures columns are "Natural Gas", "Wind", etc.
        aggfunc='sum'
    )
    print(df_pivot.to_string())
    # Graph Data
    print("Graphing Data...")
    plt.figure(figsize=(14,7))
    
    #Color Keys to match the readable names
    colors = {
        'Natural Gas': '#F39C12', 
        'Wind': '#8E44AD', 
        'Coal': '#34495E', 
        'Solar': '#E74C3C',
        'Nuclear': '#2ECC71'
    }
    
    sns.lineplot(data=df_pivot, palette=colors, linewidth=3)
    
    # Add Marker
    uri_date = pd.to_datetime('2021-02-01')
    plt.axvline(uri_date, color='red', linestyle='--', alpha=0.5)
    plt.text(uri_date, df_pivot.max().max(), ' Winter Storm Uri', color='red', fontweight='bold', verticalalignment='top')
    
    # Formatting
    plt.title("The Texas Energy Transition (2020-2025)", fontsize=18, fontweight='bold', pad=20)
    plt.ylabel("Generation (Thousand MWh)", fontsize=12)
    plt.xlabel("")
    plt.grid(True, alpha=0.3)
    
    # Automatic Legend
    plt.legend(title="Source")

    # Clean Date Axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.tight_layout()

    plt.show()
else:
    print("Error", data)