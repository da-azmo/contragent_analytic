{{ config(
    materialized='view'
)}}

SELECT
    id
    , company_id
    , amount
    , "status"

    , MD5(
        COALESCE(company_id::varchar, '') || '|' ||
        COALESCE(amount::varchar, '') || '|' ||
        COALESCE("status", ''))::varchar(64) AS hashdiff

FROM {{ source('ods', 'contracts') }}
WHERE id IS NOT NULL