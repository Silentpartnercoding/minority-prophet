export type Lane = "A" | "B" | "C" | "STANDARD";

export type TournamentRow = {
  name: string;
  provider: string;
  lane: Lane;
  correct: number;
  rawCorrect?: number;
  exact: number;
  rawExact?: number;
  invalidTrials: number;
  timeMs: number;
  inputTokens?: number;
  outputTokens?: number;
  toolCalls: number;
  cost?: number;
};

export const paperUrl = "https://github.com/Silentpartnercoding/minority-prophet/blob/main/papers/00-CURRENT-PAPER.md";

export const tournamentRows: TournamentRow[] = [
  { name: "Minority Prophet", provider: "Canonical v1", lane: "C", correct: 128, exact: 8, invalidTrials: 0, timeMs: 18.7, inputTokens: 0, outputTokens: 0, toolCalls: 0, cost: 0 },
  { name: "Claude Opus 5", provider: "Anthropic / Claude Code", lane: "A", correct: 106, exact: 6, invalidTrials: 0, timeMs: 478_018, inputTokens: 326_569, outputTokens: 41_681, toolCalls: 0, cost: 3.2534465 },
  { name: "Claude Opus 5", provider: "Anthropic / Claude Code", lane: "B", correct: 0, rawCorrect: 96, exact: 0, rawExact: 6, invalidTrials: 8, timeMs: 364_977, inputTokens: 1_489_495, outputTokens: 19_965, toolCalls: 35, cost: 4.315915 },
  { name: "Claude Sonnet 5", provider: "Anthropic / Claude Code", lane: "A", correct: 23, exact: 0, invalidTrials: 0, timeMs: 809_652, inputTokens: 639_869, outputTokens: 82_258, toolCalls: 0, cost: 3.4657121 },
  { name: "Claude Sonnet 5", provider: "Anthropic / Claude Code", lane: "B", correct: 32, rawCorrect: 74, exact: 2, rawExact: 4, invalidTrials: 5, timeMs: 1_609_078, inputTokens: 2_431_595, outputTokens: 199_228, toolCalls: 27, cost: 6.4535862 },
  { name: "Claude Haiku 4.5", provider: "Anthropic / Claude Code", lane: "A", correct: 0, exact: 0, invalidTrials: 0, timeMs: 1_058_605, inputTokens: 218_476, outputTokens: 98_985, toolCalls: 0, cost: 1.146448 },
  { name: "Claude Haiku 4.5", provider: "Anthropic / Claude Code", lane: "B", correct: 0, rawCorrect: 10, exact: 0, rawExact: 0, invalidTrials: 8, timeMs: 2_154_859, inputTokens: 3_145_023, outputTokens: 145_142, toolCalls: 59, cost: 1.9173406 },
  { name: "GPT-5.6 Terra", provider: "OpenAI / Codex", lane: "A", correct: 116, exact: 5, invalidTrials: 0, timeMs: 365_015, inputTokens: 300_475, outputTokens: 16_746, toolCalls: 0, cost: 0.8900575 },
  { name: "GPT-5.6 Sol", provider: "OpenAI / Codex", lane: "A", correct: 102, exact: 5, invalidTrials: 0, timeMs: 512_249, inputTokens: 300_694, outputTokens: 25_952, toolCalls: 0, cost: 2.237102 },
  { name: "Cluster vote", provider: "Conventional baseline", lane: "STANDARD", correct: 96, exact: 6, invalidTrials: 0, timeMs: 9.5, inputTokens: 0, outputTokens: 0, toolCalls: 0, cost: 0 },
  { name: "GPT-5.6 Sol", provider: "OpenAI / Codex", lane: "B", correct: 69, exact: 4, invalidTrials: 0, timeMs: 351_070, inputTokens: 1_101_609, outputTokens: 12_559, toolCalls: 19, cost: 2.418447 },
  { name: "GPT-5.6 Terra", provider: "OpenAI / Codex", lane: "B", correct: 68, exact: 4, invalidTrials: 0, timeMs: 245_782, inputTokens: 1_097_326, outputTokens: 9_151, toolCalls: 18, cost: 1.021252 },
  { name: "GPT-5.6 Luna", provider: "OpenAI / Codex", lane: "B", correct: 35, exact: 2, invalidTrials: 0, timeMs: 496_317, inputTokens: 1_933_985, outputTokens: 20_412, toolCalls: 41, cost: 0.8089608 },
  { name: "GPT-5.6 Luna", provider: "OpenAI / Codex", lane: "A", correct: 16, exact: 1, invalidTrials: 0, timeMs: 296_033, inputTokens: 289_024, outputTokens: 13_697, toolCalls: 0, cost: 0.371206 },
];

export const laneDetails = [
  { lane: "A", title: "AI reasons alone", copy: "The model receives the complete raw packet inline. Shell, files, web, retrieval, and every other tool are disabled." },
  { lane: "B", title: "The same AI may use tools", copy: "The same model receives the identical packet. It may choose shell, scripts, packages, or web tools. It is not told to use Minority Prophet." },
  { lane: "C", title: "Canonical Minority Prophet", copy: "The same raw packet enters deterministic code. It derives origins by following parent links, counts distinct roots, and abstains on exact ties." },
];

export const formatTime = (timeMs: number) => {
  if (timeMs < 1000) return `${timeMs.toFixed(1)} ms`;
  if (timeMs < 60_000) return `${(timeMs / 1000).toFixed(1)} s`;
  return `${(timeMs / 60_000).toFixed(1)} min`;
};

export const formatTokens = (value = 0) => value === 0 ? "0" : value.toLocaleString("en-US");
export const laneLabel = (lane: Lane) => lane === "STANDARD" ? "Standard" : `Lane ${lane}`;
