select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select last_restock_date
from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_inventory`
where last_restock_date is null



      
    ) dbt_internal_test