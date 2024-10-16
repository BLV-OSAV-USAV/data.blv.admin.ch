#Extract data to create different vizualisation


import pandas as pd
import numpy as np
from datetime import date

def count_gefahr(timeFilter, bereichName, lg):
    """
    Count occurrences of 'gefahr' and related data.

    Parameters:
    - timeFilter (str): Time filter ('all', 'week', 'month', 'year').
    - bereichName (str): Bereich name filter ('all' or specific name).
    - lg (str): Language for treiber bezeichnung ('de', 'fr', 'it', 'en').

    Returns:
    - CSV files with counts and related data.
    """
    # Load CSV files
    meldungXgefahr = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_gefahr.csv', sep='#', quotechar='`')
    gefahr = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_gefahr.csv', sep='#', quotechar='`')
    meldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung.csv', sep='#', quotechar='`')
    bereich = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_bereich.csv', sep='#', quotechar='`')
    bereichXmeldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_bereich.csv', sep='#', quotechar='`')
    treiber = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_treiber.csv', sep='#', quotechar='`')
    treiberXmeldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_treiber.csv', sep='#', quotechar='`')

    # Apply time filter
    if timeFilter != 'all':
        meldung['erfDate'] = pd.to_datetime(meldung['erf_date']).dt.date
        today = date.today()
        
        if timeFilter == 'week':
            start = (today - pd.DateOffset(weeks=1)).date()
        elif timeFilter == 'month':
            start = (today - pd.DateOffset(months=1)).date()
        elif timeFilter == 'year':
            start = (today - pd.DateOffset(years=1)).date()
        
        meldung = meldung[meldung['erfDate'] >= start]
        meldung_time_ids = meldung['id']
        meldungXgefahr = meldungXgefahr[meldungXgefahr['meldung_id'].isin(meldung_time_ids)]
    else:
        meldung_ids = meldung['id']
        meldungXgefahr = meldungXgefahr[meldungXgefahr['meldung_id'].isin(meldung_ids)]

    # Apply Bereich filter
    if bereichName != 'all':
        selected_bereich_id = bereich.loc[bereich['bezeichnung_de'] == bereichName, 'id'].values[0]
        meldung_bereich_ids = bereichXmeldung.loc[bereichXmeldung['bereich_id'] == selected_bereich_id, 'meldung_id'].values
        meldungXgefahr = meldungXgefahr[meldungXgefahr['meldung_id'].isin(meldung_bereich_ids)]

    # Group meldung_ids by gefahr_id
    meldung_ids_list = meldungXgefahr.groupby('gefahr_id')['meldung_id'].apply(list).reset_index()
    meldung_ids_list.columns = ['id', 'meldung_ids']

    # Count occurrences of gefahr_id
    gefahr_counts = meldungXgefahr['gefahr_id'].value_counts().reset_index()
    gefahr_counts.columns = ['id', 'count']

    # Calculate mean 'sterne' values per gefahr_id
    merged_df = pd.merge(meldungXgefahr, meldung[['id', 'sterne']], left_on='meldung_id', right_on='id', how='left')
    mean_sterne = merged_df.groupby('gefahr_id')['sterne'].mean().reset_index()
    mean_sterne.columns = ['id', 'mean_sterne']
    mean_sterne['mean_sterne'] = mean_sterne['mean_sterne'].round(2)

    # Merge results with existing DataFrame
    gefahr_counts = pd.merge(gefahr_counts, gefahr[['id', 'bezeichnung_de', 'bezeichnung_fr', 'bezeichnung_it', 'bezeichnung_en']], on='id', how='left')
    gefahr_counts = pd.merge(gefahr_counts, mean_sterne, on='id', how='left')
    gefahr_counts = pd.merge(gefahr_counts, meldung_ids_list, on='id', how='left')

    # Save the result to a CSV file
    if bereichName == 'Betrug / Täuschung':
        bereichName = 'BetrugTauschung'
    gefahr_counts.to_csv(f'./ogd/early_detection_for_food_safety/base/{bereichName}/gefahr_counts_{timeFilter}.csv', index=False)

    # Merge and count treiber_id occurrences
    merged_df_treiber = pd.merge(meldungXgefahr, treiberXmeldung, on='meldung_id')
    treiber_mapping = treiber.set_index('id')['bezeichnung_' + lg].to_dict()
    result_df_gefahr = merged_df_treiber.groupby(['gefahr_id', 'treiber_id']).size().unstack(fill_value=0)
    result_df_gefahr = result_df_gefahr.reset_index()

    # Rename columns using mapped values from treiber
    if not result_df_gefahr.empty:
        result_df_gefahr.columns = ['gefahr_id'] + [treiber_mapping.get(col, col) for col in result_df_gefahr.columns[1:]]
    else: 
        result_df_gefahr = pd.DataFrame(columns=['gefahr_id'] + list(treiber_mapping.values()))

    # Save the result to a CSV file
    result_df_gefahr.to_csv(f'./ogd/early_detection_for_food_safety/treiber/{bereichName}/gefahr_treiber_counts_{lg}_{timeFilter}.csv', index=False)


