{{ config(
    schema='dm',
    on_schema_change='fail',
    materialized='incremental',
    unique_key='contract_version_id',
    incremental_strategy='delete+insert'
)}}

with source as (
    select
        cont.contract_bk::int
        , f.contract_version_id::text
        , comp."name"::varchar(258) as company_name
        , cont.valid_from::timestamp
        , cont.valid_to::timestamp
        , f.amount::numeric(10, 2) as new_amount
        , lag(f.amount) over (
            partition by f.contract_bk
            order by cont.valid_from
        )::numeric(10, 2) as old_amount
    from {{ ref('fact_contracts') }} f
    left join {{ ref('dim_contracts') }} cont on f.contract_sk = cont.contract_sk
    left join {{ ref('dim_companies') }} comp on f.company_sk = comp.company_sk
),
mart_data as (
    select
        s.contract_bk
        , s.contract_version_id
        , s.company_name
        , s.valid_from
        , s.valid_to
        , s.old_amount
        , s.new_amount
        , case when s.old_amount is null then s.new_amount else (s.new_amount - s.old_amount)::numeric(10, 2) end as delta_amount
    from source s
    left join {{ this }} t on s.contract_version_id = t.contract_version_id

    {% if is_incremental() %}
    where t.contract_version_id is null
    {% endif %}
)

select
    contract_bk
    , contract_version_id
    , company_name
    , valid_from
    , valid_to
    , old_amount
    , new_amount
    , delta_amount
from mart_data