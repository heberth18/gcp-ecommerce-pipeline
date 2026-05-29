select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select status
from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_orders`
where status is null



      
    ) dbt_internal_test