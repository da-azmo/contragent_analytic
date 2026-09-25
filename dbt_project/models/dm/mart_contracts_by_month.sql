{{ config(
    materialized='incremental',
    unique_key=['year', 'month'],
    incremental_strategy='delete+insert',
    schema='dm',
    on_schema_change='fail'
)}}

with source as (
    select
        dat."year"::int
        , dat."month"::varchar(20)
        , count(contract_bk)::int as contracts_count
        , sum(amount)::numeric(20, 2) as total_amount
        , avg(amount)::numeric(20, 2) as avg_amount
        , min(amount)::numeric(10, 2) as min_amount
        , max(amount)::numeric(10, 2) as max_amount
    from {{ ref('fact_contracts') }} f
    left join {{ source('dds', 'dim_dates') }} dat on f.date_sk = dat.date_sk
    group by dat."year", dat."month"
),
mart_data as (
    select
        s."year"
        , s."month"
        , s.contracts_count
        , s.total_amount
        , s.avg_amount
        , s.min_amount
        , s.max_amount
    from source s
    left join {{ this }} t on t."year" = s."year" and t."month" = s."month"

    {% if is_incremental() %}

    where (t."year" is null and t."month" is null) or
        (s.contracts_count <> t.contracts_count)

    {% endif %}
)
select
    "year"
    , "month"
    , contracts_count
    , total_amount
    , avg_amount
    , min_amount
    , max_amount
from mart_data