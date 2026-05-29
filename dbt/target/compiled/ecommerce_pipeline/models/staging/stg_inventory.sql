with source as (
    select * from `ecommerce-data-platform-497218`.`bronze`.`inventory`
),

cleaned as (
    select
        inventory_id,
        product_id,
        stock_quantity,
        reorder_point,
        coalesce(
            last_restock_date,
            date '1900-01-01'
        )                                           as last_restock_date,
        created_at,
        updated_at

    from source
)

select * from cleaned