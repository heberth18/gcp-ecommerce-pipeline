select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select category
from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_products`
where category is null



      
    ) dbt_internal_test