import { evaluateWorkingRoute, sampleRouteQuery, sampleRouteRecords } from "../../../../exchange/knowledge-exchange-v0.1/working-route.mjs";

export async function GET() {
  return Response.json({
    schema: "minority-prophet.knowledge-exchange-service.v0.1",
    mode: "local-reference",
    accepts: "minority-prophet.working-route-query.v0.1",
    contributionSchema: "minority-prophet.working-route-comp.v0.1",
    storesPayloads: false,
    reciprocity: "give-to-get",
    authorityGranted: false,
  });
}

export async function POST(request: Request) {
  const query = await request.json().catch(() => null);
  if (!query || !query.toolId || !query.clientId || !query.environment || !query.authMode || !query.operation || query.localEvidenceStatus !== "insufficient") {
    return Response.json({ error: "invalid_working_route_query" }, { status: 400 });
  }

  try {
    return Response.json(evaluateWorkingRoute(sampleRouteRecords, {
      ...sampleRouteQuery,
      ...query,
      maxAgeDays: query.maxAgeDays ?? 7,
      minimumIndependentRoots: query.minimumIndependentRoots ?? 2,
    }, "2026-08-15T19:00:00.000Z"));
  } catch {
    return Response.json({ error: "query_could_not_be_assessed" }, { status: 422 });
  }
}
