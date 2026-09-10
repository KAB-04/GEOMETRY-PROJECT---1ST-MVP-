import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DObject, CSS2DRenderer } from "three/addons/renderers/CSS2DRenderer.js";

const COLORS = { ink: 0x252321, coral: 0xe9694f, sage: 0x78916c, grid: 0xded8ce };

function boundsFor(objects) {
  const points = [];
  objects.forEach((object) => {
    if (object.type === "point3d") points.push(new THREE.Vector3(object.x, object.y, object.z));
    if (object.type === "cuboid") {
      const [x, y, z] = object.origin || [0, 0, 0];
      [0, object.width].forEach((dx) => [0, object.height].forEach((dy) => [0, object.depth].forEach((dz) => points.push(new THREE.Vector3(x + dx, y + dy, z + dz)))));
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
  label.position.copy(position);
  scene.add(label);
}

function pointMap(objects) {
  return new Map(objects.filter((object) => object.type === "point3d").map((object) => [object.id, object]));
}

function vectorFromPoint(point) { return new THREE.Vector3(point.x, point.y, point.z); }

function addSegment(scene, first, second, color = COLORS.ink, dashed = false) {
  const geometry = new THREE.BufferGeometry().setFromPoints([first, second]);
  const material = dashed ? new THREE.LineDashedMaterial({ color, dashSize: 0.12, gapSize: 0.08 }) : new THREE.LineBasicMaterial({ color });
  const line = new THREE.Line(geometry, material);
  if (dashed) { line.computeLineDistances(); }
  scene.add(line);
}

function addArrow(scene, from, to) {
  const direction = to.clone().sub(from);
  const length = direction.length();
  if (!length) return;
  scene.add(new THREE.ArrowHelper(direction.normalize(), from, length, COLORS.coral, length * 0.12, length * 0.07));
}

function renderObjects(scene, objects) {
  const points = pointMap(objects);
  objects.forEach((object) => {
    if (object.type === "point3d") {
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
      const first = points.get(object.through?.[0]); const second = points.get(object.through?.[1]);
      if (first && second) {
        const direction = vectorFromPoint(second).sub(vectorFromPoint(first)).normalize();
        addSegment(scene, vectorFromPoint(first).clone().addScaledVector(direction, -10), vectorFromPoint(second).clone().addScaledVector(direction, 10));
      }
    }
    if (object.type === "vector3d") addArrow(scene, new THREE.Vector3(...object.from), new THREE.Vector3(...object.to));
    if (object.type === "triangle3d" || object.type === "polygon3d") {
      const vertices = object.vertices.map((id) => points.get(id)).filter(Boolean).map(vectorFromPoint);
      if (vertices.length >= 3) {
        const geometry = new THREE.BufferGeometry().setFromPoints([...vertices, vertices[0]]);
        const line = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: COLORS.ink }));
        scene.add(line);
        if (vertices.length === 3) {
          const face = new THREE.Mesh(new THREE.BufferGeometry().setFromPoints(vertices), new THREE.MeshBasicMaterial({ color: COLORS.sage, transparent: true, opacity: 0.25, side: THREE.DoubleSide }));
          scene.add(face);
        }
      }
    }
    if (object.type === "plane" && object.points?.length >= 3) {
      const vertices = object.points.slice(0, 3).map(vectorFromPoint);
      const geometry = new THREE.BufferGeometry().setFromPoints([vertices[0], vertices[1], vertices[2], vertices[0]]);
      scene.add(new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: COLORS.sage })));
    }
    if (object.type === "cuboid") {
      const [x, y, z] = object.origin || [0, 0, 0];
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(object.width, object.height, object.depth), new THREE.MeshBasicMaterial({ color: COLORS.sage, transparent: true, opacity: 0.16, wireframe: true }));
      mesh.position.set(x + object.width / 2, y + object.height / 2, z + object.depth / 2);
      scene.add(mesh);
    }
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
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    const labels = new CSS2DRenderer();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    labels.setPixelRatio?.(Math.min(window.devicePixelRatio || 1, 2));
    mount.append(renderer.domElement, labels.domElement);
    labels.domElement.className = "three-label-layer";
    const controls = new OrbitControls(camera, labels.domElement);
    controls.enableDamping = true;
    const group = new THREE.Group();
    scene.add(group);
    scene.add(new THREE.AxesHelper(2));
    scene.add(new THREE.GridHelper(6, 12, COLORS.grid, COLORS.grid));
    renderObjects(group, visualization.objects || []);
    const framing = boundsFor(visualization.objects || []);
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
    return () => { cancelAnimationFrame(frame); observer.disconnect(); controls.dispose(); renderer.dispose(); mount.replaceChildren(); scene.traverse((object) => { object.geometry?.dispose?.(); object.material?.dispose?.(); }); };
  }, [visualization]);

  function resetView() { const state = sceneRef.current; const initial = initialRef.current; if (!state || !initial) return; state.camera.position.copy(initial.position); state.controls.target.copy(initial.target); state.controls.update(); }

  if (!visualization || visualization.dimension !== "3d") return <div className="visualization-empty">This 3-D visualization is not available yet.</div>;
  return <div className="visualization-shell three-shell"><div className="visualization-toolbar"><span>Interactive 3D view</span><button type="button" onClick={resetView} aria-label="Reset 3D view">Reset</button></div><div ref={mountRef} className="three-frame" role="img" aria-label="Interactive 3D geometry diagram" /></div>;
}
