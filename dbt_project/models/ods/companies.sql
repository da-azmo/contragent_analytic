{{ config(
    materialized='incremental',
    unique_key='id',
    schema='ods',
    incremental_strategy='merge',
    on_schema_change='fail'
)}}

SELECT
    id::int,
    "name"::varchar(255),
    inn::varchar(10),
    registration_date::date,
    region::varchar(100),
    industry::varchar(100),
    hashdiff::text,
    loaded_at::timestamptz
FROM {{ source('staging', 'temp_companies') }} stg

{% if is_incremental() %}
WHERE NOT EXISTS (
    SELECT 1
    FROM {{ this }} ods
    WHERE ods.id = stg.id AND ods.hashdiff = stg.hashdiff )
{% endif %}