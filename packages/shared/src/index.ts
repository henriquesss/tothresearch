/** The seven agent ids, in the order the analysis workflow runs them. */
export const AGENT_TYPES = [
  "fundamental_analyst",
  "market_analyst",
  "news_sentiment_analyst",
  "geopolitical_analyst",
  "risk_analyst",
  "compliance_analyst",
  "portfolio_manager",
] as const;

export type AgentType = (typeof AGENT_TYPES)[number];
