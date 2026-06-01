
with source as (

    select * from {{ ref('fct_orders') }}

)

select
    date_trunc(created_at, month)   as month,
    count(order_id)                 as total_orders,
    sum(revenue)                    as total_revenue
from source
group by month
order by month