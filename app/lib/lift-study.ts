export type LiftModel = {
  name: string;
  provider: string;
  baseline: number;
  provenance: number;
  minorityProphet: number;
  provenanceGain: number;
  mpGain: number;
  pairedP: number;
  improvements: number;
  regressions: number;
};

export const liftModels: LiftModel[] = [
  { name: "GPT-5.6 Sol", provider: "OpenAI Codex CLI", baseline: 12.5, provenance: 68.75, minorityProphet: 96.875, provenanceGain: 56.25, mpGain: 28.125, pairedP: 0.003906, improvements: 9, regressions: 0 },
  { name: "Claude Sonnet 5", provider: "Anthropic Claude CLI", baseline: 3.125, provenance: 68.75, minorityProphet: 90.625, provenanceGain: 65.625, mpGain: 21.875, pairedP: 0.015625, improvements: 7, regressions: 0 },
];

export const liftStudy = {
  worlds: 32,
  conditions: 3,
  models: 2,
  trials: 192,
  failures: 0,
  parseFailures: 0,
  manifest: "sha256:7bf6d393e59ce6fbc78ca41bda4f71b5a0c29dc95d2b535bb19901c345bf3943",
  report: "sha256:396a3330d2368804e7bdb79ba7d3e028dea80573c13693bb8b94c06c83719c98",
  protocolCommit: "0b7291015d78897474eb3d8ad6a3c093df9f5c4f",
};

export const formatPercent = (value: number) => `${Number.isInteger(value) ? value : value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "")}%`;
