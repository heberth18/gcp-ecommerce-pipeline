select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select city
from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_customers`
where city is null



      
    ) dbt_internal_test