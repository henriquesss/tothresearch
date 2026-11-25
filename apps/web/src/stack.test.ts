// @vitest-environment node
import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";
import { expect, it } from "vitest";

const PACKAGE_JSON = fileURLToPath(new URL("../package.json", import.meta.url));

it("depends on the PRD frontend stack and the shared workspace package", () => {
  const pkg = JSON.parse(readFileSync(PACKAGE_JSON, "utf8")) as {
    dependencies?: Record<string, string>;
    devDependencies?: Record<string, string>;
  };
  const deps = { ...pkg.dependencies, ...pkg.devDependencies };
  for (const name of ["react", "react-router", "@tanstack/react-query", "tailwindcss"]) {
    expect(deps, name).toHaveProperty(name);
  }
  expect(pkg.dependencies?.["@toth/shared"]).toBe("workspace:*");
});
