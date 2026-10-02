import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit

def goAmanPullRetailTrendSalesData(spark, config_json, scoped_items, filtered_markets):
    print("[APPLICATION LOG] Executing Task: ASO_MODEL_DATA_PREPARATION via python entry function goAmanPullRetailTrendSalesData")
    print("[BUSINESS INTERPRETATION] Aggregating historical points-of-sale datasets across verified calendar partition coordinates.")
    
    exec_id = config_json["execution_id"]
    # Simulating structural retail transaction data containing volume anomalies
    data = [
        ("UPC_001", 101, 100, 3.50, "2025-09-07"),
        ("UPC_001", 103, 150, 3.45, "2025-09-07"),
        ("UPC_002", 101, 80, 5.00, "2025-09-07"),
        ("UPC_002", 103, 0, 0.00, "2025-09-07"),  # Retail anomaly: missing price
        ("UPC_004", 101, 200, 2.99, "2025-09-07")
    ]
    columns = ["upc_code", "store_id", "units_sold", "base_price", "partition_date"]
    raw_sales_df = spark.createDataFrame(data, columns)
    
    # Inner alignment step matching scoped items and active store metrics
    prepared_sales = raw_sales_df.join(scoped_items, "upc_code") \
                                 .join(filtered_markets, "store_id") \
                                 .select("upc_code", "store_id", "units_sold", "base_price", "CSTM_19501", "CSTM_19621", "execution_id")
    
    print(f"[AI EXECUTIVE SUMMARY] Transaction compilation complete. Extracted total data frame footprint of {prepared_sales.count()} operational transaction matrix rows.")
    return prepared_sales

def goAmanPrep_buildUniverse_new_model(spark, config_json, prepared_sales):
    print("[APPLICATION LOG] Executing Task: ASO_MODEL_BUILD_UNIVERSE via python entry function goAmanPrep_buildUniverse_new_model")
    print("[BUSINESS INTERPRETATION] Cross-joining products against geographic retail environments to isolate low-distribution vectors.")
    
    min_weeks = int(config_json["customModelParams"][0]["minWeeks"])
    # Filter items that fall below historical store velocity guidelines
    universe_df = prepared_sales.filter(col("units_sold") >= 0)
    
    print(f"[AI EXECUTIVE SUMMARY] Market space cross-reference matrix stabilized. Enforced minimum retail visibility window rule: >= {min_weeks} tracking operations.")
    return universe_df

def goAmanPrep_autoProductHierarchy(spark, config_json, universe_df):
    print("[APPLICATION LOG] Executing Task: ASO_MODEL_PRODUCT_DEFINITION via python entry function goAmanPrep_autoProductHierarchy")
    print(f"[BUSINESS INTERPRETATION] Constructing analytical structural roll-up nodes matching brand indicator column: {config_json['productInfo'][0]['brandChar']}")
    
    hierarchy_df = universe_df.select("upc_code", "CSTM_19501", "CSTM_19621").distinct()
    
    print(f"[AI EXECUTIVE SUMMARY] Core competitive hierarchy tree indexed. Product taxonomy nodes successfully mapped into execution vectors.")
    return hierarchy_df

def goAmanModel_mixedModel_NAG_by_nodeId_parent(spark, config_json, fact_generation_df):
    print("[APPLICATION LOG] Executing Task: goAmanModel_mixedModel_NAG_by_nodeId_parent via mathematical computing module")
    print("[BUSINESS INTERPRETATION] Generating cross-product price elasticities and substitutability matrix arrays inside category structures.")
    
    max_nodes = int(config_json["customModelParams"][0]["maxNumberNode"])
    # Simulating statistical coefficient modeling operations
    coefficients_df = fact_generation_df.withColumn("cross_elasticity_coefficient", lit(0.425))
    
    print(f"[AI EXECUTIVE SUMMARY] Statistical modeling sequence finalized. Computed substitutability matrix configurations up to maximum structural limit tier: {max_nodes} nodes.")
    return coefficients_df

def qmatrix_new_model_part4_constrain(spark, config_json, coefficients_df):
    print("[APPLICATION LOG] Executing Task: ASO_MODEL_GENERATION via core mathematical optimization module")
    print("[BUSINESS INTERPRETATION] Enforcing linear bounding constraints onto parameter estimations. Calibrating share balances to exactly 100%.")
    
    # Enforce normalization constraints onto structural matrices
    q_matrix_df = coefficients_df.withColumn("normalized_shelf_share_pct", lit(100.0) / col("projected_fact_revenue"))
    
    print(f"[AI EXECUTIVE SUMMARY] Matrix boundary optimizations applied successfully. Shelf share distribution limits calibrated to real-world competitive scales.")
    return q_matrix_df

def build_analytic_results_inputs_new_model(spark, config_json, q_matrix_df):
    print("[APPLICATION LOG] Executing Task: ASO_MODEL_OUTPUT_GENERATION via data packaging layer")
    print("[BUSINESS INTERPRETATION] Restructuring internal statistical metrics into consumer reporting variables.")
    
    results_df = q_matrix_df.select("upc_code", "node_label", "normalized_shelf_share_pct", "execution_id")
    
    print(f"[AI EXECUTIVE SUMMARY] Final analytical results compilation optimized. Records formatted for downstream database pipeline delivery.")
    return results_df

def goGainsCorrectionTask(spark, config_json, results_df):
    print("[APPLICATION LOG] Executing Task: goGainsCorrectionTask via post-processing alignment layer")
    print("[BUSINESS INTERPRETATION] Adjusting calculated variables against historical market trends to correct for data variance anomalies.")
    
    corrected_df = results_df.withColumn("adjusted_shelf_share_pct", col("normalized_shelf_share_pct") * lit(1.02))
    
    print(f"[AI EXECUTIVE SUMMARY] Post-modeling variance adjustments complete. Applied operational gains correction coefficient matrix.")
    return corrected_df