def count_matrix(timeFilter, bereichName, lg):
    """
    Count occurrences of 'matrix' and related data.

    Parameters:
    - timeFilter (str): Time filter ('all', 'week', 'month', 'year').
    - bereichName (str): Bereich name filter ('all' or specific name).
    - lg (str): Language for treiber bezeichnung ('de', 'fr', 'it', 'en').

    Returns:
    - CSV files with counts and related data.
    """
    # Load CSV files
    meldungXmatrix = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_matrix.csv', sep='#', quotechar='`')
    matrix = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_matrix.csv', sep='#', quotechar='`')
    meldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung.csv', sep='#', quotechar='`')
    bereich = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_bereich.csv', sep='#', quotechar='`')
    bereichXmeldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_bereich.csv', sep='#', quotechar='`')
    treiber = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_treiber.csv', sep='#', quotechar='`')
    treiberXmeldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_treiber.csv', sep='#', quotechar='`')

    # Apply time filter
    if timeFilter != 'all':
        meldung['erfDate'] = pd.to_datetime(meldung['erf_date']).dt.date
        today = pd.to_datetime('2023-11-28')
        
        if timeFilter == 'week':
            start = (today - pd.DateOffset(weeks=1)).date()
        elif timeFilter == 'month':
            start = (today - pd.DateOffset(months=1)).date()
        elif timeFilter == 'year':
            start = (today - pd.DateOffset(years=1)).date()
        
        meldung = meldung[meldung['erfDate'] >= start]
        meldung_time_ids = meldung['id']
        meldungXmatrix = meldungXmatrix[meldungXmatrix['meldung_id'].isin(meldung_time_ids)]
    else:
        meldung_ids = meldung['id']
        meldungXmatrix = meldungXmatrix[meldungXmatrix['meldung_id'].isin(meldung_ids)]

    # Apply Bereich filter
    if bereichName != 'all':
        selected_bereich_id = bereich.loc[bereich['bezeichnung_de'] == bereichName, 'id'].values[0]
        meldung_bereich_ids = bereichXmeldung.loc[bereichXmeldung['bereich_id'] == selected_bereich_id, 'meldung_id'].values
        meldungXmatrix = meldungXmatrix[meldungXmatrix['meldung_id'].isin(meldung_bereich_ids)]

    # Group meldung_ids by matrix_id
    meldung_ids_list = meldungXmatrix.groupby('matrix_id')['meldung_id'].apply(list).reset_index()
    meldung_ids_list.columns = ['id', 'meldung_ids']

    # Count occurrences of matrix_id
    matrix_counts = meldungXmatrix['matrix_id'].value_counts().reset_index()
    matrix_counts.columns = ['id', 'count']

    # Calculate mean 'sterne' values per matrix_id
    merged_df = pd.merge(meldungXmatrix, meldung[['id', 'sterne']], left_on='meldung_id', right_on='id', how='left')
    mean_sterne = merged_df.groupby('matrix_id')['sterne'].mean().reset_index()
    mean_sterne.columns = ['id', 'mean_sterne']
    mean_sterne['mean_sterne'] = mean_sterne['mean_sterne'].round(2)

    # Merge results with existing DataFrame
    matrix_counts = pd.merge(matrix_counts, matrix[['id', 'bezeichnung_de', 'bezeichnung_fr', 'bezeichnung_it', 'bezeichnung_en']], on='id', how='left')
    matrix_counts = pd.merge(matrix_counts, mean_sterne, on='id', how='left')
    matrix_counts = pd.merge(matrix_counts, meldung_ids_list, on='id', how='left')

    # Save the result to a CSV file
    if bereichName == 'Betrug / Täuschung':
        bereichName = 'BetrugTauschung'
    matrix_counts.to_csv(f'./ogd/early_detection_for_food_safety/base/{bereichName}/matrix_counts_{timeFilter}.csv', index=False)

    # Merge and count treiber_id occurrences
    merged_df_treiber = pd.merge(meldungXmatrix, treiberXmeldung, on='meldung_id')
    treiber_mapping = treiber.set_index('id')['bezeichnung_' + lg].to_dict()
    result_df_matrix = merged_df_treiber.groupby(['matrix_id', 'treiber_id']).size().unstack(fill_value=0)
    result_df_matrix = result_df_matrix.reset_index()

    # Rename columns using mapped values from treiber
    if not result_df_matrix.empty:
        result_df_matrix.columns = ['matrix_id'] + [treiber_mapping.get(col, col) for col in result_df_matrix.columns[1:]]
    else: 
        result_df_matrix = pd.DataFrame(columns=['matrix_id'] + list(treiber_mapping.values()))

    # Save the result to a CSV file
    result_df_matrix.to_csv(f'./ogd/early_detection_for_food_safety/treiber/{bereichName}/matrix_treiber_counts_{lg}_{timeFilter}.csv', index=False)

