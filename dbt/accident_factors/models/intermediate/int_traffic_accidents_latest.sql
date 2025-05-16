{{
    config(
        materialized='view'
    )
}}

with
    traffic_accidents_latest as (
        select s.* from {{ ref('stg_traffic_accidents') }} as s
        where s.updated_at >= (select coalesce(max(this.updated_at), '2025-01-01') from {{ ref('stg_traffic_accidents') }} as this)
    )

    select * from traffic_accidents_latest
