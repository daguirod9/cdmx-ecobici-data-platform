from datetime import timedelta

from feast import Entity, FeatureView, Field
from feast.types import Float32, Int64, String
from feast.infra.offline_stores.contrib.duckdb_offline_store.duckdb_source import DuckDBSource

station = Entity(name="station_id", join_keys=["station_id"])

hourly_availability_source = DuckDBSource(
    name="hourly_availability_source",
    query="""
        SELECT
            station_id,
            status_timestamp as event_timestamp,
            bikes_available,
            docks_available,
            bike_availability_ratio
        FROM fact_station_availability
    """,
    timestamp_field="event_timestamp",
)

station_hourly_features = FeatureView(
    name="station_hourly_features",
    entities=[station],
    ttl=timedelta(days=30),
    schema=[
        Field(name="bikes_available", dtype=Int64),
        Field(name="docks_available", dtype=Int64),
        Field(name="bike_availability_ratio", dtype=Float32),
    ],
    source=hourly_availability_source,
)
