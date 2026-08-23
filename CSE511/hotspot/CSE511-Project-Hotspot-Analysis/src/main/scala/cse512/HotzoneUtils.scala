package cse512

object HotzoneUtils {

  def ST_Contains(queryRectangle: String, pointString: String ): Boolean = {
    val rectangle = queryRectangle.split(",").map(_.trim.toDouble)
    val point = pointString.split(",").map(_.trim.toDouble)

    val minX = Math.min(rectangle(0), rectangle(2))
    val maxX = Math.max(rectangle(0), rectangle(2))
    val minY = Math.min(rectangle(1), rectangle(3))
    val maxY = Math.max(rectangle(1), rectangle(3))

    return point(0) >= minX && point(0) <= maxX && point(1) >= minY && point(1) <= maxY
  }

}
