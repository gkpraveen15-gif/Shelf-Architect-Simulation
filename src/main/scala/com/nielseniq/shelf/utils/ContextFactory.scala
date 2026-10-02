package com.nielseniq.shelf.utils
import java.util.UUID

case class ProductFilterRule(field: String, operator: String, value: List[String], charType: String)
case class ProductFilter(rules: List[ProductFilterRule], condition: String)
case class ProductInfo(charInfo: String, hierarchyTopLevel: String, additionalProdChars: List[String], prodCharFile: String, productFilter: List[ProductFilter], brandChar: String, manufacturerChar: String)
case class PeriodDefinition(rms_start_date: String, rms_end_date: String, nb_periods: Int, model_start_period: String, model_end_period: String, model_period_weeks: Int, covidModelExclusion: String, covid_start_period: String, covid_end_period: String)
case class MarketInfo(marketSelectionMethod: String, projectionFactorType: String, customMarketFilePath: String, markets: List[String], channelType: String, channel_definition: List[String], market_definition: List[String], channel_threshold: String)
case class RuleDefinition(charDelivery: String, excludedRestrictions: List[String], maskingRule: List[String])
case class CustomModelParams(stringMatchThreshold: String, maxNumberNode: String, maxNumberNodeUpcFlag: String, low_dist_prod_name: String, distribution_threshold: String, low_dist_node_name: String, break_other_bucket: String, minWeeks: String, sales_threshold: String, pl_upc_level: List[String], own_node: List[List[String]])
case class JobFlags(largeStudy: String, qPruning: String)
case class RefreshParams(refreshPeriodicity: String, newItemRefresh: String, initialDbName: String)

case class RuntimeConfig(
    execution_id: Long, analysisId: Long, versionId: Long, region: String, country: String, env: String,
    studyType: String, studyStage: String, deliveryType: String, dataSource: String, modelType: String, studySize: String,
    publishingDb: String, dagType: String, requestSource: String, productInfo: List[ProductInfo],
    periodDefinition: List[PeriodDefinition], marketInfo: List[MarketInfo], rule_definition: List[RuleDefinition],
    customModelParams: List[CustomModelParams], flags: List[JobFlags], refresh_params: List[RefreshParams],
    solutionName: String, modelStatus: String, dag_run_id: String
)

object ContextFactory {
  def getLorealPayload: RuntimeConfig = {
    RuntimeConfig(
      execution_id = 7001662L, analysisId = 11003982L, versionId = 7000988L, region = "US", country = "US", env = "cloud_prod",
      studyType = "model", studyStage = "TRIGGER_SEGMENTATION", deliveryType = "Manufacturer", dataSource = "BDL", modelType = "micro", studySize = "",
      publishingDb = "seff_aso_US_prod_publish_7001662", dagType = "preview", requestSource = "aes",
      productInfo = List(ProductInfo(
        charInfo = "discover|CSTM_19639,CSTM_19561,CSTM_19501|255891", hierarchyTopLevel = "TOTAL HAIR CARE",
        additionalProdChars = List("CSTM_19375", "CSTM_19357", "CSTM_19380", "CSTM_19352", "CSTM_19345", "CSTM_19377"), prodCharFile = "",
        productFilter = List(ProductFilter(rules = List(ProductFilterRule(field = "CSTM_19639", operator = "IN", value = List("HAIR CARE", "STYLING"), charType = "discover|255891")), condition = "")),
        brandChar = "CSTM_19501", manufacturerChar = "CSTM_19621"
      )),
      periodDefinition = List(PeriodDefinition("2024-09-01", "2026-08-29", 104, "2025-08-31", "2026-08-29", 52, "false", "", "")),
      marketInfo = List(MarketInfo("customFile", "census", "abfss://seff-aso@csusprodprocessing.dfs.core.windows.net/mcc/store_geo/11003921/20260827205851_L'Oreal_Club_Retailer_List.csv", List(), "", List(), List(), "10")),
      rule_definition = List(RuleDefinition("Masked", List("WALMART_PL_RULE"), List(""))),
      customModelParams = List(CustomModelParams("0.99", "20", "0", "AO LOW DISTRIBUTION", "10", "ALL OTHER", "1:1", "8", "0.05", List("", "PRIVATE LABEL"), List(List("", "")))),
      flags = List(JobFlags("no", "no")), refresh_params = List(RefreshParams("none", "no", "na")),
      solutionName = "shelf_architect", modelStatus = "Final", dag_run_id = "CONNECT_ASO_LOreal_Hair_Care_Club_2026_US_7001662_7000988_2026-09-09T16:55:02+00:00"
    )
  }
}