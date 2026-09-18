--- materialized='incremental' - модель должна обновляться инкрементально — то есть при каждом запуске обрабатывать и добавлять в таблицу только новые или изменившиеся данные, а не пересчитывать всю таблицу целиком
--- incremental_strategy='merge' - «Если запись с таким id уже есть — обнови её. Если нет — вставь»

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='id',
    schema='ods',
    on_schema_change='fail'
)}}

SELECT
    id::int,
    company_id::int,
    contract_date::date,
    amount::numeric(10,2),
    "status"::text,
    hashdiff::text,
    loaded_at::timestamptz
FROM {{ source('staging', 'temp_contracts') }} stg

{% if is_incremental() %}
WHERE NOT EXISTS (
    SELECT 1
    FROM {{ this }} ods
    WHERE ods.id = stg.id AND ods.hashdiff = stg.hashdiff )
{% endif %}