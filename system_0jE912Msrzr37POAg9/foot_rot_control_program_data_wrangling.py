import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import product
from ftplib import FTP

#########################
# Part 1) DOWNLOAD DATA
#########################

# GitHub secret
FTP_PASS = os.environ["FTP_PASS_DATEN_ALVPH"]

# Name der herunterzuladenden Datei
filename = "moderhinke-aktuelle-situation-input.csv"

# Pfad zum Skriptverzeichnis ermitteln
script_dir = os.path.dirname(os.path.abspath(__file__))
local_path = os.path.join(script_dir, filename)

# Verbindung zum FTP-Server
ftp = FTP('ftp.blv-data-ingest.ch')
ftp.login(user='Daten_ALVPH@blv-data-ingest.ch', passwd=FTP_PASS)

# In das richtige Verzeichnis wechseln
ftp.cwd("Moderhinke_2024_2025")

# Datei herunterladen
with open(local_path, "wb") as f:
    ftp.retrbinary(f"RETR {filename}", f.write)

ftp.quit()


#########################
# Part 2) WRANGLING
#########################

# Read the CSVs
df = pd.read_csv(local_path, sep=';')
canton_mapping_df  = pd.read_csv('/ogd/foot_rot_control_program/Cubes/canton_mapping.csv', sep=';')

# Convert StatusFrom from string to datetime
df['StatusFrom'] = pd.to_datetime(
    df['StatusFrom'],
        format='%Y-%m-%d',   # "2025-04-29"
            errors='coerce'      # ungültige Formate werden zu NaT
            )

# Filter out rows where StatusCode == 2 ("Nicht getestet")
df = df[df['StatusCode'] != 2]

# Filter out certain AnimalHusbandryTypes and rows where Canton == "Unknown"
exclude_types = [
    'HerdsmanHusbandry',
    'SummeringHusbandry',
    'CoOperationPastureHusbandry',
    'MigratoryHerd',
    'MedicalCenter',
    'SlaughterEnterprise',
    'MarketAuctionExhibition'
]

df = df[~df['AnimalHusbandryType'].isin(exclude_types) & (df['Canton'] != "Unknown")]

# Define weekly date range
start_date = pd.to_datetime("2025-04-29")
end_date = df['StatusFrom'].max()
weekly_dates = pd.date_range(start=start_date, end=end_date, freq='W-TUE')  # To match R's week start on Tuesday

# Create all combinations of TVD and weekly date
tvd_list = df['TVD'].unique()
all_combinations = pd.DataFrame(product(tvd_list, weekly_dates), columns=['TVD', 'week'])

# Merge with original data
merged = pd.merge(all_combinations, df, on='TVD', how='left')

# Filter rows where StatusFrom is <= week
filtered = merged[merged['StatusFrom'] <= merged['week']]

# For each TVD and week, keep the row with the latest StatusFrom date
idx = filtered.groupby(['TVD', 'week'])['StatusFrom'].transform('max') == filtered['StatusFrom']
weekly_status = filtered[idx].copy()

# Count distinct TVD per week
weekly_counts = weekly_status.groupby('week')['TVD'].nunique().reset_index(name='distinct_TVD_count')

# Group by week, StatusText, Canton and count distinct TVD
status_counts = (
    weekly_status
    .groupby(['week', 'StatusText', 'Canton'])['TVD']
    .nunique()
    .reset_index(name='farm_count')
)

# Pivot wider: StatusText values become columns
df_wide = status_counts.pivot_table(
    index=['Canton', 'week'],
    columns='StatusText',
    values='farm_count',
    fill_value=0
).reset_index()

# Rename columns for clarity if they exist
# Adjust these names based on your actual StatusText values
df_wide = df_wide.rename(columns={
    'Frei': 'farms_free_count',
    'gesperrt': 'farms_blocked_count'
})

# Make sure columns exist to avoid errors
for col in ['farms_free_count', 'farms_blocked_count']:
    if col not in df_wide.columns:
        df_wide[col] = 0

# Calculate total farms per (week, Canton)
df_wide['farms_total_count'] = df_wide['farms_free_count'] + df_wide['farms_blocked_count']

# Calculate proportions and round
df_wide['farms_blocked_proportion'] = np.round(
    df_wide['farms_blocked_count'] / df_wide['farms_total_count'] * 100
).fillna(0).astype(int)

df_wide['farms_free_proportion'] = np.round(
    df_wide['farms_free_count'] / df_wide['farms_total_count'] * 100
).fillna(0).astype(int)

# Pivot longer: convert selected columns into variable-value pairs
value_vars = [
    'farms_free_count',
    'farms_blocked_count',
    'farms_total_count',
    'farms_blocked_proportion',
    'farms_free_proportion'
]

df_long = df_wide.melt(
    id_vars=['Canton', 'week'],
    value_vars=value_vars,
    var_name='variable',
    value_name='value'
)

# Fill missing values with 0 (if any)
df_long['value'] = df_long['value'].fillna(0)

# Merge df_long with canton_mapping on Canton == canton_short
df_long = df_long.merge(
    canton_mapping_df,
    left_on='Canton',
    right_on='canton_short',
    how='left'
)

# Select and rename columns
df_long = df_long[['canton_id', 'week', 'variable', 'value']].rename(columns={'canton_id': 'canton'})

# Filter out canton 'LIE' and the proportion variables
filtered = df_long[
    (df_long['canton'] != 'LIE') &
    (~df_long['variable'].isin(['farms_blocked_proportion', 'farms_free_proportion']))
]

# Group by week and variable, summing the values
grouped = (
    filtered
    .groupby(['week', 'variable'], as_index=False)['value']
    .sum()
)

# Pivot wider to have variables as columns
pivoted = grouped.pivot(index='week', columns='variable', values='value').fillna(0)

# Calculate proportions and round
pivoted['farms_blocked_proportion'] = round(
    pivoted['farms_blocked_count'] / pivoted['farms_total_count'] * 100
).fillna(0).astype(int)

pivoted['farms_free_proportion'] = round(
    pivoted['farms_free_count'] / pivoted['farms_total_count'] * 100
).fillna(0).astype(int)

# Pivot longer again to match structure
df_totals = pivoted.reset_index().melt(
    id_vars='week',
    value_vars=[
        'farms_free_count',
        'farms_blocked_count',
        'farms_total_count',
        'farms_blocked_proportion',
        'farms_free_proportion'
    ],
    var_name='variable',
    value_name='value'
)

# Add canton column as "CHE"
df_totals['canton'] = 'CHE'

# Combine with original long DataFrame
df_final = pd.concat([df_long, df_totals], ignore_index=True)

# Sort by week
df_final = df_final.sort_values('week').reset_index(drop=True)

# Convert to integer
df_final['value'] = pd.to_numeric(df_final['value'], errors='coerce').fillna(0).astype(int)

# Output cleaned CSV
output_path = os.path.join("../ogd/foot_rot_control_program/Cubes/", "output.csv")

df_final.to_csv(output_path, sep=';', index=False)


#########################
# Part 3) CLEAN-UP
#########################

# 1. Datei löschen
if os.path.isfile(local_path):
    os.remove(local_path)
    print(f"Datei '{local_path}' gelöscht.")
else:
    print(f"Datei '{local_path}' existiert nicht.")