{{ config(
    materialized='view'
)}}

SELECT
    id::int
    , company_id::int
    , contract_date::date
    , amount::numeric(10,2)
    , "status"::text
    , hashdiff::text

FROM {{ source('ods', 'contracts') }}
WHERE id IS NOT NULL