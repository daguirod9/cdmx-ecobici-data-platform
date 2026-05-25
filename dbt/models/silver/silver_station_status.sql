select
    station_id::varchar as station_id,
    num_bikes_available::int as bikes_available,
    num_docks_available::int as docks_available,
    is_installed::int as is_installed,
    is_renting::int as is_renting,
    is_returning::int as is_returning,
    to_timestamp(last_updated) as status_timestamp,
    cast(to_timestamp(last_updated) as date) as status_date,
    extract(hour from to_timestamp(last_updated)) as status_hour,
    extract(dow from to_timestamp(last_updated)) as day_of_week_num
from {{ ref('bronze_station_status') }}
