import json
import pandas as pd

#read csv
df = pd.read_csv('./ogd/bovine_viral_diarrhea_eradication/Daten für Dashboard.csv')

# Remove extra quotes in column names
df.columns = df.columns.str.replace('"', "", regex=False)  # Cleans column names
df = df.applymap(lambda x: x.replace('"', "") if isinstance(x, str) else x)  # Cleans values

# Remove apostrophes as thousand separators in the N_FARMS column and convert to integer
df["N_FARMS"] = df["N_FARMS"].str.replace("'", "", regex=False).astype(int)

#change date to datetime and Count to int
df["TIMESTEP"] =  pd.to_datetime(df["TIMESTEP"], format="%d.%m.%Y")
df["N_FARMS"] = df["N_FARMS"].str.replace('[^0-9]', '', regex=True).astype(int)


# Function to correct large differences with color-specific thresholds
def correct_large_diffs(df):
    # Sort the DataFrame by index (in this case, the dates) to ensure chronological order
    df = df.sort_index()
    
    # Define the thresholds for each color
    thresholds = {
        'green': 1200,
        'orange': 1200,
        'red': 15
    }
    
    # Iterate over the rows of the DataFrame
    for idx, row in df.iterrows():
        color = row['BVD_AMPEL']
        threshold = thresholds.get(color, 1000)  # Default to 1000 if color is missing

        # Check if the index three rows earlier exists (last day with the same color)
        prev_idx = df.index.get_loc(idx) - 3
        if prev_idx >= 0:
            previous_valid_idx = df.index[prev_idx]

            # Calculate the difference with the last value for this color
            diff = row['N_FARMS'] - df.at[previous_valid_idx, 'N_FARMS']

            # Check if the difference exceeds the color-specific threshold
            if abs(diff) > threshold:
                print(f"Large diff at index {idx} for color {color}: {diff}")

                # Replace the current value with the value from the previous day for this color
                df.at[idx, 'N_FARMS'] = df.at[previous_valid_idx, 'N_FARMS']
                print(f"Updated index {idx} with value from index {previous_valid_idx}")

    return df

# Call the function to correct large differences
df = correct_large_diffs(df)


df.to_csv('./ogd/bovine_viral_diarrhea_eradication/OGD_bovine_viral_diarrhea_eradication.csv', index=False)

df_month = df.groupby(['BVD_AMPEL',pd.DatetimeIndex(df.TIMESTEP).to_period('M')]).nth(0)
df_month['diff'] = df_month.groupby('BVD_AMPEL')['N_FARMS'].diff().fillna(0).astype(int)

# Group by date to get the total count per day
df_month['total_per_day'] = df_month.groupby('TIMESTEP')['N_FARMS'].transform('sum')

# Calculate the percentage of each color for each day and round to 1 decimal place
df_month['percentage'] = ((df_month['N_FARMS'] / df_month['total_per_day']) * 100).round(1)
df_month.to_csv('./ogd/bovine_viral_diarrhea_eradication/Cubes/BVD_monthly_evolution.csv', index=False)

# Get the most recent date
most_recent_date = df_month['TIMESTEP'].max()
# Filter rows by the most recent date
df_recent = df_month[df_month['TIMESTEP'] == most_recent_date]
total = df_recent['N_FARMS'].sum()
df_recent['PERCENT'] = (df_recent['N_FARMS'] / total * 100).round(1)
df_recent_list = df_recent[['BVD_AMPEL', 'N_FARMS', 'PERCENT', 'diff']].to_dict(orient='records')


with open('./ogd/bovine_viral_diarrhea_eradication/CurrentData.json', 'w', encoding='utf-8') as f:
    json.dump(df_recent_list, f, ensure_ascii=False, indent=4)
