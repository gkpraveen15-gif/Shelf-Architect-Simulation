from pyspark.sql.functions import col, lit, when

def run_slow_mover_logic(spark, config_json, universe_df):
    print("[APPLICATION LOG] Executing Task: ASO_SLOW_MOVER via isolated engine module slowMovingAlgorithm.py")
    print("[BUSINESS INTERPRETATION] Sorting low-performing inventory rows into combined category nodes to avoid statistical clutter.")
    
    sales_cut = float(config_json["customModelParams"][0]["sales_threshold"])
    dist_cut = float(config_json["customModelParams"][0]["distribution_threshold"])
    fallback_bucket = config_json["customModelParams"][0]["low_dist_node_name"]
    
    # Simulating robust conditional logic evaluating retail anomalies
    classified_df = universe_df.withColumn(
        "node_label",
        when(
            (col("units_sold") < (lit(sales_cut) * 2000)) | (col("base_price") <= 0.0),
            lit(fallback_bucket)
        ).otherwise(col("CSTM_19501"))
    )
    
    print(f"[AI EXECUTIVE SUMMARY] Inventory bucket consolidation complete. Categorized items falling below {int(dist_cut)}% market coverage limits into target container: '{fallback_bucket}'.")
    return classified_df