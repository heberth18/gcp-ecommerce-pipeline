with source as (
    select * from `ecommerce-data-platform-497218`.`bronze`.`orders`
),

cleaned as (
    select
        order_id,
        customer_id,
        lower(trim(status))                         as status,
        total_amount,
        created_at,
        updated_at

    from source
)

select * from cleaned