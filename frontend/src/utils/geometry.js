export function toSvgPoints(points) {
  return points.map((p) => `${p[0]},${p[1]}`).join(" ");
}

export function getCentroid(points) {
  const sum = points.reduce((acc, p) => [acc[0] + p[0], acc[1] + p[1]], [0, 0]);
  return [sum[0] / points.length, sum[1] / points.length];
}