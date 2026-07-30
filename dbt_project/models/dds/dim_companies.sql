{{ config (
    materialized='incremental',
    schema='dds',
    unique_key='company_sk',
    on_schema_change='fail'
) }}

WITH source AS (
    SELECT
        id,
        "name",
        inn,
        registration_date,
        region,
        industry,
        loaded_at,
        hash_diff
    FROM {{ ref('stg_companies') }}
),
existing AS (
    SELECT
        company_sk
        , company_bk
        , "name"
        , region
        , industry
        , valid_from
        , valid_to
        , is_current
        , hash_diff
    FROM {{ this }}
    WHERE is_current = TRUE
)

SELECT
    NEXTVAL('dds.seq_company_sk')  AS company_sk
    , s.id as company_bk
    , s.name
    , s.region
    , s.industry
    , CURRENT_TIMESTAMP AS valid_from
    , '2999-12-31'::timestamp AS valid_to
    , TRUE AS is_current
    , s.hashdiff

FROM source s

{% if is_incremental() %}
WHERE NOT EXISTS (
    SELECT 1
    FROM existing e
    WHERE
        s.hashdiff = e.hashdiff
)
{% endif %}

UNION ALL

SELECT
    company_sk
    , company_bk
    , "name"
    , region
    , industry
    , valid_from
    , CURRENT_TIMESTAMP AS valid_to
    , FALSE AS is_current
    , hash_diff
FROM existing e

{% if is_incremental() %}

WHERE EXISTS (
    SELECT 1
    FROM source s
    WHERE
        s.id = e.company_bk AND
        s.hashdiff != e.hashdiff
)
{% endif %}