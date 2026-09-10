import { Canvas2D } from "./Canvas2D";
import { ThreeDVisualizer } from "./ThreeDVisualizer";

export function GeometryVisualizer({ visualization }) {
  if (!visualization) return null;
  if (visualization.dimension === "2d" && visualization.objects?.length) {
    return <Canvas2D visualization={visualization} />;
  }
  if (visualization.dimension === "2d") {
    return <div className="visualization-empty">A diagram is not available for this operation yet.</div>;
  }
  if (visualization.dimension === "3d" && visualization.objects?.length) {
    return <ThreeDVisualizer visualization={visualization} />;
  }
  if (visualization.dimension === "3d") {
    return <div className="visualization-empty">A 3-D diagram is not available for this operation yet.</div>;
  }
  if (import.meta.env.DEV) console.warn(`Unsupported visualization dimension: ${visualization.dimension}`);
  return <div className="visualization-empty">This visualization will be available in a later phase.</div>;
}
