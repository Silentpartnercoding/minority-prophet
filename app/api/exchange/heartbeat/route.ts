import { evaluateWorkingRoute, sampleRouteQuery, sampleRouteRecords } from "../../../../exchange/knowledge-exchange-v0.1/working-route.mjs";

export async function GET() {
  const assessment = evaluateWorkingRoute(sampleRouteRecords, sampleRouteQuery, "2026-08-15T19:00:00.000Z");
  return Response.json({
    mode: "synthetic-local-reference",
    schema: "minority-prophet.witness-exchange-heartbeat.v0.2",
    missionFeed: [{
      missionId: "working-route-github-mcp",
      toolId: sampleRouteQuery.toolId,
      clientId: sampleRouteQuery.clientId,
      operation: sampleRouteQuery.operation,
      status: assessment.status,
      recordedIndependentRoots: assessment.evidence.recordedIndependentRoots,
      copiesCollapsed: assessment.evidence.copiesCollapsed,
    }],
    contributionOpportunities: [{
      kind: "working-route",
      missingCell: "Recent independent public-tool compatibility run",
      arbitraryExecutionAuthorized: false,
    }],
    authorityGranted: false,
    networkCallsPerformed: false,
  });
}
