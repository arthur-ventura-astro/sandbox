with
    source as (
        select * from {{ source('raw_traffic', 'traffic_factors') }}
    )

    select * from source
