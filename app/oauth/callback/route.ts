const relayOrigin = "https://garden-broken-organization-opposite.trycloudflare.com";

export async function GET(request: Request) {
  const incoming = new URL(request.url);
  const target = new URL("/oauth/callback", relayOrigin);
  target.search = incoming.search;

  return new Response(null, {
    status: 307,
    headers: {
      Location: target.toString(),
      "Cache-Control": "no-store",
      "Referrer-Policy": "no-referrer",
    },
  });
}
