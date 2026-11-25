import { render, screen } from "@testing-library/react";
import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createElement } from "react";
import { MemoryRouter } from "react-router";
import { expect, it } from "vitest";

import App from "./App";

const PACKAGE_JSON = resolve(import.meta.dirname, "../package.json");
const COMPONENTS_JSON = resolve(import.meta.dirname, "../components.json");
const BUTTON = resolve(import.meta.dirname, "components/ui/button.tsx");

it("uses the PRD stack and renders a shadcn Button on /", () => {
  const pkg = JSON.parse(readFileSync(PACKAGE_JSON, "utf8")) as {
    dependencies?: Record<string, string>;
    devDependencies?: Record<string, string>;
  };
  const deps = { ...pkg.dependencies, ...pkg.devDependencies };
  for (const name of [
    "react",
    "react-router",
    "@tanstack/react-query",
    "tailwindcss",
    "vite",
    "typescript",
  ]) {
    expect(deps, name).toHaveProperty(name);
  }
  expect(pkg.dependencies?.["@toth/shared"]).toBe("workspace:*");

  const components = JSON.parse(readFileSync(COMPONENTS_JSON, "utf8")) as {
    $schema?: string;
    aliases?: Record<string, string>;
  };
  expect(components.$schema).toBe("https://ui.shadcn.com/schema.json");
  expect(components.aliases?.ui).toBe("@/components/ui");
  expect(existsSync(BUTTON)).toBe(true);

  render(createElement(MemoryRouter, { initialEntries: ["/"] }, createElement(App)));
  expect(screen.getByRole("button")).toHaveAttribute("data-slot", "button");
});
