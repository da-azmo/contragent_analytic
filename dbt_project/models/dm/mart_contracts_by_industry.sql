{{ config(
    schema='dm',
    materialized='incremental',
    incremental_strategy='delete+insert',
    on_schema_change='fail',
    unique_key='industry'
)}}


with source as (
    select
        industry::varchar(100)
        , count(f.contract_bk)::int as contracts_count
        , sum(amount)::numeric(20, 2) as total_amount
        , avg(amount)::numeric(20, 2) as avg_amount
        , min(amount)::numeric(10, 2) as min_amount
        , max(amount)::numeric(10, 2) as max_amount
    from {{ ref('fact_contracts') }} f
    left join {{ ref('dim_companies') }} comp on f.company_sk = comp.company_sk and comp.is_current = True
    group by industry
),
mart_data as (
    select
        s.industry
        , s.contracts_count
        , s.total_amount
        , s.avg_amount
        , s.min_amount
        , s.max_amount
    from source s
    left join {{ this }} t on s.industry = t.industry

    {% if is_incremental() %}
    where t.industry is null or s.contracts_count <> t.contracts_count
    {% endif %}
)
select
    industry
    , contracts_count
    , total_amount
    , avg_amount
    , min_amount
    , max_amount
from mart_data