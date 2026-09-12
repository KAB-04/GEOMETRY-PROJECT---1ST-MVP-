import { expect, test } from "@playwright/test";

const savedResponse = {
  success: true,
  question: "A cylindrical water tank has radius 4 m and height 9 m. Find its volume.",
  operation: "cylinder_volume",
  operation_label: "Cylinder Volume",
  result: 452.3893421169302,
  explanation: {
    concept: "The volume of a cylinder is the area of its circular base multiplied by its height.",
    formula: "V = \\pi r^2h",
    steps: ["V = 144\\pi", "V \\approx 452.39"],
    conclusion: "Therefore, the cylinder's volume is approximately 452.39 cubic meters.",
  },
  visualization: {
    dimension: "3d",
    coordinateSystem: true,
    objects: [{ type: "cylinder", origin: [0, 0, 0], radius: 4, height: 9, label: "Cylinder" }],
  },
};

const topics = [
  {
    id: "cylinders",
    name: "Cylinders",
    category: "Solid Geometry / 3D Geometry",
    dimension: "3d",
    status: "available",
    description: "Right circular cylinder volume and surface area.",
    supported_operations: [{ label: "Volume", operation: "cylinder_volume" }],
    examples: ["A cylindrical water tank has radius 4 m and height 9 m. Find its volume."],
  },
];

for (const viewport of [
  { width: 375, height: 812 },
  { width: 768, height: 900 },
  { width: 1366, height: 900 },
  { width: 1920, height: 1080 },
]) {
  test(`History and Topics work at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.route("**/api/history/", async (route) => {
      if (route.request().method() === "GET") {
        await route.fulfill({
          json: {
            success: true,
            items: [{
              id: 1,
              question: savedResponse.question,
              operation: savedResponse.operation,
              operation_label: savedResponse.operation_label,
              dimension: "3d",
              geometry_type: "cylinder",
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }],
          },
        });
      } else {
        await route.fulfill({ json: { success: true } });
      }
    });
    await page.route("**/api/history/1/", async (route) => route.fulfill({ json: { success: true, item: { id: 1, response: savedResponse } } }));
    await page.route("**/api/topics/", async (route) => route.fulfill({ json: { success: true, topics } }));
    let solveCalls = 0;
    await page.route("**/api/solve/", async (route) => {
      solveCalls += 1;
      await route.fulfill({ json: savedResponse });
    });

    await page.goto("http://127.0.0.1:5173/");
    await expect(page.getByText("soon")).toHaveCount(0);

    await page.getByRole("button", { name: /history/i }).click();
    await expect(page.getByRole("heading", { name: "History" })).toBeVisible();
    await page.getByText(savedResponse.question).click();
    await expect(page.getByText("Cylinder Volume")).toBeVisible();
    expect(solveCalls).toBe(0);

    await page.getByRole("button", { name: /topics/i }).click();
    await expect(page.getByRole("heading", { name: "Topics" })).toBeVisible();
    await page.getByRole("button", { name: /cylinders/i }).click();
    await expect(page.getByText("Right circular cylinder volume and surface area.")).toBeVisible();
    await page.getByRole("button", { name: savedResponse.question }).click();
    await expect(page.getByLabel("Geometry question")).toHaveValue(savedResponse.question);
    expect(solveCalls).toBe(0);
  });
}
