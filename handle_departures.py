import pandas as pd
from api_request import get_delay_for_station
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def process_departures_data(station_id, departures):
    """
    Process the 'departures' data from the JSON file to create a DataFrame with delay, line, and station information.
    """
    departures_list = []
    realtimeDataUpdatedAt = departures.get('realtimeDataUpdatedAt', None)
    departures = departures.get('departures', [])
    for departure in departures:
        remarks = departure.get('remarks', {})
        remark_summary = None
        remark_start = None
        remark_end = None
        for remark in remarks:
            if departure.get('line', {}).get('name').lower() in remark.get('text', ' ').lower():
                remark_summary = remark.get('summary', remark.get('text', None))
                remark_start = remark.get('validFrom', None)
                remark_end = remark.get('validUntil', None)

        departure_info = {
            'stop_id': departure.get('stop', {}).get('id', station_id),
            'trip_id': departure.get('tripId', None),
            'when': departure.get('when', None),
            'planned_when': departure.get('plannedWhen', None),
            'stop_name': departure.get('stop', {}).get('name', None).replace(',', ''),
            'line_name': departure.get('line', {}).get('name', None),
            'delay_seconds': departure.get('delay', 0),  # Defaulting to 0 if no delay info
            'start_station': departure.get('stop', {}).get('name', '').replace(',', ''),  # Assuming the current stop is the start station
            'end_station': departure.get('destination', {}).get('name', '').replace(',', '') if 'destination' in departure else None,
            'end_station_id': departure.get('destination', {}).get('id', None) if 'destination' in departure else None,
            'product': departure.get('line', {}).get('product'),
            'occupancy': departure.get('occupancy', None),
            'remark_summary': remark_summary,
            'remark_start': remark_start,
            'remark_end': remark_end,
            'realtimeDataUpdatedAt': realtimeDataUpdatedAt
        }
        departures_list.append(departure_info)
    return departures_list


if __name__ == "__main__":
    current_time = datetime.now()
    end_time = datetime(2024, 1, 1, 0, 0, 0)
    columns = ['stop_id', 'trip_id', 'when', 'planned_when', 'stop_name', 'line_name', 'delay_seconds', 'start_station', 'end_station', 'end_station_id', 'product', 'occupancy', 'remark_summary', 'remark_start', 'remark_end', 'realtimeDataUpdatedAt']

    stations = pd.read_csv('/data/stations/BVG_complete.csv', index_col=0)
    stations_id = stations.index
    df_data = []
    with open(f'/data/delays/delays{current_time}.csv', 'a+') as file:
        logger.warning(f'Started processing departures.')
        while current_time < end_time:
            try:
                for station_id in stations_id:
                    departure = get_delay_for_station(station_id)
                    if departure is None:
                        departure = get_delay_for_station(station_id)
                        if departure is None:
                            continue
                    departure = process_departures_data(station_id, departure)
                    [file.write(','.join([str(x) for x in list(departure.values())]) + '\n') for departure in departure]
            except Exception as e:
                logger.error(e)
                continue
            current_time = datetime.now()
            logger.warning(f'Finished processing departures for {current_time}')



