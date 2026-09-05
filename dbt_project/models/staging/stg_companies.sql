{{ config(
    materialized='view'
)}}

SELECT
    id
    , "name"
    , inn
    , registration_date
    , region
    , industry

    , MD5(
        COALESCE("name", '') || '|' ||
        COALESCE(inn, '') || '|' ||
        COALESCE(registration_date::varchar, '') || '|' ||
        COALESCE(region, '') || '|' ||
        COALESCE(industry, ''))::varchar(64) AS hashdiff

FROM {{ source('ods', 'companies') }}
WHERE id IS NOT NULL