{{ config(
    materialized='view',
    schema='staging'
)}}

SELECT
    id
    , company_id
    , amount
    , "status"
    , loaded_at

    , MD5(
        COALESCE(company_id, '') || '|' ||
        COALESCE(amount, '') || '|' ||
        COALESCE("status", '') || '|' ||
    ) AS hashdiff

FROM {{ source('ods', 'contracts') }}
WHERE id IS NOT NULL