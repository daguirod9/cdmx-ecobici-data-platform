select distinct
    status_date as date_key,
    dayofweek(status_date) as day_of_week,
    dayname(status_date) as day_name,
    month(status_date) as month,
    year(status_date) as year
from {{ ref('silver_station_status') }}
