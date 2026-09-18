--- «Как менялась запись в исходной системе?»

{{ config(
    materialized='view'
)}}

SELECT
    id::int
    , "name"::varchar(258)
    , inn::varchar(10)
    , registration_date::date
    , region::varchar(100)
    , industry::varchar(100)
    , hashdiff::text

FROM {{ source('ods', 'companies') }}
WHERE id IS NOT NULL