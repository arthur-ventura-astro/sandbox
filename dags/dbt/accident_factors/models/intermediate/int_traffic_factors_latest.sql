{{
    config(
        materialized='view'
    )
}}

with
    traffic_factors_latest as (
        select s.* from {{ ref('stg_traffic_factors') }} as s
        where s.ds::date >= (select coalesce(max(this.ds::date), '2025-01-01') from {{ ref('stg_traffic_factors') }} as this)
    )

    select * from traffic_factors_latest
