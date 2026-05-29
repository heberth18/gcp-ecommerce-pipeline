
    
    

with dbt_test__target as (

  select inventory_id as unique_field
  from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_inventory`
  where inventory_id is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


