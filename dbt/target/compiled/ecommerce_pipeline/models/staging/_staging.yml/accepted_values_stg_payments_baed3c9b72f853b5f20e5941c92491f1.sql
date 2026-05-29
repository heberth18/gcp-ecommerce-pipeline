
    
    

with all_values as (

    select
        status as value_field,
        count(*) as n_records

    from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_payments`
    group by status

)

select *
from all_values
where value_field not in (
    'pending','completed','failed','refunded'
)


