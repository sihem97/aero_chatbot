import pandas as pd
import os

print("Checking data file...")
data_path = os.path.join('data', 'bdd_ia.csv')

if os.path.exists(data_path):
    print(f"\nFound data file at: {data_path}")
    df = pd.read_csv(data_path, encoding='utf-8')
    
    print("\nDataset Summary:")
    print(f"Total rows: {len(df)}")
    print("\nColumns found:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nFirst 2 rows:")
    print(df.head(2).to_string())
else:
    print(f"\n❌ Data file not found at: {data_path}")