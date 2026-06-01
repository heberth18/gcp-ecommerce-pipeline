
with orders as (

    select * from {{ ref('fct_orders') }}

),

customers as (

    select * from {{ ref('dim_customers') }}

)

select
    c.country,
    count(o.order_id)               as total_orders,
    sum(o.revenue)                  as total_revenue
from orders o
join customers c using (customer_id)
group by c.country
order by total_revenue desc