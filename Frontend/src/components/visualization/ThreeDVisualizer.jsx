import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DObject, CSS2DRenderer } from "three/addons/renderers/CSS2DRenderer.js";

const COLORS = { ink: 0x252321, coral: 0xe9694f, sage: 0x78916c, grid: 0xded8ce };
const LABEL_OFFSET = new THREE.Vector3(0.08, 0.08, 0.08);

function boundsFor(objects) {
  const points = [];
  objects.forEach((object) => {
    if (object.type === "point3d") points.push(new THREE.Vector3(object.x, object.y, object.z));
    if (object.type === "cuboid") {
      const [x, y, z] = object.origin || [0, 0, 0];
      [0, object.width].forEach((dx) => [0, object.height].forEach((dy) => [0, object.depth].forEach((dz) => points.push(new THREE.Vector3(x + dx, y + dy, z + dz)))));
    }
    if (object.type === "cylinder") {
      const [x, y, z] = object.origin || [0, 0, 0];
      const radius = object.radius || 1;
      const height = object.height || 1;
      points.push(new THREE.Vector3(x - radius, y, z - radius), new THREE.Vector3(x + radius, y + height, z + radius));
    }
    if (object.type === "cone") {
      const [x, y, z] = object.origin || [0, 0, 0];
      const radius = object.radius || 1;
      const height = object.height || 1;
      points.push(new THREE.Vector3(x - radius, y, z - radius), new THREE.Vector3(x + radius, y + height, z + radius));
    }
    if (object.type === "vector3d") { points.push(new THREE.Vector3(...object.from), new THREE.Vector3(...object.to)); }
  });
  if (!points.length) points.push(new THREE.Vector3(-2, -2, -2), new THREE.Vector3(2, 2, 2));
  const box = new THREE.Box3().setFromPoints(points);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  return { center, radius: Math.max(size.x, size.y, size.z, 2) * 0.75 };
}

function addLabel(scene, text, position, calculated = false) {
  const element = document.createElement("span");
  element.className = `three-label${calculated ? " calculated" : ""}`;
  element.textContent = text;
  const label = new CSS2DObject(element);
  label.position.copy(position).add(LABEL_OFFSET);
  scene.add(label);
}

function pointMap(objects) {
  return new Map(objects.filter((object) => object.type === "point3d").map((object) => [object.id, object]));
}

function vectorFromPoint(point) { return new THREE.Vector3(point.x, point.y, point.z); }
function vectorFromArray(value) { return Array.isArray(value) && value.length >= 3 ? new THREE.Vector3(value[0], value[1], value[2]) : null; }

function addSegment(scene, first, second, color = COLORS.ink, dashed = false) {
  const geometry = new THREE.BufferGeometry().setFromPoints([first, second]);
  const material = dashed ? new THREE.LineDashedMaterial({ color, dashSize: 0.12, gapSize: 0.08 }) : new THREE.LineBasicMaterial({ color });
  const line = new THREE.Line(geometry, material);
  if (dashed) { line.computeLineDistances(); }
  scene.add(line);
}

function addArrow(scene, from, to, label) {
  const direction = to.clone().sub(from);
  const length = direction.length();
  if (!length) return;
  scene.add(new THREE.ArrowHelper(direction.normalize(), from, length, COLORS.coral, length * 0.12, length * 0.07));
  if (label) addLabel(scene, label, from.clone().lerp(to, 0.62), true);
}

function addFace(scene, vertices, color = COLORS.sage, opacity = 0.22) {
  if (vertices.length < 3) return;
  const positions = [];
  for (let index = 1; index < vertices.length - 1; index += 1) {
    positions.push(...vertices[0].toArray(), ...vertices[index].toArray(), ...vertices[index + 1].toArray());
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  scene.add(new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ color, transparent: true, opacity, side: THREE.DoubleSide })));
}

function addPlane(scene, object, points, sceneRadius) {
  let origin;
  let normal;
  const referenced = (object.points || []).map(vectorFromPoint);
  if (referenced.length >= 3) {
    origin = referenced[0];
    normal = referenced[1].clone().sub(referenced[0]).cross(referenced[2].clone().sub(referenced[0])).normalize();
  } else if (object.point && object.normal) {
    origin = vectorFromPoint(object.point);
    normal = vectorFromPoint(object.normal).normalize();
  }
  if (!origin || !normal || normal.lengthSq() === 0) return;

  const tangent = Math.abs(normal.dot(new THREE.Vector3(0, 1, 0))) > 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
  const u = tangent.cross(normal).normalize();
  const v = normal.clone().cross(u).normalize();
  const size = Math.max(sceneRadius * 1.35, 2);
  const corners = [
    origin.clone().addScaledVector(u, -size).addScaledVector(v, -size),
    origin.clone().addScaledVector(u, size).addScaledVector(v, -size),
    origin.clone().addScaledVector(u, size).addScaledVector(v, size),
    origin.clone().addScaledVector(u, -size).addScaledVector(v, size),
  ];
  addFace(scene, corners, COLORS.sage, 0.18);
  addSegment(scene, corners[0], corners[1], COLORS.sage);
  addSegment(scene, corners[1], corners[2], COLORS.sage);
  addSegment(scene, corners[2], corners[3], COLORS.sage);
  addSegment(scene, corners[3], corners[0], COLORS.sage);
  if (object.label) addLabel(scene, object.label, origin, true);
}

