select distinct
    status_hour as hour_key,
    case when status_hour between 6 and 10 then 'morning_peak'
         when status_hour between 17 and 21 then 'evening_peak'
         else 'off_peak' end as demand_window
from {{ ref('silver_station_status') }}
