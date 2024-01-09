import pandas as pd
import re
import numpy as np
import os


pd.set_option('display.max_columns', None)

stations = pd.read_csv('data/stations/BVG_complete.csv').set_index('Unnamed: 0')
lat_long = stations[['latitude', 'longitude']]
columns = ['stop_id', 'trip_id', 'when', 'planned_when', 'stop_name', 'line_name', 'delay_seconds', 'start_station', 'end_station', 'end_station_id', 'product', 'occupancy', 'remark_summary', 'remark_start', 'remark_end', 'realtimeDataUpdatedAt']

data = open('delays2023-11-29.csv').readlines()
data = [re.split(r',(?!\s)', d) for d in data]
df = pd.DataFrame(data, columns=columns).set_index('trip_id')
df.replace(r'None', np.nan, regex=True, inplace=True)
df['realtimeDataUpdatedAt'] = df['realtimeDataUpdatedAt'].str.replace('\n', '').astype(float)
df['when'] = pd.to_datetime(df['when'])
df['planned_when'] = pd.to_datetime(df['planned_when'])
df['stop_id'] = df['stop_id'].astype(float)
df['stop_name'] = df['stop_name'].astype(str)
df['line_name'] = df['line_name'].astype(str)
df['start_station'] = df['start_station'].astype(str)
df['end_station'] = df['end_station'].astype(str)
df['end_station_id'] = df['end_station_id'].astype(float)
df['product'] = df['product'].astype(str)
df['occupancy'] = df['occupancy'].astype(str)
df['remark_summary'] = df['remark_summary'].astype(str)
df['remark_start'] = pd.to_datetime(df['remark_start'])
df['remark_end'] = pd.to_datetime(df['remark_end'])
df['delay_seconds'] = df['delay_seconds'].astype(float)


# calculate delay for those where its none
no_delay_mask = df['delay_seconds'].isna()
df.loc[no_delay_mask, 'delay_seconds'] = df.loc[no_delay_mask, 'when'] - df.loc[no_delay_mask, 'planned_when']
df.loc[no_delay_mask, 'delay_seconds'] = df.loc[no_delay_mask, 'delay_seconds'].apply(lambda x: x.total_seconds())

# set information if delay_seconds is calculated
df.loc[no_delay_mask, 'delay_calculated'] = True
df.loc[~no_delay_mask, 'delay_calculated'] = False

df['delay_minutes'] = df['delay_seconds'].apply(lambda x: x / 60)
df = df.join(lat_long, on='stop_id')

df.to_csv('data/postproc-delays2023-11-29.csv')

no_lat = df['latitude'].isna()
print(df[no_lat]['stop_name'].unique())



# sum up number of delay_seconds by product
df_delay = df.groupby('product')['delay_minutes'].sum()
df_mean = df.groupby('product')['delay_seconds'].mean()
# convert delay to hours
df_delay = df_delay.apply(lambda x: x / 60)

# sum up delay for each station
df_delay_station = df.groupby('stop_name')['delay_minutes'].sum()

# sum up delay for each line
df_delay_line = df.groupby('line_name')['delay_minutes'].sum()



# filter all 'express' and 'regional' products out
df = df[~df['product'].isin(['express', 'regional'])]



# group by values and keep only the last entry
df_grouped = df.groupby('trip_id', group_keys=True).last()

# count the occupancy by each line_name
df_occupancy = df.groupby('line_name')['occupancy'].value_counts()


df_grouped.sort_values(by=['delay_seconds'], inplace=True, ascending=False)



# df_grouped.to_csv('data_grouped.csv')
print(df_grouped[['stop_name', 'when', 'end_station', 'product', 'delay_seconds', 'delay_minutes']].head())
# print(df_grouped.head())
# print(df_delay[:10])
# df_grouped = df.groupby('trip_id', group_keys=True).apply(lambda x: x)
# print(df_grouped.head())