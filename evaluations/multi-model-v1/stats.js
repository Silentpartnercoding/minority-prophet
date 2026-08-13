const round = (value) => Number(value.toFixed(6));
const mean = (values) => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;

export function wilsonInterval(successes, trials, z = 1.959964) {
  if (!trials) return { low: null, high: null };
  const p = successes / trials;
  const denominator = 1 + z ** 2 / trials;
  const center = (p + z ** 2 / (2 * trials)) / denominator;
  const margin = z * Math.sqrt((p * (1 - p) + z ** 2 / (4 * trials)) / trials) / denominator;
  return { low: round(Math.max(0, center - margin)), high: round(Math.min(1, center + margin)) };
}

function binomialTwoSided(successes, total) {
  if (!total) return 1;
  const choose = (n, k) => { let value = 1; for (let index = 1; index <= k; index += 1) value = value * (n - index + 1) / index; return value; };
  const tail = Array.from({ length: Math.min(successes, total - successes) + 1 }, (_, k) => choose(total, k) * 0.5 ** total).reduce((a, b) => a + b, 0);
  return Math.min(1, 2 * tail);
}

export function pairedGain(fromItems, toItems) {
  const from = new Map(fromItems.filter((item) => item.eligible).map((item) => [item.world_id, item]));
  const pairs = toItems.filter((item) => item.eligible && from.has(item.world_id)).map((item) => [from.get(item.world_id), item]);
  const differences = pairs.map(([a, b]) => Number(b.correct) - Number(a.correct));
  const gain = mean(differences) ?? 0;
  const variance = differences.length > 1 ? differences.reduce((sum, value) => sum + (value - gain) ** 2, 0) / (differences.length - 1) : 0;
  const margin = differences.length ? 1.959964 * Math.sqrt(variance / differences.length) : 0;
  const discordant = pairs.filter(([a, b]) => a.correct !== b.correct);
  const improvements = discordant.filter(([a, b]) => !a.correct && b.correct).length;
  return { gain: round(gain), pairs: pairs.length, confidence_interval_95: { low: round(Math.max(-1, gain - margin)), high: round(Math.min(1, gain + margin)) }, p_value: round(binomialTwoSided(improvements, discordant.length)) };
}
