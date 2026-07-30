{{ config(
    materialized='view',
    schema='staging'
)}}

SELECT
    id
    , "name"
    , inn
    , registration_date
    , region
    , industry
    , loaded_at

    , MD5(
        COALESCE("name", '') || '|' ||
        COALESCE(inn, '') || '|' ||
        COALESCE(registration_date, '') || '|' ||
        COALESCE(region, '') || '|' ||
        COALESCE(industry, '') || '|' ||
    ) AS hashdiff

FROM {{ source('ods', 'companies') }}
WHERE id IS NOT NULL