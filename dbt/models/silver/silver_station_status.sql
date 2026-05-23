select
    station:station_id::varchar as station_id,
    station:num_bikes_available::int as bikes_available,
    station:num_docks_available::int as docks_available,
    station:is_installed::int as is_installed,
    station:is_renting::int as is_renting,
    station:is_returning::int as is_returning,
    to_timestamp(last_updated) as status_timestamp,
    cast(to_timestamp(last_updated) as date) as status_date,
    extract(hour from to_timestamp(last_updated)) as status_hour,
    extract(dow from to_timestamp(last_updated)) as day_of_week_num
from {{ ref('bronze_station_status') }}
