export function createTransform(bounds, width, height, zoom = 1, pan = { x: 0, y: 0 }) {
  const rangeX = Math.max(bounds.maxX - bounds.minX, 1);
  const rangeY = Math.max(bounds.maxY - bounds.minY, 1);
  const scale = Math.min(width / rangeX, height / rangeY) * 0.92 * zoom;
  const centerX = (bounds.minX + bounds.maxX) / 2;
  const centerY = (bounds.minY + bounds.maxY) / 2;
  return {
    scale,
    toCanvas(point) {
      return {
        x: width / 2 + (point.x - centerX) * scale + pan.x,
        y: height / 2 - (point.y - centerY) * scale + pan.y,
      };
    },
    unitsPerPixel: 1 / scale,
  };
}

export function distanceInPixels(first, second) {
  return Math.hypot(first.x - second.x, first.y - second.y);
}
