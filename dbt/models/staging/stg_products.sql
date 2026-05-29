with source as (
    select * from {{ source('bronze', 'products') }}
),

cleaned as (
    select
        product_id,
        trim(name)                                  as name,
        lower(trim(category))                       as category,
        price,
        is_active,
        created_at,
        updated_at

    from source
)

select * from cleaned