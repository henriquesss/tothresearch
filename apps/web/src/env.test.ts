// @vitest-environment node
import { readFileSync } from "node:fs";
import { fileURLToPath, URL } from "node:url";
import type { ProxyOptions } from "vite";
import { afterEach, expect, it, vi } from "vitest";

import viteConfig from "../vite.config";

const ENV_EXAMPLE = fileURLToPath(new URL("../../../.env.example", import.meta.url));

function resolveConfig() {
  if (typeof viteConfig !== "function") throw new Error("vite.config.ts must export a function");
  return viteConfig({ command: "serve", mode: "development" });
}

afterEach(() => {
  vi.unstubAllEnvs();
});

it("exposes only VITE_ variables and no secrets", () => {
  expect(resolveConfig().envPrefix).toBe("VITE_");

  const names = readFileSync(ENV_EXAMPLE, "utf8")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#") && line.includes("="))
    .map((line) => line.slice(0, line.indexOf("=")).trim());
  expect(names).toContain("DATABASE_URL");
  const exposedSecrets = names.filter(
    (name) => name.startsWith("VITE_") && /KEY|SECRET|TOKEN/.test(name),
  );
  expect(exposedSecrets).toEqual([]);
});

it("proxies /api to the configured target", () => {
  vi.stubEnv("API_PROXY_TARGET", undefined);
  const defaultProxy = resolveConfig().server?.proxy?.["/api"] as ProxyOptions;
  expect(defaultProxy.target).toBe("http://localhost:8000");

  vi.stubEnv("API_PROXY_TARGET", "http://api:8000");
  const composeProxy = resolveConfig().server?.proxy?.["/api"] as ProxyOptions;
  expect(composeProxy.target).toBe("http://api:8000");
});
