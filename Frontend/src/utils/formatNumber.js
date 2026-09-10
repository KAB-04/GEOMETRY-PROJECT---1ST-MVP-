const INTEGER_EPSILON = 1e-9;

export function formatNumber(value, maximumFractionDigits = 2) {
  if (value === null || value === undefined || value === "") return "";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value !== "number" || !Number.isFinite(value)) return String(value);
  if (Math.abs(value - Math.round(value)) <= INTEGER_EPSILON) return String(Math.round(value));
  return new Intl.NumberFormat("en", {
    maximumFractionDigits,
    useGrouping: false,
  }).format(value);
}

export function formatCoordinate(value) {
  return formatNumber(value, 4);
}

export function formatResult(value) {
  if (value === null || value === undefined) return "No result returned";
  if (Array.isArray(value)) return `(${value.map(formatCoordinate).join(", ")})`;
  if (value && Array.isArray(value.transformed)) {
    return value.transformed
      .map((point) => `${point.label || point.id} = (${formatCoordinate(point.x)}, ${formatCoordinate(point.y)})`)
      .join("   ");
  }
  if (value?.final?.points) {
    const points = value.final.points;
    if (!points.length) return value.final.relationship === "coincident" ? "Infinitely many intersections" : "No intersection";
    return points.map((point, index) => `P${index + 1} = (${formatCoordinate(point.x)}, ${formatCoordinate(point.y)})`).join("   ");
  }
  if (value && typeof value === "object") return JSON.stringify(value, null, 2);
  return formatNumber(value);
}
