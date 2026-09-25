{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='company_bk',
    schema='dm',
    on_schema_change='fail'
)}}

with source as
(
    select
        comp.company_bk::bigint,
        comp."name"::varchar(258) as company_name,
        count(f.contract_bk)::int as contracts_count,
        sum(f.amount)::numeric(20, 2) as total_amount,
        avg(f.amount)::numeric(20, 2) as avg_amount,
        min(f.amount)::numeric(10, 2) as min_amount,
        max(f.amount)::numeric(10, 2) as max_amount,

        md5(
            comp."name" || '|' ||
            coalesce(sum(f.amount)::numeric(20, 2)::text, '0') || '|' ||
            coalesce(avg(f.amount)::numeric(20, 2)::text, '0') || '|' ||
            coalesce(min(f.amount)::numeric(10, 2)::text, '0') || '|' ||
            coalesce(max(f.amount)::numeric(10, 2)::text, '0')
        ) as hashdiff
    from {{ ref('fact_contracts') }} f
    left join {{ ref('dim_contracts') }} cont on cont.contract_sk = f.contract_sk and cont.is_current = True
    left join {{ ref('dim_companies') }} comp on comp.company_sk = f.company_sk and comp.is_current = True
    group by comp.company_bk, comp."name"
),
mart_data as (
    select
        s.company_bk,
        s.company_name,
        s.contracts_count,
        s.total_amount,
        s.avg_amount,
        s.min_amount,
        s.max_amount,
        s.hashdiff
    from source s
    left join {{ this }} t on s.company_bk = t.company_bk

    {% if is_incremental() %}
    where t.company_bk is null or t.hashdiff <> s.hashdiff
    {% endif %}
)

select
    company_bk,
    company_name,
    contracts_count,
    total_amount,
    avg_amount,
    min_amount,
    max_amount,
    hashdiff
from mart_data