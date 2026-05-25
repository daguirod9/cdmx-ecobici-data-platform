select
    parent.last_updated,
    stations.station_id,
    stations.num_bikes_available,
    stations.num_docks_available,
    stations.is_installed,
    stations.is_renting,
    stations.is_returning
from ecobici_bronze.station_status_raw as parent
inner join ecobici_bronze.station_status_raw__stations as stations
    on parent._dlt_id = stations._dlt_parent_id
