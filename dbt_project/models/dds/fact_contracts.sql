{{ config (
    materialized='incremental',
    incremental_strategy='append',
    unique_key='contract_version_id',
    schema='dds',
    on_schema_change='fail'
) }}

SELECT
    NEXTVAL('dds.seq_fact_contract_sk') as fact_contract_sk
    , dim_companies.company_sk::bigint as company_sk
    , dim_contracts.contract_sk::bigint as contract_sk
    , stg_contract.id::bigint as contract_bk
    , TO_CHAR(stg_contract.contract_date, 'YYYYMMDD')::bigint as date_sk
    , stg_contract.amount::numeric(10,2) as amount
    , stg_contract.contract_date::date as contract_date
    , dim_contracts.dbt_scd_id as contract_version_id
FROM {{ ref('stg_from_ods_to_dds_contracts') }} stg_contract

--- Найди ту версию контракта, интервал действия которой содержит дату контракта.
JOIN {{ ref('dim_contracts') }} dim_contracts ON 
(
    stg_contract.id = dim_contracts.contract_bk AND
    dim_contracts.valid_from <= stg_contract.contract_date::timestamp AND
    stg_contract.contract_date::timestamp < dim_contracts.valid_to
)

--- Найди ту версию компании, которая была актуальна на момент заключения контракта
JOIN {{ ref('dim_companies') }} dim_companies ON
(
    stg_contract.company_id = dim_companies.company_bk AND
    dim_companies.valid_from <= stg_contract.contract_date::timestamp AND
    stg_contract.contract_date::timestamp < dim_companies.valid_to
)

{% if is_incremental() %}

    WHERE NOT EXISTS
    (   
        SELECT 1
        FROM {{ this }} f
        WHERE f.contract_version_id = dim_contracts.dbt_scd_id
    )

{% endif %}