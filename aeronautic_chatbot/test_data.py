import pandas as pd
import os

def test_data():
    try:
        # Print current directory
        print("Current directory:", os.getcwd())
        
        # Check if data file exists
        data_path = os.path.join('data', 'bdd_ia.csv')
        print("\nLooking for file at:", data_path)
        print("File exists:", os.path.exists(data_path))
        
        # Try to read the file
        print("\nTrying to read the file...")
        df = pd.read_csv(data_path, encoding='utf-8')
        
        # Print information about the dataset
        print("\nDataset Info:")
        print(df.info())
        
        print("\nFirst few rows:")
        print(df.head())
        
        print("\nColumns:", df.columns.tolist())
        
        return True
        
    except Exception as e:
        print("\n❌ Error testing data:")
        print(str(e))
        return False

if __name__ == "__main__":
    test_data()