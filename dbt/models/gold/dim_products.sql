
with source as (

    select * from {{ ref('stg_products') }}

)

select
    product_id,
    name,
    category,
    price,
    is_active
from source