function addCylinder(scene, object) {
  const [x, y, z] = object.origin || [0, 0, 0];
  const radius = object.radius;
  const height = object.height;
  if (![radius, height].every((value) => Number.isFinite(value) && value > 0)) return;

  const geometry = new THREE.CylinderGeometry(radius, radius, height, 64, 1, false);
  const material = new THREE.MeshBasicMaterial({ color: COLORS.sage, transparent: true, opacity: 0.18, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(x, y + height / 2, z);
  scene.add(mesh);

  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), new THREE.LineBasicMaterial({ color: COLORS.ink }));
  edges.position.copy(mesh.position);
  scene.add(edges);

  const top = y + height;
  const bottom = y;
  addSegment(scene, new THREE.Vector3(x, bottom, z), new THREE.Vector3(x + radius, bottom, z), COLORS.coral);
  addSegment(scene, new THREE.Vector3(x + radius * 1.18, bottom, z), new THREE.Vector3(x + radius * 1.18, top, z), COLORS.coral);
  if (object.label) addLabel(scene, object.label, new THREE.Vector3(x, top, z), true);
  if (object.labels?.radius) addLabel(scene, object.labels.radius, new THREE.Vector3(x + radius / 2, bottom, z), true);
  if (object.labels?.height) addLabel(scene, object.labels.height, new THREE.Vector3(x + radius * 1.18, y + height / 2, z), true);
}

function addCone(scene, object) {
  const [x, y, z] = object.origin || [0, 0, 0];
  const radius = object.radius;
  const height = object.height;
  if (![radius, height].every((value) => Number.isFinite(value) && value > 0)) return;

  const geometry = new THREE.ConeGeometry(radius, height, 64, 1, false);
  const material = new THREE.MeshBasicMaterial({ color: COLORS.sage, transparent: true, opacity: 0.18, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(x, y + height / 2, z);
  scene.add(mesh);

  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), new THREE.LineBasicMaterial({ color: COLORS.ink }));
  edges.position.copy(mesh.position);
  scene.add(edges);

  const apex = new THREE.Vector3(x, y + height, z);
  const baseCenter = new THREE.Vector3(x, y, z);
  const baseEdge = new THREE.Vector3(x + radius, y, z);
  addSegment(scene, baseCenter, baseEdge, COLORS.coral);
  addSegment(scene, baseCenter, apex, COLORS.coral, true);
  addSegment(scene, baseEdge, apex, COLORS.coral);
  if (object.label) addLabel(scene, object.label, apex, true);
  if (object.labels?.radius) addLabel(scene, object.labels.radius, baseCenter.clone().lerp(baseEdge, 0.55), true);
  if (object.labels?.height) addLabel(scene, object.labels.height, baseCenter.clone().lerp(apex, 0.5), true);
  if (object.labels?.slantHeight) addLabel(scene, object.labels.slantHeight, baseEdge.clone().lerp(apex, 0.5), true);
}

