--- DIM хранит свойства контракта, которые могут иметь историю

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    schema='dds',
    unique_key='dbt_scd_id',
    on_schema_change='fail'
)}}

WITH snapshot_data as
(
    SELECT
        id as contract_bk
        , company_id as company_bk
        , "status"
        , contract_date
        , dbt_valid_from as valid_from
        , COALESCE(dbt_valid_to, '2999-12-31'::timestamp) as valid_to
        , dbt_valid_to IS NULL as is_current
        , hashdiff
        , dbt_scd_id
    FROM {{ ref('contracts_snapshot') }}
),
dim_data as
(
    SELECT
        CASE WHEN d.dbt_scd_id IS NULL THEN NEXTVAL('dds.seq_contract_sk')::bigint ELSE d.contract_sk END as contract_sk
        , s.contract_bk
        , s.company_bk
        , s.status
        , case when d.contract_bk is null then s.contract_date::timestamp else s.valid_from end as valid_from
        , s.valid_to
        , s.is_current
        , s.hashdiff
        , s.dbt_scd_id as dbt_scd_id
    FROM snapshot_data s
    LEFT JOIN {{ this }} d ON s.dbt_scd_id = d.dbt_scd_id

    {% if is_incremental() %}

        WHERE d.dbt_scd_id IS NULL
        OR d.hashdiff <> s.hashdiff
        OR d.valid_to <> s.valid_to
        OR d.is_current <> s.is_current

    {% endif %}
)

SELECT
    contract_sk
    , contract_bk
    , company_bk
    , "status"
    , valid_from
    , valid_to
    , is_current
    , hashdiff
    , dbt_scd_id
FROM dim_data