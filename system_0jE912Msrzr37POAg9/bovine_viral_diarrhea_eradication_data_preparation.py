import json
import pandas as pd

#read csv
df = pd.read_csv('./ogd/bovine_viral_diarrhea_eradication/BVD.csv')

#change date to datetime and Count to int
df["TIMESTEP"] =  pd.to_datetime(df["TIMESTEP"], format="%d.%m.%Y")
df["N_FARMS"] = df["N_FARMS"].str.replace('[^0-9]', '', regex=True).astype(int)


#function to correct large differences
def correct_large_diffs(df):
    # Sort the DataFrame by index (in this case, the dates) to ensure chronological order
    df = df.sort_index()

    # Iterate over the rows of the DataFrame
    for idx, row in df.iterrows():
        # Check if the index three rows earlier (last day with the same color) exists
        prev_idx = df.index.get_loc(idx) - 3
        if prev_idx >= 0:
            previous_valid_idx = df.index[prev_idx]

            # Calculate the difference with the last value for this color
            diff = row['N_FARMS'] - df.at[previous_valid_idx, 'N_FARMS']

            # Check if the difference exceeds 1000
            if abs(diff) > 1000:
                print(f"Large diff at index {idx}: {diff}")
                
                # Replace the current value with the value from last day for this color
                df.at[idx, 'N_FARMS'] = df.at[previous_valid_idx, 'N_FARMS']
                print(f"Updated index {idx} with value from index {previous_valid_idx}")

    return df

# Call the function to correct large differences
df = correct_large_diffs(df)


df.to_csv('./ogd/bovine_viral_diarrhea_eradication/OGD_bovine_viral_diarrhea_eradication.csv', index=False)

df_week = df.groupby(['BVD_AMPEL',pd.DatetimeIndex(df.TIMESTEP).to_period('W')]).nth(0)
df_week['diff'] = df_week.groupby('BVD_AMPEL')['N_FARMS'].diff().fillna(0).astype(int)

# Get the most recent date
most_recent_date = df_week['TIMESTEP'].max()
# Filter rows by the most recent date
df_recent = df_week[df_week['TIMESTEP'] == most_recent_date]
total = df_recent['N_FARMS'].sum()
df_recent['PERCENT'] = (df_recent['N_FARMS'] / total * 100).round(1)
df_recent_list = df_recent[['BVD_AMPEL', 'N_FARMS', 'PERCENT', 'diff']].to_dict(orient='records')


with open('./ogd/bovine_viral_diarrhea_eradication/CurrentData.json', 'w', encoding='utf-8') as f:
    json.dump(df_recent_list, f, ensure_ascii=False, indent=4)