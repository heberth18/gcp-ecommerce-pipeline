
with source as (

    select * from {{ ref('fct_orders') }}

)

select
    order_status,
    count(order_id)                 as total_orders
from source
group by order_status
order by total_orders desc