def count_steckbrief(timeFilter, bereichName, lg):
    """
    Count occurrences of 'steckbrief' and related data.

    Parameters:
    - timeFilter (str): Time filter ('all', 'week', 'month', 'year').
    - bereichName (str): Bereich name filter ('all' or specific name).
    - lg (str): Language for treiber bezeichnung ('de', 'fr', 'it', 'en').

    Returns:
    - CSV files with counts and related data.
    """
    # Load CSV files
    meldungXsteckbrief = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_steckbrief.csv', sep='#', quotechar='`')
    steckbrief = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_steckbrief.csv', sep='#', quotechar='`')
    meldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung.csv', sep='#', quotechar='`')
    bereich = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_bereich.csv', sep='#', quotechar='`')
    bereichXmeldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_bereich.csv', sep='#', quotechar='`')
    treiber = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_treiber.csv', sep='#', quotechar='`')
    treiberXmeldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_treiber.csv', sep='#', quotechar='`')
    log = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_log.csv', sep='#', quotechar='`')

    # Apply time filter
    if timeFilter != 'all':
        meldung['erfDate'] = pd.to_datetime(meldung['erf_date']).dt.date
        today = pd.to_datetime('2023-11-28')

        if timeFilter == 'week':
            start = (today - pd.DateOffset(weeks=1)).date()
        elif timeFilter == 'month':
            start = (today - pd.DateOffset(months=1)).date()
        elif timeFilter == 'year':
            start = (today - pd.DateOffset(years=1)).date()

        meldung = meldung[meldung['erfDate'] >= start]
        meldung_time_ids = meldung['id']
        meldungXsteckbrief = meldungXsteckbrief[meldungXsteckbrief['meldung_id'].isin(meldung_time_ids)]
    else:
        meldung_ids = meldung['id']
        meldungXsteckbrief = meldungXsteckbrief[meldungXsteckbrief['meldung_id'].isin(meldung_ids)]

    # Apply Bereich filter
    if bereichName != 'all':
        selected_bereich_id = bereich.loc[bereich['bezeichnung_de'] == bereichName, 'id'].values[0]
        meldung_bereich_ids = bereichXmeldung.loc[bereichXmeldung['bereich_id'] == selected_bereich_id, 'meldung_id'].values
        meldungXsteckbrief = meldungXsteckbrief[meldungXsteckbrief['meldung_id'].isin(meldung_bereich_ids)]

    # Group meldung_ids by steckbrief_id
    meldung_ids_list = meldungXsteckbrief.groupby('steckbrief_id')['meldung_id'].apply(list).reset_index()
    meldung_ids_list.columns = ['id', 'meldung_ids']

    # Count occurrences of steckbrief_id
    steckbrief_counts = meldungXsteckbrief['steckbrief_id'].value_counts().reset_index()
    steckbrief_counts.columns = ['id', 'count']

    # Count the number of mutations per steckbrief
    steckbrief_mut = log['parent_code'].value_counts().reset_index()
    steckbrief_mut.columns = ['code', 'count_mut']

    # Calculate mean 'sterne' values per steckbrief_id
    merged_df = pd.merge(meldungXsteckbrief, meldung[['id', 'sterne']], left_on='meldung_id', right_on='id', how='left')
    mean_sterne = merged_df.groupby('steckbrief_id')['sterne'].mean().reset_index()
    mean_sterne.columns = ['id', 'mean_sterne']
    mean_sterne['mean_sterne'] = mean_sterne['mean_sterne'].round(2)

    # Merge results with existing DataFrame
    steckbrief_counts = pd.merge(steckbrief_counts, steckbrief[['id', 'code', 'titel', 'kurzinfo', 'signal', 'erf_date', 'mut_date']], on='id', how='left')
    steckbrief_counts = pd.merge(steckbrief_counts, mean_sterne, on='id', how='left')
    steckbrief_counts = pd.merge(steckbrief_counts, steckbrief_mut, on='code', how='left')
    steckbrief_counts = pd.merge(steckbrief_counts, meldung_ids_list, on='id', how='left')

    # Replace empty strings with NaN in the 'titel' column
    steckbrief_counts['titel'].replace('', pd.NA, inplace=True)

    # Drop rows with NaN in the 'titel' column
    steckbrief_counts.dropna(subset=['titel'], inplace=True)

    # Save the result to a CSV file
    if bereichName == 'Betrug / Täuschung':
        bereichName = 'BetrugTauschung'
    steckbrief_counts.to_csv(f'./ogd/early_detection_for_food_safety/base/{bereichName}/steckbrief_counts_{timeFilter}.csv', index=False)

    # Merge and count treiber_id occurrences
    merged_df_treiber = pd.merge(meldungXsteckbrief, treiberXmeldung, on='meldung_id')
    treiber_mapping = treiber.set_index('id')['bezeichnung_' + lg].to_dict()
    result_df_steckbrief = merged_df_treiber.groupby(['steckbrief_id', 'treiber_id']).size().unstack(fill_value=0)
    result_df_steckbrief = result_df_steckbrief.reset_index()

    # Rename columns using mapped values from treiber
    if not result_df_steckbrief.empty:
        result_df_steckbrief.columns = ['steckbrief_id'] + [treiber_mapping.get(col, col) for col in result_df_steckbrief.columns[1:]]
    else: 
        # If result_df_steckbrief is empty, create an empty DataFrame with columns from treiber
        result_df_steckbrief = pd.DataFrame(columns=['steckbrief_id'] + list(treiber_mapping.values()))

    # Save the result to a CSV file
    result_df_steckbrief.to_csv(f'./ogd/early_detection_for_food_safety/treiber/{bereichName}/steckbrief_treiber_counts_{lg}_{timeFilter}.csv', index=False)


