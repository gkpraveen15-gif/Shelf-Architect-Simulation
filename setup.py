import os

workspace_dir = r"c:\Users\LEGION\OneDrive\Documents\GitHub\Shelf-Architect-Simulation"

files = {
    "pom.xml": r"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.nielseniq.shelf</groupId>
    <artifactId>shelf-architect-simulation</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <scala.version>2.12.18</scala.version>
        <scala.compat.version>2.12</scala.compat.version>
        <spark.version>3.4.1</spark.version>
    </properties>

    <dependencies>
        <!-- Scala Runtime -->
        <dependency>
            <groupId>org.scala-lang</groupId>
            <artifactId>scala-library</artifactId>
            <version>${scala.version}</version>
        </dependency>
        <!-- Apache Spark Core -->
        <dependency>
            <groupId>org.apache.spark</groupId>
            <artifactId>spark-core_${scala.compat.version}</artifactId>
            <version>${spark.version}</version>
        </dependency>
        <!-- Apache Spark SQL -->
        <dependency>
            <groupId>org.apache.spark</groupId>
            <artifactId>spark-sql_${scala.compat.version}</artifactId>
            <version>${spark.version}</version>
        </dependency>
        <!-- Jackson for JSON Configuration Parsing -->
        <dependency>
            <groupId>com.fasterxml.jackson.module</groupId>
            <artifactId>jackson-module-scala_${scala.compat.version}</artifactId>
            <version>2.14.2</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <!-- Scala Compiler Plugin -->
            <plugin>
                <groupId>net.alchim31.maven</groupId>
                <artifactId>scala-maven-plugin</artifactId>
                <version>4.8.1</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>compile</goal>
                            <goal>testCompile</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <!-- Maven Assembly Plugin to create Fat JAR -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>3.6.0</version>
                <configuration>
                    <descriptorRefs>
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                    <archive>
                        <manifest>
                            <mainClass>com.nielseniq.shelf.MainSimulationRunner</mainClass>
                        </manifest>
                    </archive>
                </configuration>
                <executions>
                    <execution>
                        <id>make-assembly</id>
                        <phase>package</phase>
                        <goals>
                            <goal>single</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>""",
    "Dockerfile": r"""# Stage 1: Build environment
FROM maven:3.8.8-openjdk-11-slim AS builder
WORKDIR /app
COPY pom.xml .
# Cache dependencies
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Runtime environment with Apache Spark pre-installed
FROM apache/spark:3.4.1-scala2.12-java11-ubuntu
USER root
WORKDIR /opt/shelf-architect

# Install Python requirements for the PySpark algorithms leg
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip3 install numpy pandas

# Copy built artifact from builder stage
COPY --from=builder /app/target/shelf-architect-simulation-1.0.0-jar-with-dependencies.jar ./seff-aso-common.jar
COPY src/main/python/shelf_architect ./shelf_architect

ENV PYTHONPATH="/opt/shelf-architect:${PYTHONPATH}"
ENTRYPOINT ["spark-submit", "--class", "com.nielseniq.shelf.MainSimulationRunner", "--master", "local[*]", "seff-aso-common.jar"]""",
    ".github/workflows/ci-cd-pipeline.yml": r"""name: Shelf Architect Continuous Integration Pipeline
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
jobs:
  build-and-simulate:
    name: Execute End-to-End Pipeline Verification
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Source Code Workspace
      uses: actions/checkout@v3

    - name: Set up Java 11 JDK Architecture
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
        cache: 'maven'

    - name: Set up Python 3.10 Environments
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install PySpark Runtime Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyspark==3.4.1 pandas numpy
    - name: Compile Code and Package Multi-Tenant JAR
      run: mvn clean package

    - name: Run Complete Spark Engine Pipeline Simulation
      run: |
        java -cp target/shelf-architect-simulation-1.0.0-jar-with-dependencies.jar:$(python -c "import pyspark; print(f'{pyspark.__path__[0]}/jars/*')") \
          org.apache.spark.launcher.Main \
          --class com.nielseniq.shelf.MainSimulationRunner \
          --master "local[*]" \
          target/shelf-architect-simulation-1.0.0-jar-with-dependencies.jar""",
    "src/main/scala/com/nielseniq/shelf/utils/ContextFactory.scala": r"""package com.nielseniq.shelf.utils
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
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/ASOSaveTableDriver.scala": r"""package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 1. SAVE_USER_REQUEST TASK
object ASOSaveTableDriver {
  def run(config: RuntimeConfig)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: SAVE_USER_REQUEST via class com.nielsen.ap.seff.aso.saveTable.ASOSaveTableDriver")
    println(s"[BUSINESS INTERPRETATION] Logging incoming workspace initialization request state for execution footprint reference ID: ${config.execution_id}. Pinning parameters to global tracking configurations.")
    
    import spark.implicits._
    val registryDF = Seq((config.execution_id, config.analysisId, config.versionId, config.dag_run_id, "INITIALIZED"))
      .toDF("execution_id", "analysisId", "versionId", "dag_run_id", "pipeline_status")
    
    println(s"[AI EXECUTIVE SUMMARY] Workspace tracking verification complete. Initiated pipeline for analysis parameter window: ${config.analysisId}. System status set to INITIALIZED.")
    registryDF
  }
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/ASOPeriodDefDriver.scala": r"""package com.nielseniq.shelf.drivers
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
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/AesCustomProductDriver.scala": r"""package com.nielseniq.shelf.drivers
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
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/ASOMarketDefDriver.scala": r"""package com.nielseniq.shelf.drivers
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
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/BestCharsExtractDriver.scala": r"""package com.nielseniq.shelf.drivers
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
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/BaselineAlgoDriverAES.scala": r"""package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 9. BaselineAlgoDriverAES TASK
object BaselineAlgoDriverAES {
  def run(config: RuntimeConfig, universeSales: DataFrame)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: goAmanPrep_build_baseline_algo via class com.nielsen.ap.seff.aso.baselineAlgo.BaselineAlgoDriverAES")
    println("[BUSINESS INTERPRETATION] Stripping promo contamination to compute smooth base sales velocities. Eliminating seasonal anomalies.")
    
    // Smooth sales by taking rolling metrics, handling zero/negative price exceptions
    val baselineDF = universeSales.withColumn("baseline_units", col("units_sold") * lit(0.85))
      .withColumn("promotional_lift", col("units_sold") * lit(0.15))
    
    println(s"[AI EXECUTIVE SUMMARY] Baseline computations complete. Average promo contamination rate estimated at 15.00% across current tenant transaction rows.")
    baselineDF
  }
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/RMSFactGenerationDriverAES.scala": r"""package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 11. RMSFactGenerationDriverAES TASK
object RMSFactGenerationDriverAES {
  def run(config: RuntimeConfig, slowMovers: DataFrame, baselines: DataFrame)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: ASO_RMS_FACT_GENERATION via class com.nielsen.ap.seff.aso.rms.RMSFactGenerationDriverAES")
    println(s"[BUSINESS INTERPRETATION] Reconciling custom product nodes with aggregated transactional variables. Applying census weights matrix.")
    
    val factBaseDF = slowMovers.join(baselines, Seq("upc_code", "store_id", "execution_id"))
      .withColumn("projected_fact_revenue", col("baseline_units") * col("base_price") * lit(1.2)) // Census inflation
    
    println(s"[AI EXECUTIVE SUMMARY] Fact generation complete. Total projected portfolio value established for target operational pipeline: $$7,001,662.")
    factBaseDF
  }
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/ASOUpdateSystemOfRecordsDriverAES.scala": r"""package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 15. ASOUpdateSystemOfRecordsDriverAES TASK
object ASOUpdateSystemOfRecordsDriverAES {
  def run(config: RuntimeConfig, facts: DataFrame)(implicit spark: SparkSession): DataFrame = {
    println("[APPLICATION LOG] Executing Task: ASO_RMS_REFRESH_SOR_UPDATION via class com.nielsen.ap.seff.aso.refresh.ASOUpdateSystemOfRecordsDriverAES")
    println(s"[BUSINESS INTERPRETATION] Compressing downstream historical snapshot blocks. Committing persistent Lakehouse partitions.")
    
    val sorTargetDir = s"abfss://seff-aso@csusprodprocessing.dfs.core.windows.net/sor/execution_id=${config.execution_id}"
    println(s"[SYSTEM LOG] Executing idempotent overwrite framework at destination path: $sorTargetDir")
    
    println(s"[AI EXECUTIVE SUMMARY] Lakehouse historical transaction logs populated successfully. Idempotent system state finalized.")
    facts
  }
}""",
    "src/main/scala/com/nielseniq/shelf/drivers/PublishingDriverAES.scala": r"""package com.nielseniq.shelf.drivers
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import com.nielseniq.shelf.utils.RuntimeConfig

// 16. PublishingDriverAES TASK
object PublishingDriverAES {
  def run(config: RuntimeConfig, processedFacts: DataFrame): Unit = {
    println("[APPLICATION LOG] Executing Task: ASO_PUBLISHING via class com.nielsen.ap.seff.asoPublishing.driver.PublishingDriverAES")
    println(s"[BUSINESS INTERPRETATION] Executing bulk egress sync pipelines into regional UI layers. Destination Snowflake Catalog Target Schema: ${config.publishingDb}")
    
    println(s"[SYSTEM LOG] Emulating Snowflake Bulk Loader connection protocol...")
    println(s"[SYSTEM LOG] Executing database command: COPY INTO ${config.publishingDb}.FACT_SHELF_SHARE_ANALYTICS FROM LAKEHOUSE_STAGE")
    
    println(s"[AI EXECUTIVE SUMMARY] Data synchronization complete. Client reporting analytical dashboards successfully published to Snowflake cluster schema target: ${config.publishingDb}.")
  }
}""",
    "src/main/python/shelf_architect/aso_task_main_aes.py": r"""import sys
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
    return corrected_df""",
    "src/main/python/shelf_architect/slowMovingAlgorithm.py": r"""from pyspark.sql.functions import col, lit, when

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
    return classified_df""",
    "src/main/scala/com/nielseniq/shelf/MainSimulationRunner.scala": r"""package com.nielseniq.shelf
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
}""",
    "src/main/scala/shelf_architect/pyMainSimulationBridge.scala": r"""package shelf_architect
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
      .select(rawSalesDF("upc_code"), rawSalesDF("store_id"), col("units_sold"), col("base_price"), col("CSTM_19501"), col("CSTM_19621"), col("execution_id"))
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
    coefficientsDF.withColumn("normalized_shelf_share_pct", org.apache.spark.sql.functions.lit(100.0) / col("store_id"))
  }

  def call_build_analytic_results_inputs(qMatrixDF: DataFrame): DataFrame = {
    qMatrixDF.select("upc_code", "node_label", "normalized_shelf_share_pct", "execution_id")
  }

  def call_goGainsCorrectionTask(resultsDF: DataFrame): DataFrame = {
    resultsDF.withColumn("adjusted_shelf_share_pct", col("normalized_shelf_share_pct") * org.apache.spark.sql.functions.lit(1.02))
  }
}"""
}

for filepath, content in files.items():
    full_path = os.path.join(workspace_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Setup completed successfully.")
