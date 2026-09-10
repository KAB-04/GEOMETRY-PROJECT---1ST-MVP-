const COLORS = { ink: "#252321", coral: "#e9694f", sage: "#78916c", grid: "#ded8ce", muted: "#827d75" };

function pointFor(id, points) {
  return points.get(id);
}

function drawLabel(context, text, x, y, options = {}) {
  if (!text) return;
  context.save();
  context.font = options.font || "11px Manrope, sans-serif";
  context.fillStyle = options.color || COLORS.ink;
  context.textAlign = options.align || "center";
  context.textBaseline = "middle";
  context.fillText(String(text), x + (options.offsetX || 0), y + (options.offsetY || 0));
  context.restore();
}

function drawPoint(context, object, transform) {
  const point = transform.toCanvas(object);
  context.save();
  context.fillStyle = object.variant === "transformed" || object.calculated ? COLORS.coral : COLORS.ink;
  context.beginPath();
  context.arc(point.x, point.y, 4.5, 0, Math.PI * 2);
  context.fill();
  drawLabel(context, object.label || object.id, point.x, point.y, { offsetX: 9, offsetY: -9, align: "left", font: "600 12px Manrope, sans-serif" });
  if (object.coordinateLabel !== false) drawLabel(context, `(${object.x}, ${object.y})`, point.x, point.y, { offsetX: 9, offsetY: 8, align: "left", color: COLORS.muted, font: "10px DM Mono, monospace" });
  context.restore();
}

function drawSegment(context, object, points, transform) {
  const start = pointFor(object.from, points);
  const end = pointFor(object.to, points);
  if (!start || !end) return;
  const first = transform.toCanvas(start);
  const second = transform.toCanvas(end);
  context.save();
  context.strokeStyle = object.variant === "correspondence" ? COLORS.muted : object.variant === "transformed" || object.calculated ? COLORS.coral : COLORS.ink;
  context.lineWidth = object.calculated || object.variant === "transformed" ? 2.5 : 1.8;
  if (object.dashed) context.setLineDash([6, 5]);
  context.beginPath();
  context.moveTo(first.x, first.y);
  context.lineTo(second.x, second.y);
  context.stroke();
  const midpoint = { x: (first.x + second.x) / 2, y: (first.y + second.y) / 2 };
  drawLabel(context, object.label, midpoint.x, midpoint.y, { offsetY: -9, color: object.calculated ? COLORS.coral : COLORS.muted, font: "10px DM Mono, monospace" });
  context.restore();
}

function drawLine(context, object, points, transform, width, height) {
  const first = pointFor(object.through?.[0], points);
  const second = pointFor(object.through?.[1], points);
  if (!first || !second) return;
  const dx = second.x - first.x;
  const dy = second.y - first.y;
  const length = Math.hypot(dx, dy) || 1;
  const extension = Math.max(width, height) / transform.scale * 2;
  const start = transform.toCanvas({ x: first.x - (dx / length) * extension, y: first.y - (dy / length) * extension });
  const end = transform.toCanvas({ x: second.x + (dx / length) * extension, y: second.y + (dy / length) * extension });
  context.save();
  context.strokeStyle = COLORS.ink;
  context.lineWidth = 1.4;
  context.beginPath();
  context.moveTo(start.x, start.y);
  context.lineTo(end.x, end.y);
  context.stroke();
  context.restore();
}

function drawCircle(context, object, transform) {
  if (!Number.isFinite(object.radius) || object.radius <= 0) return;
  const center = transform.toCanvas(object.center);
  context.save();
  context.strokeStyle = COLORS.sage;
  context.lineWidth = 2;
  context.beginPath();
  context.arc(center.x, center.y, object.radius * transform.scale, 0, Math.PI * 2);
  context.stroke();
  drawLabel(context, object.label, center.x, center.y - object.radius * transform.scale - 10, { color: COLORS.sage, font: "10px DM Mono, monospace" });
  context.restore();
}

function drawPolygon(context, object, points, transform) {
  const vertices = object.vertices.map((id) => pointFor(id, points)).filter(Boolean).map(transform.toCanvas);
  if (vertices.length < 3) return;
  context.save();
  context.fillStyle = object.variant === "transformed" ? "rgba(233, 105, 79, .12)" : "rgba(202, 216, 192, .22)";
  context.strokeStyle = object.variant === "transformed" ? COLORS.coral : COLORS.ink;
  context.lineWidth = 1.8;
  context.beginPath();
  context.moveTo(vertices[0].x, vertices[0].y);
  vertices.slice(1).forEach((point) => context.lineTo(point.x, point.y));
  context.closePath();
  context.fill();
  context.stroke();
  context.restore();
}

function drawAngle(context, object, points, transform) {
  const vertex = pointFor(object.vertex, points);
  const first = pointFor(object.from, points);
  const second = pointFor(object.to, points);
  if (!vertex || !first || !second) return;
  const center = transform.toCanvas(vertex);
  const firstCanvas = transform.toCanvas(first);
  const secondCanvas = transform.toCanvas(second);
  const firstAngle = Math.atan2(firstCanvas.y - center.y, firstCanvas.x - center.x);
  const secondAngle = Math.atan2(secondCanvas.y - center.y, secondCanvas.x - center.x);
  const radius = 20;
  context.save();
  context.strokeStyle = object.calculated ? COLORS.coral : COLORS.sage;
  context.lineWidth = 1.5;
  context.beginPath();
  context.arc(center.x, center.y, radius, firstAngle, secondAngle, false);
  context.stroke();
  if (object.value !== undefined) drawLabel(context, `${object.value}°`, center.x, center.y - 28, { color: object.calculated ? COLORS.coral : COLORS.sage, font: "10px DM Mono, monospace" });
  context.restore();
}

export function renderObjects(context, visualization, transform, width, height) {
  const objects = visualization?.objects || [];
  const points = new Map(objects.filter((object) => object.type === "point").map((object) => [object.id, object]));
  objects.filter((object) => object.type === "polygon").forEach((object) => drawPolygon(context, object, points, transform));
  objects.filter((object) => object.type === "circle").forEach((object) => drawCircle(context, object, transform));
  objects.filter((object) => object.type === "line").forEach((object) => drawLine(context, object, points, transform, width, height));
  objects.filter((object) => object.type === "segment").forEach((object) => drawSegment(context, object, points, transform));
  objects.filter((object) => object.type === "angle").forEach((object) => drawAngle(context, object, points, transform));
  objects.filter((object) => object.type === "point").forEach((object) => drawPoint(context, object, transform));
}
