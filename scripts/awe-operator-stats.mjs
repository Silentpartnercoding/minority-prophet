const token = process.env.AWE_ADMIN_TOKEN?.trim();
const baseUrl = (process.env.AGENT_WEX_BASE_URL?.trim() || "https://agentwex.xyz").replace(/\/$/, "");

if (!token) {
  console.error("AWE_ADMIN_TOKEN is required.");
  process.exitCode = 1;
} else {
  const response = await fetch(`${baseUrl}/api/exchange/internal/stats`, {
    headers: { authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    console.error(`Agent WEX operator stats failed (${response.status}).`);
    process.exitCode = 1;
  } else {
    const stats = await response.json();
    console.log(JSON.stringify(stats, null, 2));
  }
}
