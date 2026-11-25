import { expect, it } from "vitest";

import { AGENT_TYPES } from "./index";

it("AGENT_TYPES lists the seven agents in workflow order", () => {
  expect(AGENT_TYPES).toEqual([
    "fundamental_analyst",
    "market_analyst",
    "news_sentiment_analyst",
    "geopolitical_analyst",
    "risk_analyst",
    "compliance_analyst",
    "portfolio_manager",
  ]);
});
