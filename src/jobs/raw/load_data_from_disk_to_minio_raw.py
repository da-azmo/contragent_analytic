def get_load_data_from_disk_to_minio_raw(data_from_disk: dict):
    for table_name, target_df in data_from_disk.items():
        target = target_df.get('target')
        df = target_df.get('df')

        df.write \
            .format("parquet") \
            .mode("append") \
            .save(target)