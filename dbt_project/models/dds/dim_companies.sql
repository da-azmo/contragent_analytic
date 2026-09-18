--- «Какие исторические версии сущности доступны аналитике и какие ключи использовать для связи с FACT?»

{{ config(
    schema='dds',
    materialized='incremental',
    incremental_strategy = 'merge',
    unique_key='dbt_scd_id',
    on_schema_change='fail'
)}}

with snapshot_data as
(
    select
        id
        , "name"
        , region
        , industry
        , registration_date
        , dbt_valid_from
        , COALESCE(dbt_valid_to, '2200-01-01'::timestamp) as valid_to
        , dbt_valid_to is null as is_current
        , hashdiff
        , dbt_scd_id
    from {{ ref('companies_snapshot')}}
),
dim_data as
(
    select
        case when d.dbt_scd_id is null then NEXTVAL('dds.seq_company_sk')::bigint else d.company_sk end as company_sk
        , s.id as company_bk
        , s.name as "name"
        , s.region as region
        , s.industry as industry
        , case when d.company_bk is null then s.registration_date::timestamp else s.dbt_valid_from end as valid_from
        , s.valid_to as valid_to
        , s.is_current as is_current
        , s.hashdiff as hashdiff
        , s.dbt_scd_id as dbt_scd_id
    from snapshot_data s
    left join {{ this }} d on d.dbt_scd_id = s.dbt_scd_id

    {% if is_incremental() %}
        WHERE d.dbt_scd_id is null
        OR s.hashdiff <> d.hashdiff
        OR s.valid_to <> d.valid_to
        OR s.is_current <> d.is_current
    {% endif %}
)

SELECT
    company_sk
    , company_bk
    , "name"
    , region
    , industry
    , valid_from
    , valid_to
    , is_current
    , hashdiff
    , dbt_scd_id
FROM dim_data