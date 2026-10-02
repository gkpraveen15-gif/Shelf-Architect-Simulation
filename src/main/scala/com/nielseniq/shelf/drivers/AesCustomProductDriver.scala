package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 3. CATEGORY_DEFINITION TASK
object AesCustomProductDriver {
  def run(config: RuntimeConfig)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: CATEGORY_DEFINITION via class com.nielsen.ap.seff.aso.customProduct.AesCustomProductDriver")
    println(s"[BUSINESS INTERPRETATION] Setting operational product classification boundaries. Segment profile targets top-level inventory group: ${config.productInfo.head.hierarchyTopLevel}")
    
    import spark.implicits._
    val categoryDF = Seq((config.execution_id, config.productInfo.head.hierarchyTopLevel, config.productInfo.head.brandChar, config.productInfo.head.manufacturerChar))
      .toDF("execution_id", "hierarchyTopLevel", "brandChar", "manufacturerChar")
    
    println(s"[AI EXECUTIVE SUMMARY] Analysis parameters set for core inventory category: ${config.productInfo.head.hierarchyTopLevel}. Competitive indexing active.")
    categoryDF
  }
}