with base as (
    select
        station_id,
        status_timestamp,
        cast(status_date as date) as date_key,
        cast(status_hour as int) as hour_key,
        bikes_available,
        docks_available,
        lag(bikes_available) over (
            partition by station_id
            order by status_timestamp
        ) as prev_bikes_available,
        lag(docks_available) over (
            partition by station_id
            order by status_timestamp
        ) as prev_docks_available
    from {{ ref('silver_station_status') }}
    where is_installed = 1 and is_renting = 1 and is_returning = 1
),
proxy as (
    select
        md5(station_id || cast(status_timestamp as varchar)) as target_proxy_fact_id,
        station_id,
        date_key,
        hour_key,
        status_timestamp,
        bikes_available,
        docks_available,
        coalesce(prev_bikes_available, bikes_available) as prev_bikes_available,
        coalesce(prev_docks_available, docks_available) as prev_docks_available,
        greatest(coalesce(prev_bikes_available, bikes_available) - bikes_available, 0) as demand_departures_proxy,
        greatest(coalesce(prev_docks_available, docks_available) - docks_available, 0) as supply_arrivals_proxy
    from base
)
select
    *,
    demand_departures_proxy - supply_arrivals_proxy as net_demand_pressure_proxy
from proxy
