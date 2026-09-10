export function drawCoordinateGrid(context, width, height, transform) {
  const units = transform.unitsPerPixel;
  const step = units < 0.05 ? 1 : units < 0.2 ? 5 : units < 1 ? 10 : Math.ceil(units * 8);
  const origin = transform.toCanvas({ x: 0, y: 0 });
  context.save();
  context.strokeStyle = "#e9e3da";
  context.lineWidth = 1;
  for (let x = origin.x % (step / units); x < width; x += step / units) {
    context.beginPath(); context.moveTo(x, 0); context.lineTo(x, height); context.stroke();
  }
  for (let y = origin.y % (step / units); y < height; y += step / units) {
    context.beginPath(); context.moveTo(0, y); context.lineTo(width, y); context.stroke();
  }
  context.strokeStyle = "#a9a197";
  context.lineWidth = 1.2;
  if (origin.x >= 0 && origin.x <= width) { context.beginPath(); context.moveTo(origin.x, 0); context.lineTo(origin.x, height); context.stroke(); }
  if (origin.y >= 0 && origin.y <= height) { context.beginPath(); context.moveTo(0, origin.y); context.lineTo(width, origin.y); context.stroke(); }
  context.restore();
}
