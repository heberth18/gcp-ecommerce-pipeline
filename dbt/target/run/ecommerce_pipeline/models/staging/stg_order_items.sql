

  create or replace view `ecommerce-data-platform-497218`.`ecommerce_pipeline_staging`.`stg_order_items`
  OPTIONS()
  as with source as (
    select * from `ecommerce-data-platform-497218`.`bronze`.`order_items`
),

cleaned as (
    select
        order_item_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        subtotal,
        created_at,
        updated_at

    from source
    qualify row_number() over (
        partition by order_item_id
        order by created_at desc, execution_date desc
    ) = 1
)

select * from cleaned;

