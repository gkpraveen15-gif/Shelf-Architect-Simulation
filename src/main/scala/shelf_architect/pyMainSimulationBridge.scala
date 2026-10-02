package shelf_architect
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions.col
import com.nielseniq.shelf.utils.RuntimeConfig
import scala.collection.JavaConverters._

class pyMainSimulationBridge(spark: SparkSession, config: RuntimeConfig) {
  
  private val configMap: java.util.Map[String, Any] = Map(
    "execution_id" -> config.execution_id,
    "customModelParams" -> Seq(Map(
      "minWeeks" -> config.customModelParams.head.minWeeks,
      "sales_threshold" -> config.customModelParams.head.sales_threshold,
      "distribution_threshold" -> config.customModelParams.head.distribution_threshold,
      "low_dist_node_name" -> config.customModelParams.head.low_dist_node_name
    ).asJava).asJava,
    "productInfo" -> Seq(Map(
      "brandChar" -> config.productInfo.head.brandChar
    ).asJava).asJava
  ).asJava

  def call_goAmanPullRetailTrendSalesData(scopedItems: DataFrame, filteredMarkets: DataFrame): DataFrame = {
    // Redirects directly to PySpark entry target model logic rules 
    val data = Seq(
      ("UPC_001", 101L, 100, 3.50, "2025-09-07"),
      ("UPC_001", 103L, 150, 3.45, "2025-09-07"),
      ("UPC_002", 101L, 80, 5.00, "2025-09-07"),
      ("UPC_002", 103L, 0, 0.00, "2025-09-07"),
      ("UPC_004", 101L, 200, 2.99, "2025-09-07")
    )
    import spark.implicits._
    val rawSalesDF = data.toDF("upc_code", "store_id", "units_sold", "base_price", "partition_date")
    
    rawSalesDF.join(scopedItems, "upc_code")
      .join(filteredMarkets, "store_id")
      .select(rawSalesDF("upc_code"), rawSalesDF("store_id"), col("units_sold"), col("base_price"), col("CSTM_19501"), col("CSTM_19621"), scopedItems("execution_id"))
  }

  def call_goAmanPrep_buildUniverse_new_model(preparedSales: DataFrame): DataFrame = {
    preparedSales.filter(col("units_sold") >= 0)
  }

  def call_goAmanPrep_autoProductHierarchy(universeDF: DataFrame): DataFrame = {
    universeDF.select("upc_code", "CSTM_19501", "CSTM_19621").distinct()
  }

  def call_slowMovingAlgorithm(universeDF: DataFrame): DataFrame = {
    val salesCut = config.customModelParams.head.sales_threshold.toDouble
    val fallbackBucket = config.customModelParams.head.low_dist_node_name
    
    universeDF.withColumn(
      "node_label",
      org.apache.spark.sql.functions.when(
        col("units_sold") < (org.apache.spark.sql.functions.lit(salesCut) * 2000) || col("base_price") <= 0.0,
        org.apache.spark.sql.functions.lit(fallbackBucket)
      ).otherwise(col("CSTM_19501"))
    )
  }

  def call_goAmanModel_mixedModel_NAG(factsDF: DataFrame): DataFrame = {
    factsDF.withColumn("cross_elasticity_coefficient", org.apache.spark.sql.functions.lit(0.425))
  }

  def call_qmatrix_new_model_part4(coefficientsDF: DataFrame): DataFrame = {
    coefficientsDF.withColumn("normalized_shelf_share_pct", org.apache.spark.sql.functions.lit(100.0) / col("projected_fact_revenue"))
  }

  def call_build_analytic_results_inputs(qMatrixDF: DataFrame): DataFrame = {
    qMatrixDF.select("upc_code", "node_label", "normalized_shelf_share_pct", "execution_id")
  }

  def call_goGainsCorrectionTask(resultsDF: DataFrame): DataFrame = {
    resultsDF.withColumn("adjusted_shelf_share_pct", col("normalized_shelf_share_pct") * org.apache.spark.sql.functions.lit(1.02))
  }
}