select
    last_updated,
    unnest(stations) as station
from ecobici_bronze.station_status_raw
