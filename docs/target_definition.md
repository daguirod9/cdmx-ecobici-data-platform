# Target Definition for Demand Forecasting (Proxy v1)

## Objective
Define a trainable target now, using currently available Ecobici station status snapshots.

## Grain
`station_id` + `status_timestamp` (later aggregated to station-hour in marts).

## Proxy formulas
Given two consecutive snapshots per station:

- `demand_departures_proxy = max(previous_bikes_available - bikes_available, 0)`
- `supply_arrivals_proxy = max(previous_docks_available - docks_available, 0)`
- `net_demand_pressure_proxy = demand_departures_proxy - supply_arrivals_proxy`

## Interpretation
- `demand_departures_proxy` approximates bike check-outs.
- `supply_arrivals_proxy` approximates bike returns pressure on docks.
- `net_demand_pressure_proxy > 0` indicates depletion pressure.

## Known limitations
- It is a proxy, not confirmed trips.
- Rebalancing operations may distort the signal.
- Sampling frequency impacts precision.

## Migration path to real trips
When trip-level data is available:
1. Replace proxy target with observed trips-started per station-hour.
2. Keep feature pipelines unchanged where possible.
3. Run shadow validation to compare proxy-vs-real model performance.
