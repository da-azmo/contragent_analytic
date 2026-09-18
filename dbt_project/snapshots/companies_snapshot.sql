{% snapshot companies_snapshot %}

{{ config(
    target_schema='snapshots',
    unique_key='id',
    strategy='check',
    check_cols=['hashdiff']
)}}

select
    id
    , "name"
    , inn
    , registration_date
    , region
    , industry
    , hashdiff
from {{ ref('stg_from_ods_to_dds_companies') }}

{% endsnapshot %}