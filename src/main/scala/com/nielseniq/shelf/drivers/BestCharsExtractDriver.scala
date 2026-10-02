package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 5. CREATE_CATEGORY_SCOPE TASK
object BestCharsExtractDriver {
  def run(config: RuntimeConfig, marketUniverse: DataFrame)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: CREATE_CATEGORY_SCOPE via class com.nielsen.ap.seff.aso.charExtractAlgo.BestCharsExtractDriver")
    println(s"[BUSINESS INTERPRETATION] Scanning global items database catalog. Enforcing characteristic restrictions matching rule arrays where operational column field code equals ${config.productInfo.head.productFilter.head.rules.head.field}")
    
    import spark.implicits._
    // Simulating anomalies: unmapped categories, dirty nomenclature strings
    val itemCatalogDF = Seq(
      ("UPC_001", "HAIR CARE", "SHAMPOO", "LOREAL", "MAN_LOREAL", 1.20),
      ("UPC_002", "STYLING", "SPRAY", "GARNIER", "MAN_LOREAL", 0.95),
      ("UPC_003", "SKIN CARE", "LOTION", "OLAY", "MAN_P&G", 4.50), // Out of scope
      ("UPC_004", "HAIR CARE", "CONDITIONER", "PANTENE", "MAN_P&G", 1.10)
    ).toDF("upc_code", "CSTM_19639", "CSTM_19375", "CSTM_19501", "CSTM_19621", "unit_share_pct")
    
    val filterValues = config.productInfo.head.productFilter.head.rules.head.value
    val scopedItems = itemCatalogDF.filter(col("CSTM_19639").isin(filterValues: _*))
      .withColumn("execution_id", lit(config.execution_id))
    
    println(s"[AI EXECUTIVE SUMMARY] Active analytical taxonomy scope locked. Isolated ${scopedItems.count()} unique UPC codes matching target criteria: ${filterValues.mkString(", ")}.")
    scopedItems
  }
}