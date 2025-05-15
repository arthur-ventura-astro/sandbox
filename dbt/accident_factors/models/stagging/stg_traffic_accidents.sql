{{
    config(
        materialized='incremental'
    )
}}


with
    source as (
        select * from {{ source('raw_traffic', 'traffic_accidents') }}
        {% if is_incremental() %}
        where ds > (select coalesce(max(ds),'2025-01-01') from {{ this }} )
        {% endif %}
    )

    select * from source
