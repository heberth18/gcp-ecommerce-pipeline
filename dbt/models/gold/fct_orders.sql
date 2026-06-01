
with orders as (

    select * from {{ ref('stg_orders') }}

),

payments as (

    select * from {{ ref('stg_payments') }}
    where status = 'completed'

)

select
    o.order_id,
    o.customer_id,
    o.status        as order_status,
    o.created_at,

    p.payment_method,
    p.status        as payment_status,
    p.amount as revenue

from orders o
left join payments p using (order_id)