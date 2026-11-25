import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { expect, it, vi } from "vitest";

import App from "./App";

vi.mock("@toth/shared", () => ({ AGENT_TYPES: ["first", "second", "third"] }));

it("renders the agent count from the shared AGENT_TYPES", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByText("3 specialized agents")).toBeInTheDocument();
});
