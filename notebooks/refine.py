import pandas as pd
import numpy as np
import json
import argparse
import sys
from typing import Dict, Any

def is_admissible(value, admissible_keys):
    """Helper function for refine_data function (validate codes portion):
    Checks if a single value is inadmissible based on keys in data_dictionary.json.
    Returns true if the value is inadmissible (not defined in data_dictionary.json and not NaN)."""
    
    #Exclude values that are NaN (-8 "No code required (CE residents)" in FAMILY_TYPE)
    if pd.isna(value) or value == -8: #source: https://pandas.pydata.org/docs/reference/api/pandas.isna.html
        return False
        
    #Return value is NOT one of the expected keys
    return value not in admissible_keys
    

def refine_data(csv_filepath: str, json_filepath: str) -> pd.DataFrame:
    """Refines census data anticipating errors in the data which do not occur in this dataset, but may potentially happen:
    - handles file loading issues
    - removes duplicates
    - handles missing values
    - converts data types
    - checks values for selected columns"""

    
    #LOAD FILES
    #source: Lecture video "23 - Errors in Python"
    try:
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"CSV file not found at {csv_filepath}")
        sys.exit(1) #source: https://docs.python.org/3/library/sys.html
        
    try:
        with open(json_filepath, 'r') as f:
            data_dictionary = json.load(f)
    except FileNotFoundError:
        print(f"JSON file not found at {json_filepath}")
        sys.exit(1)
    except json.JSONDecodeError: #source: https://www.geeksforgeeks.org/python/json-parsing-errors-in-python/
        print(f"Unable to decode JSON dictionary file at {json_filepath}")
        sys.exit(1)
        
    print(f"Loaded {len(df)} rows")


    #REMOVE DUPLICATES
    initial_rows = len(df)
    df.drop_duplicates(inplace=True) #source: https://pandas.pydata.org/docs/reference/frame.html
    duplicates_removed = initial_rows - len(df)
    print(f"Removed {duplicates_removed} duplicate rows")

    
    #VALIDATE DATA TYPE AND HANDLE MISSING VALUES 
    #Define data type (numbers in df are either coded or identifiers like "SerialNum")
    dtype_mapping = {col: 'Int64' for col in df.columns} #https://pandas.pydata.org/docs/user_guide/integer_na.html
    
    #Convert data type
    for col, dtype in dtype_mapping.items():
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(dtype) #https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
        except Exception as e:
            print(f"Unable to convert column '{col}' to {dtype}: {e}")

    #Replace FAMILY_TYPE -8 "No code required (CE residents)" to numpy NaN
    #source: https://numpy.org/doc/stable/user/misc.html)
    #source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.replace.html
    df.replace(-8, np.nan, inplace=True)
    print("CE residents code '-8' replaced with NaN.")

    
    #VALIDATE CODES AND MAP TO STRINGS
    for col, mapping_dict in data_dictionary.items():
        if col in df.columns:
            #Exclude the code -8 "No code required (CE residents)"
            admissible_keys = [int(k) for k in mapping_dict.keys() if k != '-8']
            #Use is_admissible function to count the number of inadmissible values
            #source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html#
            inadmissible_count = df[col].apply(is_admissible, admissible_keys=admissible_keys).sum()
 
        if inadmissible_count > 0:
            print(f"'{col}' column contains {inadmissible_count} inadmissible values")
            
        #Create a new column with human-readable string labels
        new_col_name = f"{col}_LABEL"
        #Convert data_dictionary.json keys to integers to match with column data
        int_mapping_dict = {int(k): v for k, v in mapping_dict.items()}
        
        #Apply the mapping
        #Unmapped (NaN/inadmissible) values will remain NaN
        df[new_col_name] = df[col].map(int_mapping_dict)
        print(f"Created new column '{new_col_name}' using dictionary mapping")
        

    #IDENTIFY OUTLIERS AND ANOMALIES
    #Unusually high number of hours worked per week
    hours_col = 'HOURS_PER_WEEK_WORKED'
    if hours_col in df.columns:
        #Set to 100 or higher based on typical 40 hour work week, taking into account overtime
        outlier_limit = 100
        outlier_count = (df[hours_col] > outlier_limit).sum()
    
    if outlier_count > 0:
        print(f"Anomaly Check: {outlier_count} records in '{hours_col}' exceed {outlier_limit} hours per week")
        df.loc[df[hours_col] > outlier_limit, hours_col] = np.nan #source: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html
        print(f"Outliers in '{hours_col}' replaced with NaN")
 
    return df


def main():
    """Main function to handle command-line arguments and execute the refinement."""
    
    parser = argparse.ArgumentParser(description="Automated data refinement script for Census microdata.",
        formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('csv_file', type=str, help="Path to the CSV data file")
    parser.add_argument('json_file', type=str, help="Path to the data dictionary JSON file")
    
    #Parse arguments provided in terminal
    args = parser.parse_args()

    #Define output file path
    output_filepath = "refined_census_data.csv"
    
    #Execute refinement process
    refined_df = refine_data(args.csv_file, args.json_file)
    
    #Save refined data
    try:
        refined_df.to_csv(output_filepath, index=False)
        print(f"Refined data saved to {output_filepath}")
        print(f"Final data shape: {refined_df.shape}") #source: Lecture video "34 - Pandas"
    except Exception as e:
        print(f"Error: Could not save the refined data. {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()