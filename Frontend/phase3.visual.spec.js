import { expect, test } from "@playwright/test";

const payload = {
  success: true,
  question: "Point A is at (1, 2, 3) and point B is at (5, 5, 6). Find the distance between A and B.",
  operation: "distance3d",
  operation_label: "3D Distance Between Points",
  result: 5.830951894845301,
  explanation: {
    concept: "Use the three-dimensional distance formula.",
    formula: "d = sqrt((x2-x1)^2+(y2-y1)^2+(z2-z1)^2)",
    steps: ["d = sqrt(34)", "d = 5.83 units"],
    conclusion: "Therefore, the distance is approximately 5.83 units.",
  },
  visualization: {
    dimension: "3d",
    coordinateSystem: true,
    objects: [
      { type: "point3d", id: "A", x: 1, y: 2, z: 3, label: "A" },
      { type: "point3d", id: "B", x: 5, y: 5, z: 6, label: "B" },
      { type: "segment3d", from: "A", to: "B", label: "AB" },
      { type: "vector3d", from: [0, 0, 0], to: [3, 4, 2], label: "v" },
      { type: "triangle3d", vertices: ["A", "B", "C"] },
      { type: "plane", points: [{ id: "A", x: 1, y: 2, z: 3 }, { id: "B", x: 5, y: 5, z: 6 }, { id: "C", x: 2, y: 6, z: 3 }], label: "plane" },
      { type: "cuboid", origin: [0, 0, 0], width: 2, height: 1.5, depth: 1, labels: { width: "w = 2", height: "h = 1.5", depth: "d = 1" } },
      { type: "cylinder", origin: [4, 0, 0], radius: 1, height: 3, label: "Cylinder", labels: { radius: "r = 1", height: "h = 3" } },
      { type: "cone", origin: [-4, 0, 0], radius: 1, height: 3, slantHeight: 3.16, label: "Cone", labels: { radius: "r = 1", height: "h = 3", slantHeight: "l = 3.16" } },
      { type: "unknown3d" },
    ],
  },
};

async function render3D(page, viewport) {
  await page.setViewportSize(viewport);
  await page.route("**/api/solve/", async (route) => route.fulfill({ json: payload }));
  await page.goto("http://127.0.0.1:5173/");
  await page.getByLabel("Geometry question").fill(payload.question);
  await page.getByRole("button", { name: /solve/i }).click();
  await expect(page.locator(".three-frame canvas")).toBeVisible({ timeout: 15000 });
  await expect(page.getByText("A", { exact: true })).toBeVisible();
  await expect(page.getByText("B", { exact: true })).toBeVisible();
  await expect(page.getByText("Cylinder", { exact: true })).toBeVisible();
  await expect(page.getByText("Cone", { exact: true })).toBeVisible();
}

async function sampledPixelsAreNonBlank(page) {
  return page.locator(".three-frame canvas").evaluate((canvas) => {
    const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
    if (!gl || gl.drawingBufferWidth === 0 || gl.drawingBufferHeight === 0) return false;
    const samples = [];
    const xs = [0.25, 0.5, 0.75];
    const ys = [0.25, 0.5, 0.75];
    for (const x of xs) {
      for (const y of ys) {
        const pixel = new Uint8Array(4);
        gl.readPixels(
          Math.floor(gl.drawingBufferWidth * x),
          Math.floor(gl.drawingBufferHeight * y),
          1,
          1,
          gl.RGBA,
          gl.UNSIGNED_BYTE,
          pixel
        );
        samples.push(Array.from(pixel).join(","));
      }
    }
    return new Set(samples).size > 1;
  });
}

test("3D renderer is visible and nonblank on desktop", async ({ page }) => {
  await render3D(page, { width: 1280, height: 850 });
  await page.locator(".three-frame").screenshot({ path: "test-results/phase3-desktop.png", animations: "disabled" });
  expect(await sampledPixelsAreNonBlank(page)).toBe(true);
});

test("3D renderer is visible and nonblank on mobile", async ({ page }) => {
  await render3D(page, { width: 390, height: 844 });
  await page.locator(".three-frame").screenshot({ path: "test-results/phase3-mobile.png", animations: "disabled" });
  expect(await sampledPixelsAreNonBlank(page)).toBe(true);
});
