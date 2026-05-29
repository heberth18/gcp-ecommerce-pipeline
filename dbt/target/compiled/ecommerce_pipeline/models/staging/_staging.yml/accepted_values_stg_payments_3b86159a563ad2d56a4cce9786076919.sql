
    
    

with all_values as (

    select
        payment_method as value_field,
        count(*) as n_records

    from `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_payments`
    group by payment_method

)

select *
from all_values
where value_field not in (
    'credit_card','debit_card','paypal','bank_transfer','unknown'
)


