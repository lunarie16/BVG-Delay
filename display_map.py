import plotly.express as px
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# get mapbox token
mapbox_token = os.getenv('MAPBOX_TOKEN')
px.set_mapbox_access_token(mapbox_token)


df = pd.read_csv('data/postproc-delays2023-11-29.csv')

# group data for every hour
df['planned_when_hr'] = pd.to_datetime(df['planned_when'])
df['planned_when_hr'] = df['planned_when_hr'].dt.floor('h').dt.strftime('%d.%m - %H')
df['planned_when_hr'] = df['planned_when_hr'].apply(lambda x: f"{x}h")

df['delay_minutes'] = df['delay_minutes'].apply(lambda x: round(abs(x), 2))

# drop ferry data
df = df[df['product'] != 'ferry']

df_map = df.groupby(['product', 'stop_name', 'planned_when_hr', 'latitude', 'longitude',
                    'line_name'])['delay_minutes'].sum().reset_index()

df['occupancy'] = df['occupancy'].fillna('low')

# sum up delay for each station for every hour
df = df.groupby(['product', 'stop_name', 'planned_when_hr', 'latitude', 'longitude',
                 'line_name', 'occupancy'])['delay_minutes'].sum().reset_index()


# drop all rows where delay is nan
# df = df.dropna(subset=['delay_minutes'])

product = {
    'bus': 'Bus',
    'tram': 'Tram',
    'subway': 'U-Bahn',
    'suburban': 'S-Bahn',
    'regional': 'Regional (Train)',
    'express': 'Express (Train)',
    'ferry': 'Ferry',
}

product_colors = {
    'Bus': '#6d597a',
    'Tram': '#d62828',
    'U-Bahn': '#003049',
    'S-Bahn': '#90a955',
    'Regional (Train)': '#fcbf49',
    'Express  (Train)': '#f77f00',
}

category_orders = {'product': ['Bus', 'Tram', 'U-Bahn', 'S-Bahn', 'Regional (Train)', 'Express (Train)']}


df['product'] = df['product'].map(product)
df_map['product'] = df_map['product'].map(product)

occupancy = {
    'high': 3,
    'medium': 2,
    'low': 1,
    'none': 1,
}
df['occupancy_num'] = df['occupancy'].map(occupancy)

# sum up occupancy for every line
df_occupancy = df.groupby(['line_name', 'product'])['occupancy_num'].mean().reset_index()

# get first and last date of data
first_date = df['planned_when_hr'].iloc[0]
last_date = df['planned_when_hr'].iloc[-1]

# sort by occupancy
df_occupancy = df_occupancy.sort_values(by=['occupancy_num'], ascending=False)


def create_map():
    # fill delay_minutes values that are nan with 0.1
    df_map['delay_minutes'] = df_map['delay_minutes'].fillna(0.1)

    # fill delay_minutes values that are 0 with 0.1
    df_map['delay_minutes'] = df_map['delay_minutes'].replace(0, 0.1)

    # normalize delay_minutes to max 50
    df_map['size'] = df_map['delay_minutes'].apply(lambda x: round(x / max(df_map['delay_minutes']) * 50, 2))


    # map showing delay for each station
    fig = px.scatter_mapbox(df_map, lat="latitude", lon="longitude", color="product",
                            size="size",
                            title='Total delay in minutes by hour, station and type of transport',
                            color_discrete_map=product_colors,
                            size_max=50, zoom=10,
                            category_orders=category_orders,
                            range_color=(0, 1000),
                            animation_frame="planned_when_hr", animation_group="stop_name",
                            hover_name="stop_name", hover_data=["product", "delay_minutes", "line_name"],
                            labels=dict(delay_minutes="Delay in minutes",
                                        product="Type of Transport",
                                        planned_when_hr='Planned when (hour)')
                            )

    fig.show()

def create_bar_delay():
    # TODO: norm delay by amount of


    df_bar = df.groupby(['product', 'planned_when_hr'])['delay_minutes'].sum().reset_index()
    df_bar['delay_hrs'] = df_bar['delay_minutes'].apply(lambda x: round(x / 60, 2))


    # bar chart showing total delay for each type of transport
    fig = px.bar(df_bar, x='delay_hrs', y='product', orientation='h',
                 color='product',
                 color_discrete_map=product_colors,
                 title='Total delay in hours by type of transport', animation_group='product',
                 animation_frame='planned_when_hr', hover_name="product",
                 category_orders=category_orders,
                 labels=dict(delay_hrs="Delay in hours", product="Type of Transport",
                             planned_when_hr='Planned when (hour)'),
                 text="delay_hrs",
                 range_x=[0, max(df_bar['delay_hrs'])+100],
                 hover_data=["product", "delay_minutes"])
    fig.show()


def create_bar_occupancy():
    fig = px.bar(df_occupancy[:20], y='occupancy_num', x='line_name',
                 text_auto='.3s',
                 color_discrete_map=product_colors,
                 labels=dict(occupancy_num="Occupancy (mean)",
                             line_name="Line",
                             product="Type of Transport"),
                 color='product',
                 category_orders=category_orders,
                 title=f'Mean occupancy (High = 3, Medium = 2, Low/None = 1) ({first_date} until {last_date})',
                 hover_name="line_name",
                 hover_data=["line_name", "product"])


    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3],
            ticktext=['Low/None', 'Medium', 'High']
        )
    )
    fig.show()


def create_bar_occupancy_no_bus():
    df_no_bus = df_occupancy[df_occupancy['product'] != 'Bus']
    fig = px.bar(df_no_bus[:20], y='occupancy_num', x='line_name',
                 text_auto='.3s',
                 color_discrete_map=product_colors,
                 labels=dict(occupancy_num="Occupancy (mean)",
                             line_name="Line",
                             product="Type of Transport"),
                 color='product',
                 category_orders=category_orders,
                 title=f'Mean occupancy (High = 3, Medium = 2, Low/None = 1) ({first_date} until {last_date})',
                 hover_name="line_name",
                 hover_data=["line_name", "product"])


    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3],
            ticktext=['Low/None', 'Medium', 'High']
        )
    )
    fig.show()


if __name__ == "__main__":
    create_map()
    # create_bar_delay()
    # create_bar_occupancy()
    # create_bar_occupancy_no_bus()
