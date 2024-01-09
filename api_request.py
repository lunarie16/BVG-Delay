import requests
import json
import logging
import os
import time

main_url = 'https://v6.bvg.transport.rest/'
delay_url = 'stops/{station}/departures?linesOfStops=true&duration=15'



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_delay_for_station(station_id: int):
    url = delay_url.format(station=station_id)
    url_delay = f"{main_url}{url}"
    response = make_request(url_delay)
    # print(json.dumps(response, indent=4))
    return response


def get_all_transports_for_station(station_id: int, name: str):
    url_all_transports = f'{main_url}stops/{station_id}?linesOfStops=True'
    name = re.sub(r'[^\w]', '', name)
    path = f'data/stations/bvg_transports_for_{name}.json'
    if not os.path.exists(path):
        make_request(url_all_transports, f'stations/bvg_transports_for_{name}')
    else:
        print(f"skipped {name}")


def get_all_stations():
    """
    Get all stations from the BVG API
    Returns:
        list of all stations
    """
    url_all_stations = f'{main_url}stops/'
    make_request(url_all_stations, 'bvg_stations')


def make_request(url: str, file_name: str = None):
    logger.warning(f"requesting {url}")
    try:
        response = requests.get(url)
        while response.reason == 'Too Many Requests':
            logger.warning('too many requests')
            time.sleep(10)
            response = requests.get(url)
        json_resp = response.json()
        if not json_resp:
            logger.warning(f"empty response for {url}")
            return None
        if file_name:
            with open(f'data/{file_name}.json', 'w') as f:
                json.dump(json_resp, f, indent=4, ensure_ascii=False)
            f.close()
            print(f"saved to {file_name}")
        return json_resp
    except Exception as e:
        logger.warning(f"error for {url}")
        logger.error(e)
        return None


def return_all_stations(only_ids: bool = False):
    """
    Get all stations from the BVG API
    Returns:
        list of all stations
    """
    with open('data/stations/full.json', 'r') as f:
        json_resp = json.load(f)

    station_ids = []
    for station in json_resp:
        s = json_resp[station]
        station_id = s['id'].split(':')
        if len(station_id) == 3:
            station_ids.append((station_id[2], s['name']))

    if only_ids:
        return [station_id for station_id, name in station_ids]
    else:
        return station_ids


# if __name__ == "__main__":
#     stations = pd.read_csv('data/stations/BVG_complete.csv', index_col=0)
#     stations_id = stations.index
#     for station_id in tqdm(stations_id):
#         get_delay_for_station(station_id)
