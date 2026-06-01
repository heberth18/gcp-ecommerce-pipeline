
with source as (

    select * from {{ ref('stg_customers') }}

)

select
    customer_id,
    email,
    first_name,
    last_name,
    country,
    city,
    registration_date
from source