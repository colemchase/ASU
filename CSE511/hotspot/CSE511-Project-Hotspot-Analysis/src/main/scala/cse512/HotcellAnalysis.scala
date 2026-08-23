package cse512

import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions.udf
import org.apache.spark.sql.functions._

object HotcellAnalysis {
  Logger.getLogger("org.spark_project").setLevel(Level.WARN)
  Logger.getLogger("org.apache").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)
  Logger.getLogger("com").setLevel(Level.WARN)

def runHotcellAnalysis(spark: SparkSession, pointPath: String): DataFrame =
{
  import spark.implicits._

  // Load the original data from a data source
  var pickupInfo = spark.read.format("com.databricks.spark.csv").option("delimiter",";").option("header","false").load(pointPath);
  pickupInfo.createOrReplaceTempView("nyctaxitrips")

  // Assign cell coordinates based on pickup points
  spark.udf.register("CalculateX",(pickupPoint: String)=>((
    HotcellUtils.CalculateCoordinate(pickupPoint, 0)
    )))
  spark.udf.register("CalculateY",(pickupPoint: String)=>((
    HotcellUtils.CalculateCoordinate(pickupPoint, 1)
    )))
  spark.udf.register("CalculateZ",(pickupTime: String)=>((
    HotcellUtils.CalculateCoordinate(pickupTime, 2)
    )))
  pickupInfo = spark.sql("select CalculateX(nyctaxitrips._c5),CalculateY(nyctaxitrips._c5), CalculateZ(nyctaxitrips._c1) from nyctaxitrips")
  var newCoordinateName = Seq("x", "y", "z")
  pickupInfo = pickupInfo.toDF(newCoordinateName:_*)

  // Define the min and max of x, y, z
  val minX = -74.50/HotcellUtils.coordinateStep
  val maxX = -73.70/HotcellUtils.coordinateStep
  val minY = 40.50/HotcellUtils.coordinateStep
  val maxY = 40.90/HotcellUtils.coordinateStep
  val minZ = 1
  val maxZ = 31
  val numCells = (maxX - minX + 1)*(maxY - minY + 1)*(maxZ - minZ + 1)

  val allCells = (for {
    x <- minX.toInt to maxX.toInt
    y <- minY.toInt to maxY.toInt
    z <- minZ to maxZ
  } yield (x, y, z)).toDF("x", "y", "z")

  val pickupCounts = pickupInfo
    .filter($"x" >= minX && $"x" <= maxX && $"y" >= minY && $"y" <= maxY && $"z" >= minZ && $"z" <= maxZ)
    .groupBy("x", "y", "z")
    .count()
    .withColumnRenamed("count", "numPoints")

  val cellStats = allCells
    .join(pickupCounts, Seq("x", "y", "z"), "left_outer")
    .na.fill(0, Seq("numPoints"))

  val totals = cellStats
    .agg(
      sum($"numPoints").cast("double").as("sumPoints"),
      sum(pow($"numPoints".cast("double"), 2)).as("sumSquares")
    )
    .first()

  val sumPoints = totals.getAs[Double]("sumPoints")
  val sumSquares = totals.getAs[Double]("sumSquares")
  val mean = sumPoints / numCells
  val standardDeviation = Math.sqrt((sumSquares / numCells) - HotcellUtils.square(mean))

  val expandedNeighborSums = pickupCounts
    .as[(Int, Int, Int, Long)]
    .flatMap { case (x, y, z, numPoints) =>
      for {
        nx <- (x - 1) to (x + 1)
        ny <- (y - 1) to (y + 1)
        nz <- (z - 1) to (z + 1)
        if nx >= minX.toInt && nx <= maxX.toInt &&
          ny >= minY.toInt && ny <= maxY.toInt &&
          nz >= minZ && nz <= maxZ
      } yield (nx, ny, nz, numPoints)
    }
    .toDF("x", "y", "z", "numPoints")
    .groupBy("x", "y", "z")
    .agg(sum($"numPoints").cast("double").as("neighborSum"))

  val resultDf = allCells
    .join(expandedNeighborSums, Seq("x", "y", "z"), "left_outer")
    .na.fill(0, Seq("neighborSum"))
    .withColumn(
      "neighborCount",
      ((least($"x" + 1, lit(maxX.toInt)) - greatest($"x" - 1, lit(minX.toInt)) + 1) *
        (least($"y" + 1, lit(maxY.toInt)) - greatest($"y" - 1, lit(minY.toInt)) + 1) *
        (least($"z" + 1, lit(maxZ)) - greatest($"z" - 1, lit(minZ)) + 1)).cast("double")
    )
    .withColumn(
      "gScore",
      ($"neighborSum" - lit(mean) * $"neighborCount") /
        (lit(standardDeviation) * sqrt((lit(numCells) * $"neighborCount" - pow($"neighborCount", 2)) / lit(numCells - 1)))
    )
    .orderBy(desc("gScore"))
    .select("x", "y", "z")

  return resultDf
}
}
