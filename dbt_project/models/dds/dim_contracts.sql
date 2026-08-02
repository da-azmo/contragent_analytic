{{ config(
    materialized = 'incremental',
    unique_key = 'contract_sk',
    on_schema_change='fail'
) }}

WITH source AS (
    SELECT
        NEXTVAL('dds.seq_contract_sk') AS contract_sk
        , id AS contract_bk
        , company_id AS company_bk
        , "status" AS "status"
        , CURRENT_TIMESTAMP::timestamp AS valid_from
        , '2999-12-31'::timestamp AS valid_to
        , TRUE AS is_current
        , hashdiff AS hashdiff
    FROM {{ ref('stg_contracts') }}
),
existing AS (
    SELECT
        contract_sk
        , contract_bk
        , company_bk
        , "status"
        , valid_from
        , valid_to
        , is_current
        , hashdiff
    FROM {{ this }}
)

SELECT
    s.contract_sk
    , s.contract_bk
    , s.company_bk
    , s.status
    , s.valid_from
    , s.valid_to
    , s.is_current
    , s.hashdiff
FROM source s

{% if is_incremental() %}
WHERE NOT EXISTS (
    SELECT 1
    FROM existing e
    WHERE e.hashdiff = s.hashdiff
)
{% endif %}

UNION ALL

SELECT
    e.contract_sk
    , e.contract_bk
    , e.company_bk
    , e.status
    , e.valid_from
    , CURRENT_TIMESTAMP::timestamp AS valid_to
    , FALSE AS is_current
    , e.hashdiff
FROM existing e

{% if is_incremental() %}
WHERE NOT EXISTS (
    SELECT 1
    FROM source s
    WHERE s.hashdiff != e.hashdiff
)
{% endif %}