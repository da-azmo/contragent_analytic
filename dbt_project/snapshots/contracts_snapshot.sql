{% snapshot contracts_snapshot %}

{{ config(
    target_schema='snapshots',
    unique_key='id',
    strategy='check',
    check_cols=['hashdiff']
)}}

select
    id
    , company_id
    , contract_date
    , amount
    , "status"
    , hashdiff
from {{ ref('stg_from_ods_to_dds_contracts') }}

{% endsnapshot %}