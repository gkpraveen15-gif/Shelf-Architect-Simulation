# Stage 1: Build environment
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
ENTRYPOINT ["spark-submit", "--class", "com.nielseniq.shelf.MainSimulationRunner", "--master", "local[*]", "seff-aso-common.jar"]