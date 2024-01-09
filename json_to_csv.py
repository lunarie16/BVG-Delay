import json
import os
import pandas as pd

# get all files from data/stations
files = os.listdir('data/stations')

# filter for json files
files = [file for file in files if file.endswith('.json') and not file.startswith('full')]

# create empty dataframe
df = pd.DataFrame()

#create columns for dataframe
columns = ['id', 'name', 'type', 'latitude', 'longitude', 'products', 'suburban', 'subway', 'tram', 'bus', 'ferry', 'express', 'regional', 'line_id']

df_data = []
df_index = []
# iterate over files
for file in files:
    # read json file
    json_data = json.load(open(f'data/stations/{file}'))
    if 'Wedding' in file:
        print(json_data)

    if 'stops' in json_data:
        stops_data = json_data['stops']
    else:
        stops_data = [json_data]  # Treat the entire data as a single stop

        # Preparing data for DataFrame


    stop_info = {
        'stop_name': json_data.get('name', 'Unknown'),  # Using 'Unknown' if name is not present
        'latitude': json_data['location']['latitude'],
        'longitude': json_data['location']['longitude']
    }
    products = json_data.get('products', {})  # Using empty dict if products not present
    for product, available in products.items():
        stop_info[f'product_{product}'] = available

    df_data.append(stop_info)
    df_index.append(int(json_data['id']))

    for stop in stops_data:
        stop_info = {
            'stop_name': stop.get('name', 'Unknown'),  # Using 'Unknown' if name is not present
            'latitude': stop['location']['latitude'],
            'longitude': stop['location']['longitude']
        }
        df_index.append(int(stop['id']))
        if int(stop['id']) < 1000:
            print(stop['id'])
        # Flattening the products data
        products = stop.get('products', {})  # Using empty dict if products not present
        for product, available in products.items():
            stop_info[f'product_{product}'] = available
        df_data.append(stop_info)

    # Creating the DataFrame
stops_df = pd.DataFrame(data=df_data, index=df_index)
# print(stops_df.head())

# reset index
# stops_df = stops_df.reset_index(drop=True)
# # set index to id
# stops_df['stop_id'] = stops_df['stop_id'].astype(str)

# Check for duplicates in 'stop_id'
# if stops_df['stop_id'].duplicated().any():
#     print("Warning: Duplicate 'stop_id' values found.")

# stops_df.reset_index(drop=True, inplace=True)
# Set the index using an alternative method
# stops_df = stops_df.set_index('stop_id')

# save to csv
stops_df.to_csv('./data/stations/BVG_complete.csv')
