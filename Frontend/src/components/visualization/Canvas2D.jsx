import { useEffect, useRef, useState } from "react";
import { calculateBounds } from "./utils/calculateBounds";
import { createTransform } from "./utils/coordinateTransform";
import { drawCoordinateGrid } from "./CoordinateGrid";
import { renderObjects } from "./renderers";

export function Canvas2D({ visualization }) {
  const canvasRef = useRef(null);
  const frameRef = useRef(null);
  const dragRef = useRef(null);
  const [view, setView] = useState({ zoom: 1, pan: { x: 0, y: 0 } });
  const viewRef = useRef(view);
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const bounds = calculateBounds(visualization?.objects || []);

  viewRef.current = view;

  function drawCanvas() {
    const canvas = canvasRef.current;
    const frame = frameRef.current;
    if (!canvas || !frame) return;
    const context = canvas.getContext("2d");
    const rect = frame.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, rect.width, rect.height);
    const transform = createTransform(bounds, rect.width, rect.height, viewRef.current.zoom, viewRef.current.pan);
    if (visualization?.coordinateSystem) drawCoordinateGrid(context, rect.width, rect.height, transform);
    renderObjects(context, visualization, transform, rect.width, rect.height);
  }

  useEffect(() => {
    drawCanvas();
    const observer = new ResizeObserver(drawCanvas);
    const frame = frameRef.current;
    if (!frame) return undefined;
    observer.observe(frame);
    return () => observer.disconnect();
  }, [bounds.minX, bounds.maxX, bounds.minY, bounds.maxY, visualization]);

  useEffect(() => {
    drawCanvas();
  }, [view]);

  function updateZoom(amount) {
    setView((current) => ({ ...current, zoom: Math.min(5, Math.max(0.35, current.zoom * amount)) }));
  }

  function handleWheel(event) {
    event.preventDefault();
    updateZoom(event.deltaY < 0 ? 1.12 : 0.89);
  }

  function handlePointerDown(event) {
    event.currentTarget.setPointerCapture(event.pointerId);
    dragRef.current = { x: event.clientX, y: event.clientY, pan: view.pan };
  }

  function handlePointerMove(event) {
    if (dragRef.current) {
      const drag = dragRef.current;
      setView((current) => ({ ...current, pan: { x: drag.pan.x + event.clientX - drag.x, y: drag.pan.y + event.clientY - drag.y } }));
    }
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const transform = createTransform(bounds, rect.width, rect.height, view.zoom, view.pan);
    const hit = (visualization?.objects || []).find((object) => object.type === "point" && Math.hypot(transform.toCanvas(object).x - (event.clientX - rect.left), transform.toCanvas(object).y - (event.clientY - rect.top)) < 12);
    setHoveredPoint(hit || null);
  }

  function stopDragging() { dragRef.current = null; }
  function resetView() { setView({ zoom: 1, pan: { x: 0, y: 0 } }); }

  if (!visualization || visualization.dimension !== "2d") return <div className="visualization-empty">This visualization is not available yet.</div>;
  return (
    <div className="visualization-shell">
      <div className="visualization-toolbar">
        <span>Interactive 2D view</span>
        <div className="visualization-controls">
          <button type="button" onClick={() => updateZoom(1.2)} aria-label="Zoom in">+</button>
          <button type="button" onClick={() => updateZoom(0.83)} aria-label="Zoom out">−</button>
          <button type="button" onClick={resetView} aria-label="Reset view">Reset</button>
        </div>
      </div>
      <div ref={frameRef} className="canvas-frame">
        <canvas ref={canvasRef} role="img" aria-label="Interactive geometry diagram" onWheel={handleWheel} onPointerDown={handlePointerDown} onPointerMove={handlePointerMove} onPointerUp={stopDragging} onPointerLeave={() => { stopDragging(); setHoveredPoint(null); }} />
        {hoveredPoint && <div className="point-tooltip"><strong>{hoveredPoint.label || hoveredPoint.id}</strong><span>({hoveredPoint.x}, {hoveredPoint.y})</span></div>}
      </div>
    </div>
  );
}
