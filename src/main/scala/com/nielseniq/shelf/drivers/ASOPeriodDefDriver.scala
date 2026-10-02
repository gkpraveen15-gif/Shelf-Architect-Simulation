package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 2. PERIOD_DEFINITION TASK
object ASOPeriodDefDriver {
  def run(config: RuntimeConfig)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: PERIOD_DEFINITION via class com.nielsen.ap.seff.aso.periodDefinition.ASOPeriodDefDriver")
    println(s"[BUSINESS INTERPRETATION] Translating calendar windows to numeric scopes. Total configured historical database parameters match: ${config.periodDefinition.head.nb_periods} weeks.")
    
    import spark.implicits._
    val p = config.periodDefinition.head
    val periodsDF = Seq((config.execution_id, p.rms_start_date, p.rms_end_date, p.nb_periods, p.model_start_period, p.model_end_period, p.model_period_weeks))
      .toDF("execution_id", "rms_start_date", "rms_end_date", "nb_periods", "model_start_period", "model_end_period", "model_period_weeks")
    
    println(s"[AI EXECUTIVE SUMMARY] Active analytical tracking window bounded from ${p.model_start_period} to ${p.model_end_period}, isolating exactly ${p.model_period_weeks} key model estimation parameters.")
    periodsDF
  }
}