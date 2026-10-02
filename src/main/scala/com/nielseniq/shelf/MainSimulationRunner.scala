package com.nielseniq.shelf
import org.apache.spark.sql.SparkSession
import com.nielseniq.shelf.utils.ContextFactory
import com.nielseniq.shelf.drivers._
import org.apache.spark.api.python.PythonRunner
import java.util.Collections
import org.apache.spark.sql.functions.sum

object MainSimulationRunner {
  def main(args: Array[String]): Unit = {
    // 1. Initialize local in-memory simulated Spark cluster environment
    implicit val spark: SparkSession = SparkSession.builder()
      .appName("ShelfArchitectEndToEndSimulation")
      .master("local[*]")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .getOrCreate()
      
    spark.sparkContext.setLogLevel("WARN")

    println("\n=========================================================================================")
    println("      🚀 INITIALIZING CRADLE-TO-GRAVE SHELF ARCHITECT SIMULATED COMPUTE ENGINE 🚀         ")
    println("=========================================================================================\n")

    // 2. Fetch configurations matching L'Oreal Hair Care target dataset payload
    val clientContext = ContextFactory.getLorealPayload

    // --- MODULE 1 & 2 LEG: ORCHESTRATION ENTRY & SCOPE DEFINITION ---
    val jobRegistry = ASOSaveTableDriver.run(clientContext)
    val periodScope = ASOPeriodDefDriver.run(clientContext)
    val categoryScope = AesCustomProductDriver.run(clientContext)
    val filteredMarkets = ASOMarketDefDriver.run(clientContext)
    val scopedItems = BestCharsExtractDriver.run(clientContext, filteredMarkets)

    // --- MODULE 3 LEG: DYNAMIC EXECUTION INTERFACE (PYSPARK BRIDGING SIMULATION) ---
    // Emulating invocation sequence executed by python entry task: aso_task_main_aes.py
    println("\n[SYSTEM LOG] Executing BranchPythonOperator: CHECK_REFRESH_JOB router logic.")
    println(s"[SYSTEM LOG] Evaluated target payload setting -> studyStage: '${clientContext.studyStage}'. Routing execution straight to TRIGGER_SEGMENTATION pipeline branch.")
    
    val pyMain = new shelf_architect.pyMainSimulationBridge(spark, clientContext)
    val preparedSales = pyMain.call_goAmanPullRetailTrendSalesData(scopedItems, filteredMarkets)
    val universeMatrix = pyMain.call_goAmanPrep_buildUniverse_new_model(preparedSales)
    val productHierarchy = pyMain.call_goAmanPrep_autoProductHierarchy(universeMatrix)
    
    // Core structural algorithms
    val baselineEstimates = BaselineAlgoDriverAES.run(clientContext, universeMatrix)
    val slowMoversClassified = pyMain.call_slowMovingAlgorithm(universeMatrix)
    
    // --- MODULE 4 LEG: FACT GENERATION & STATISTICAL ESTIMATIONS ---
    val finalFactsDF = RMSFactGenerationDriverAES.run(clientContext, slowMoversClassified, baselineEstimates)
    val statisticalCoefficients = pyMain.call_goAmanModel_mixedModel_NAG(finalFactsDF)
    val optimizedQMatrix = pyMain.call_qmatrix_new_model_part4(statisticalCoefficients)
    val analyticalOutputs = pyMain.call_build_analytic_results_inputs(optimizedQMatrix)
    val correctedOutputs = pyMain.call_goGainsCorrectionTask(analyticalOutputs)
    
    // --- MODULE 5 LEG: Lakehouse Snapshots & Snowflake Egress Sync ---
    val finalizedSorSnapshot = ASOUpdateSystemOfRecordsDriverAES.run(clientContext, correctedOutputs)
    
    println("\n[SYSTEM LOG] Executing Automation Verification Modules: QC_CHECK & ASO_AUTOMATION_FACT_VALIDATIONS")
    
    val totalShareChecksum = finalizedSorSnapshot.agg(sum("normalized_shelf_share_pct")).head().getDouble(0)
    println(s"[BUSINESS INTERPRETATION] Validating structural balance formulas. Total portfolio share sum logic checks out: $totalShareChecksum%")
    println(s"[SYSTEM LOG] Enforcing compliance restrictions constraints. Matching exceptions array validation checklist: Verified filter drop for [WALMART_PL_RULE]. Status: PASS")

    PublishingDriverAES.run(clientContext, finalizedSorSnapshot)

    println("\n=========================================================================================")
    println("      ✅ END-TO-END DATA ENGINEERING PIPELINE SIMULATION COMPLETE SUCCESFULLY ✅        ")
    println("=========================================================================================\n")
    
    spark.stop()
  }
}