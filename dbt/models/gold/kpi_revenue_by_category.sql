
with items as (

    select * from {{ ref('fct_order_items') }}

),

products as (

    select * from {{ ref('dim_products') }}

)

select
    p.category,
    sum(oi.subtotal)                as total_revenue,
    sum(oi.quantity)                as total_units_sold
from items oi
join products p using (product_id)
group by p.category
order by total_revenue desc