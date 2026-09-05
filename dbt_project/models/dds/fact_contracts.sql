{{ config (
    materialized='incremental',
    unique_key='fact_contract_sk',
    on_schema_change='fail',
    alias='fact_contracts_test'
) }}

SELECT
    NEXTVAL('dds.seq_fact_contract_sk') as fact_contract_sk
    , dim_companies.company_sk as company_sk
    , dim_contracts.contract_sk as contract_sk
    , TO_CHAR(dim_contracts.valid_from, 'YYYYMMDD') as date_sk
    , stg_contract.amount as amount
    , dim_contracts.contract_date as contract_date
FROM {{ ref('stg_contracts') }} stg_contract

JOIN {{ ref('dim_contracts') }} dim_contracts ON stg_contract.id = dim_contracts.contract_bk AND dim_contracts.is_current = TRUE
JOIN {{ ref('dim_companies') }} dim_companies ON stg_contract.company_id = dim_companies.company_bk AND dim_companies.is_current = TRUE

{% if is_incremental() %}
WHERE stg_contract.contract_date > (SELECT MAX(contract_date) FROM {{ this }} )
{% endif %}