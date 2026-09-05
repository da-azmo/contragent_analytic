{{ config(
    materialized = 'incremental',
    unique_key = 'contract_sk',
    on_schema_change='fail'
) }}

WITH source AS (
    SELECT
        id
        , company_id
        , contract_date
        , amount
        , "status"
        , hashdiff
    FROM {{ ref('stg_contracts') }}
),
existing AS (
    SELECT
        contract_sk
        , contract_bk
        , company_bk
        , contract_date
        , "status"
        , valid_from
        , valid_to
        , is_current
        , hashdiff
    FROM {{ this }}
    WHERE is_current = TRUE
)

SELECT
    NEXTVAL('dds.seq_contract_sk') AS contract_sk
    , s.id as contract_bk
    , s.company_id as company_bk
    , s.contract_date as contract_date
    , s.status as "status"
    , CURRENT_TIMESTAMP::timestamp AS valid_from
    , '2999-12-31'::timestamp AS valid_to
    , TRUE AS is_current
    , hashdiff AS hashdiff
FROM source s

{% if is_incremental() %}
WHERE NOT EXISTS (
    SELECT 1
    FROM existing e
    WHERE e.contract_bk = s.id AND e.hashdiff = s.hashdiff
)
{% endif %}

UNION ALL

SELECT
    e.contract_sk
    , e.contract_bk
    , e.company_bk
    , e.contract_date
    , e.status
    , e.valid_from
    , CURRENT_TIMESTAMP::timestamp AS valid_to
    , FALSE AS is_current
    , e.hashdiff
FROM existing e

{% if is_incremental() %}
WHERE EXISTS (
    SELECT 1
    FROM source s
    WHERE e.contract_bk = s.id AND s.hashdiff != e.hashdiff
)
{% endif %}