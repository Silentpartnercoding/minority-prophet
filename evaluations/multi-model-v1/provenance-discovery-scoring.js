function pairs(rootByDocument) {
  const ids = Object.keys(rootByDocument).sort();
  const values = new Set();
  for (let i = 0; i < ids.length; i += 1) for (let j = i + 1; j < ids.length; j += 1) if (rootByDocument[ids[i]] === rootByDocument[ids[j]]) values.add(`${ids[i]}|${ids[j]}`);
  return values;
}

export function scoreProvenance(world, inferredRootByDocument) {
  const truth = pairs(world.hidden.root_by_document);
  const inferred = pairs(inferredRootByDocument);
  const tp = [...inferred].filter((pair) => truth.has(pair)).length;
  const fp = inferred.size - tp;
  const fn = truth.size - tp;
  const precision = tp / Math.max(1, tp + fp);
  const recall = tp / Math.max(1, tp + fn);
  return {
    pairwise_true_positive: tp, pairwise_false_positive: fp, pairwise_false_negative: fn,
    pairwise_precision: precision, pairwise_recall: recall,
    pairwise_f1: precision + recall ? 2 * precision * recall / (precision + recall) : 0,
    true_root_count: new Set(Object.values(world.hidden.root_by_document)).size,
    inferred_root_count: new Set(Object.values(inferredRootByDocument)).size
  };
}

export function normalizedLlmInference(world, response) {
  const ids = new Set(world.documents.map((document) => document.document_id));
  const rootByDocument = {};
  for (const group of response.root_groups ?? []) {
    const members = (group.document_ids ?? []).filter((id) => ids.has(id));
    if (!members.length) continue;
    const canonical = [...members].sort()[0];
    for (const id of members) if (!(id in rootByDocument)) rootByDocument[id] = canonical;
  }
  for (const id of ids) rootByDocument[id] ??= id;
  return rootByDocument;
}
