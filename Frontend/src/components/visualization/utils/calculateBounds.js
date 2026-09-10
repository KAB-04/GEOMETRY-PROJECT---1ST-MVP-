export function getObjectPoints(objects) {
  const points = [];
  for (const object of objects) {
    if (object.type === "point" && Number.isFinite(object.x) && Number.isFinite(object.y)) {
      points.push({ x: object.x, y: object.y });
    }
    if (object.type === "circle" && object.center && Number.isFinite(object.radius)) {
      points.push(
        { x: object.center.x - object.radius, y: object.center.y - object.radius },
        { x: object.center.x + object.radius, y: object.center.y + object.radius },
      );
    }
  }
  return points;
}

export function calculateBounds(objects) {
  const points = getObjectPoints(objects);
  if (!points.length) return { minX: -5, maxX: 5, minY: -5, maxY: 5 };
  const xs = points.map((point) => point.x);
  const ys = points.map((point) => point.y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const xSize = Math.max(maxX - minX, 1);
  const ySize = Math.max(maxY - minY, 1);
  const paddingX = xSize * 0.18;
  const paddingY = ySize * 0.18;
  return { minX: minX - paddingX, maxX: maxX + paddingX, minY: minY - paddingY, maxY: maxY + paddingY };
}
