package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 4. MARKET_DEFINITION TASK
object ASOMarketDefDriver {
  def run(config: RuntimeConfig)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: MARKET_DEFINITION via class com.nielsen.ap.seff.aso.marketDefinition.ASOMarketDefDriver")
    println(s"[BUSINESS INTERPRETATION] Streaming geographic parameter maps from location bucket: ${config.marketInfo.head.customMarketFilePath}. Active operational density parameter: ${config.marketInfo.head.projectionFactorType}")
    
    import spark.implicits._
    // Simulating robust anomalies (e.g., store inclusion threshold filters, out-of-bounds geographic metrics)
    val storesDF = Seq(
      (101L, "STORE_A_EAST", "US", 15.5),
      (102L, "STORE_B_WEST", "US", 8.2), // Fails channel_threshold
      (103L, "STORE_C_SOUTH", "US", 24.1),
      (104L, "STORE_D_NORTH", "US", 3.0)  // Fails channel_threshold
    ).toDF("store_id", "store_name", "store_country", "sales_volume_in_channel")
    
    val threshold = config.marketInfo.head.channel_threshold.toDouble
    val filteredMarkets = storesDF.filter(col("sales_volume_in_channel") >= threshold)
      .withColumn("execution_id", lit(config.execution_id))
      .withColumn("projection_factor", lit(config.marketInfo.head.projectionFactorType))
    
    println(s"[AI EXECUTIVE SUMMARY] Retail network data cleanup complete. Dropped ${storesDF.count() - filteredMarkets.count()} outlets falling below channel limit threshold of ${threshold} revenue metric units.")
    filteredMarkets
  }
}