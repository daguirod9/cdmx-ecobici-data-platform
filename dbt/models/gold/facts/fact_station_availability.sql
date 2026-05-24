select
    md5(station_id || cast(status_timestamp as varchar)) as availability_fact_id,
    station_id,
    cast(status_date as date) as date_key,
    cast(status_hour as int) as hour_key,
    status_timestamp,
    bikes_available,
    docks_available,
    (bikes_available + docks_available) as total_capacity,
    case when (bikes_available + docks_available) = 0 then 0
         else bikes_available * 1.0 / (bikes_available + docks_available)
    end as bike_availability_ratio
from {{ ref('silver_station_status') }}
where is_installed = 1
