import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { expect, it } from "vitest";

import App from "./App";

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

it("renders the Toth Research heading on /", () => {
  renderAt("/");
  expect(screen.getByRole("heading", { name: "Toth Research" })).toBeInTheDocument();
});

it("renders Page not found on an unknown path", () => {
  renderAt("/nope");
  expect(screen.getByText("Page not found")).toBeInTheDocument();
  expect(screen.getByRole("link")).toHaveAttribute("href", "/");
  expect(screen.queryByRole("heading", { name: "Toth Research" })).not.toBeInTheDocument();
});

it("not-found link navigates home", async () => {
  const user = userEvent.setup();
  renderAt("/nope");
  await user.click(screen.getByRole("link"));
  expect(screen.getByRole("heading", { name: "Toth Research" })).toBeInTheDocument();
  expect(screen.queryByText("Page not found")).not.toBeInTheDocument();
});

it("renders a shadcn button on /", () => {
  renderAt("/");
  expect(screen.getByRole("button")).toHaveAttribute("data-slot", "button");
  expect(screen.getByText("7 specialized agents")).toBeInTheDocument();
});
