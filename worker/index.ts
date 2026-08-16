/** Cloudflare Worker entry point for the vinext-starter template. */
import { handleImageOptimization, DEFAULT_DEVICE_SIZES, DEFAULT_IMAGE_SIZES } from "vinext/server/image-optimization";
import handler from "vinext/server/app-router-entry";
import { handleExchangeApi } from "../db/exchange-api.mjs";

interface Env {
  ASSETS: Fetcher;
  DB: D1Database;
  AWE_VERIFIER_TOKEN?: string;
  IMAGES: {
    input(stream: ReadableStream): {
      transform(options: Record<string, unknown>): {
        output(options: { format: string; quality: number }): Promise<{ response(): Response }>;
      };
    };
  };
}

const aweHosts = new Set(["agentwex.xyz", "www.agentwex.xyz"]);

interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
  passThroughOnException(): void;
}

// Image security config. SVG sources with .svg extension auto-skip the
// optimization endpoint on the client side (served directly, no proxy).
// To route SVGs through the optimizer (with security headers), set
// dangerouslyAllowSVG: true in next.config.js and uncomment below:
// const imageConfig: ImageConfig = { dangerouslyAllowSVG: true };

const worker = {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (["/api/exchange/signup", "/api/exchange/account", "/api/exchange/ledger", "/api/exchange/signing-keys", "/api/exchange/contributions", "/api/exchange/queries", "/api/exchange/working-route-comps", "/api/exchange/bounties", "/api/exchange/unlock", "/api/exchange/internal/accept"].includes(url.pathname)
      || url.pathname.startsWith("/api/exchange/contributions/")
      || url.pathname.startsWith("/api/exchange/queries/")) {
      return handleExchangeApi(request, env.DB, { verifierToken: env.AWE_VERIFIER_TOKEN });
    }

    if (url.pathname === "/_vinext/image") {
      const allowedWidths = [...DEFAULT_DEVICE_SIZES, ...DEFAULT_IMAGE_SIZES];
      return handleImageOptimization(request, {
        fetchAsset: (path) => env.ASSETS.fetch(new Request(new URL(path, request.url))),
        transformImage: async (body, { width, format, quality }) => {
          const result = await env.IMAGES.input(body).transform(width > 0 ? { width } : {}).output({ format, quality });
          return result.response();
        },
      }, allowedWidths);
    }

    if (aweHosts.has(url.hostname) && url.pathname === "/") {
      url.pathname = "/exchange";
      return handler.fetch(new Request(url, request), env, ctx);
    }

    return handler.fetch(request, env, ctx);
  },
};

export default worker;
