with
    rural_traffic as (
        select
            s.id as id,
            s.accidents as accidents,
            s.traffic_fine_amount as traffic_fine_amount,
            s.traffic_density as traffic_density,
            s.traffic_lights as traffic_lights,
            s.pavement_quality as pavement_quality,
            s.average_speed as average_speed,
            s.rain_intensity as rain_intensity,
            s.vehicle_count as vehicle_count,
            s.time_of_day as time_of_day
        from {{ ref('int_traffic_accidents_latest') }} as s where s.urban_area = 0
    )

    select * from rural_traffic