def list_meldung_pro_Gefahr(id):
    # Charger les fichiers CSV
    meldungXgefahr = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung_ad_gefahr.csv', sep='#', quotechar='`')
    meldung = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_meldung.csv', sep='#', quotechar='`')

    meldung_ids = list(meldungXgefahr.meldung_id[meldungXgefahr['gefahr_id'] == id])

    meldungs = meldung[meldung['id'].isin(meldung_ids)]


# Read the Bereich CSV file
bereich_csv = pd.read_csv('./ogd/early_detection_for_food_safety/early_detection_for_food_safety_ad_bereich.csv', sep='#', quotechar='`')

# Get unique values of Bereich names and add 'all' as an option
bereich_list = bereich_csv.bezeichnung_de.unique()
bereich_list = np.append(bereich_list, 'all')

# Loop through each Bereich and language
for bereich in bereich_list:
    for lg in ['de','fr','it','en']:
        # Count occurrences of gefahr
        count_gefahr('year', bereich, lg)
        count_gefahr('month', bereich, lg)
        count_gefahr('week', bereich, lg)
        count_gefahr('all', bereich, lg)

        # Count occurrences of matrix
        count_matrix('year', bereich, lg)
        count_matrix('month', bereich, lg)
        count_matrix('week', bereich, lg)
        count_matrix('all', bereich, lg) 

        # Count occurrences of steckbrief
        count_steckbrief('year', bereich, lg)
        count_steckbrief('month', bereich, lg)
        count_steckbrief('week', bereich, lg)
        count_steckbrief('all', bereich, lg) 