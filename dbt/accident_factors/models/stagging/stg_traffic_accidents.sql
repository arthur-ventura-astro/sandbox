{{
    config(
        materialized='incremental'
    )
}}


with
    source as (
        select
            accidents::integer,
            traffic_fine_amount::numeric,
            traffic_density::numeric,
            traffic_lights::numeric,
            pavement_quality::numeric,
            urban_area::int,
            average_speed::numeric,
            rain_intensity::numeric,
            vehicle_count::numeric,
            time_of_day::numeric,
            updated_at::timestamp,
            id::integer
        from {{ source('raw_traffic', 'traffic_accidents') }}
        {% if is_incremental() %}
        where updated_at::timestamp > (select coalesce(max(updated_at::timestamp), '2025-01-01') from {{ this }})
        {% endif %}
    )

    select * from source