function renderObjects(scene, objects, sceneRadius) {
  const points = pointMap(objects);
  objects.forEach((object) => {
    if (object.type === "point3d") {
      if (![object.x, object.y, object.z].every(Number.isFinite)) return;
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), new THREE.MeshBasicMaterial({ color: object.calculated ? COLORS.coral : COLORS.ink }));
      mesh.position.set(object.x, object.y, object.z);
      scene.add(mesh);
      addLabel(scene, object.label || object.id, mesh.position, object.calculated);
    }
    if (object.type === "segment3d") {
      const first = points.get(object.from); const second = points.get(object.to);
      if (first && second) addSegment(scene, vectorFromPoint(first), vectorFromPoint(second));
    }
    if (object.type === "line3d") {
      const first = points.get(object.through?.[0]);
      const second = points.get(object.through?.[1]);
      const base = object.point ? vectorFromPoint(object.point) : first && vectorFromPoint(first);
      const direction = object.direction ? vectorFromPoint(object.direction).normalize() : first && second && vectorFromPoint(second).sub(vectorFromPoint(first)).normalize();
      if (base && direction && direction.lengthSq() > 0) {
        const extension = Math.max(sceneRadius * 2, 4);
        addSegment(scene, base.clone().addScaledVector(direction, -extension), base.clone().addScaledVector(direction, extension));
        if (object.label) addLabel(scene, object.label, base, true);
      }
    }
    if (object.type === "vector3d") {
      const from = vectorFromArray(object.from);
      const to = vectorFromArray(object.to);
      if (from && to) addArrow(scene, from, to, object.label);
    }
    if (object.type === "triangle3d" || object.type === "polygon3d") {
      const vertices = Array.isArray(object.vertices) ? object.vertices.map((id) => points.get(id)).filter(Boolean).map(vectorFromPoint) : [];
      if (vertices.length >= 3) {
        const geometry = new THREE.BufferGeometry().setFromPoints([...vertices, vertices[0]]);
        const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: COLORS.ink }));
        scene.add(line);
        addFace(scene, vertices);
      }
    }
    if (object.type === "plane") addPlane(scene, object, points, sceneRadius);
    if (object.type === "cuboid") {
      const [x, y, z] = object.origin || [0, 0, 0];
      if (![object.width, object.height, object.depth].every((value) => Number.isFinite(value) && value > 0)) return;
      const box = new THREE.BoxGeometry(object.width, object.height, object.depth);
      const mesh = new THREE.Mesh(box, new THREE.MeshBasicMaterial({ color: COLORS.sage, transparent: true, opacity: 0.12, side: THREE.DoubleSide }));
      mesh.position.set(x + object.width / 2, y + object.height / 2, z + object.depth / 2);
      scene.add(mesh);
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(box), new THREE.LineBasicMaterial({ color: COLORS.ink }));
      edges.position.copy(mesh.position);
      scene.add(edges);
      if (object.labels?.width) addLabel(scene, object.labels.width, new THREE.Vector3(x + object.width / 2, y, z), true);
      if (object.labels?.height) addLabel(scene, object.labels.height, new THREE.Vector3(x + object.width, y + object.height / 2, z), true);
      if (object.labels?.depth) addLabel(scene, object.labels.depth, new THREE.Vector3(x, y, z + object.depth / 2), true);
    }
    if (object.type === "cylinder") addCylinder(scene, object);
    if (object.type === "cone") addCone(scene, object);
  });
}

export function ThreeDVisualizer({ visualization }) {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const initialRef = useRef(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return undefined;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf3f7ef);
    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    const labels = new CSS2DRenderer();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    labels.setPixelRatio?.(Math.min(window.devicePixelRatio || 1, 2));
    mount.append(renderer.domElement, labels.domElement);
    labels.domElement.className = "three-label-layer";
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = true;
    const group = new THREE.Group();
    scene.add(group);
    scene.add(new THREE.AxesHelper(2));
    const framing = boundsFor(visualization.objects || []);
    scene.add(new THREE.GridHelper(Math.max(framing.radius * 3, 6), 12, COLORS.grid, COLORS.grid));
    renderObjects(group, visualization.objects || [], framing.radius);
    const distance = framing.radius * 3.2;
    camera.position.copy(framing.center).add(new THREE.Vector3(distance, distance, distance));
    camera.near = Math.max(0.01, framing.radius / 100); camera.far = framing.radius * 100; camera.updateProjectionMatrix();
    controls.target.copy(framing.center); controls.update();
    initialRef.current = { position: camera.position.clone(), target: framing.center.clone() };
    sceneRef.current = { scene, camera, renderer, labels, controls, group, mount };
    let frame;
    const resize = () => { const rect = mount.getBoundingClientRect(); camera.aspect = rect.width / Math.max(rect.height, 1); camera.updateProjectionMatrix(); renderer.setSize(rect.width, rect.height); labels.setSize(rect.width, rect.height); };
    const animate = () => { frame = requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); labels.render(scene, camera); };
    resize(); animate();
    const observer = new ResizeObserver(resize); observer.observe(mount);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      controls.dispose();
      mount.replaceChildren();
      scene.traverse((object) => {
        object.geometry?.dispose?.();
        if (Array.isArray(object.material)) object.material.forEach((material) => material.dispose?.());
        else object.material?.dispose?.();
      });
      renderer.dispose();
    };
  }, [visualization]);

  function resetView() { const state = sceneRef.current; const initial = initialRef.current; if (!state || !initial) return; state.camera.position.copy(initial.position); state.controls.target.copy(initial.target); state.controls.update(); }

  if (!visualization || visualization.dimension !== "3d") return <div className="visualization-empty">This 3-D visualization is not available yet.</div>;
  return <div className="visualization-shell three-shell"><div className="visualization-toolbar"><span>Interactive 3D view</span><div className="visualization-controls"><button type="button" onClick={resetView} aria-label="Reset 3D view">Reset</button></div></div><div ref={mountRef} className="three-frame" role="img" aria-label="Interactive 3D geometry diagram" /></div>;
}
