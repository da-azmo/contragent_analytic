{{ config(
    materialized='incremental',
    unique_key='contract_bk',
    incremental_strategy='delete+insert',
    schema='dm',
    on_schema_change='fail'
)}}

with source as (
    select
        fact.contract_bk
        , dim_comp.name
        , dim_cont.status
        , dim_comp.region
        , dim_comp.industry
        , fact.amount
        , fact.contract_date
        , MD5(
            dim_comp.name::text || 
            dim_cont.status::text || 
            coalesce(dim_comp.region::text, '<NULL>') || 
            coalesce(dim_comp.industry::text, '<NULL>') || 
            coalesce(fact.amount::text, '<NULL>') || 
            coalesce(fact.contract_date::text, '<NULL>')) as hashdiff
    from {{ ref('fact_contracts') }} fact
    left join {{ ref ('dim_contracts') }} dim_cont on fact.contract_bk = dim_cont.contract_bk and dim_cont.is_current is True
    left join {{ ref('dim_companies') }} dim_comp on dim_cont.company_bk = dim_comp.company_bk and dim_comp.is_current is True
),
mart_data as
(
    select
        s.contract_bk
        , s.name as company_name
        , s.status
        , s.region
        , s.industry
        , s.amount
        , s.contract_date
        , s.hashdiff
    from source as s
    left join {{ this }} t on t.contract_bk = s.contract_bk

    {% if is_incremental() %}
        WHERE t.contract_bk is null or t.hashdiff <> s.hashdiff
    {% endif %}
)

select
    contract_bk
    , company_name
    , "status"
    , region
    , industry
    , amount
    , contract_date
    , hashdiff
from mart_data