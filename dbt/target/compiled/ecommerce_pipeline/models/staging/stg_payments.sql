with source as (
    select * from `ecommerce-data-platform-497218`.`bronze`.`payments`
),

cleaned as (
    select
        payment_id,
        order_id,
        coalesce(
            nullif(trim(payment_method), ''),
            'unknown'
        )                                           as payment_method,
        lower(trim(status))                         as status,
        safe_cast(amount as numeric)                as amount,
        created_at,
        updated_at

    from source
    qualify row_number() over (
        partition by payment_id
        order by updated_at desc
    ) = 1
)

select * from cleaned