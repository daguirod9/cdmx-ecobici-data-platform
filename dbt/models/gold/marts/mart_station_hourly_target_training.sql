select
    f.station_id,
    f.date_key,
    f.hour_key,
    t.day_of_week,
    t.day_name,
    h.demand_window,
    avg(f.bikes_available) as avg_bikes_available,
    avg(f.docks_available) as avg_docks_available,
    sum(f.demand_departures_proxy) as target_demand_proxy,
    sum(f.supply_arrivals_proxy) as target_supply_proxy,
    avg(f.net_demand_pressure_proxy) as avg_net_demand_pressure_proxy
from {{ ref('fact_station_hourly_target_proxy') }} f
join {{ ref('dim_time') }} t using (date_key)
join {{ ref('dim_hour') }} h using (hour_key)
group by 1,2,3,4,5,6
