

  create or replace view `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_customers`
  OPTIONS()
  as with source as (
    select * from `ecommerce-data-platform-497218`.`bronze`.`customers`
),

cleaned as (
    select
        customer_id,
        lower(trim(email))                          as email,
        initcap(trim(first_name))                   as first_name,
        initcap(trim(last_name))                    as last_name,
        country,
        initcap(trim(city))                         as city,
        registration_date,
        created_at,
        updated_at

    from source
)

select * from cleaned;

