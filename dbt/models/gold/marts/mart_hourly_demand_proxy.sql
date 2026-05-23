select
    f.date_key,
    f.hour_key,
    t.day_name,
    h.demand_window,
    count(distinct f.station_id) as active_station_count,
    avg(f.bike_availability_ratio) as avg_bike_availability_ratio
from {{ ref('fact_station_availability') }} f
join {{ ref('dim_time') }} t using (date_key)
join {{ ref('dim_hour') }} h using (hour_key)
group by 1,2,3,4
