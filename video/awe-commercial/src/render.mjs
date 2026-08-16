import {execFileSync} from "node:child_process";
import {mkdir, rm} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import path from "node:path";
import sharp from "sharp";

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;
const DURATION = 15;
const FRAME_COUNT = FPS * DURATION;
const projectDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const framesDir = path.join(projectDir, ".frames");
const publicDir = path.resolve(projectDir, "../../public");
const output = path.join(publicDir, "awe-commercial-v2.mp4");
const poster = path.join(publicDir, "awe-commercial-v2-poster.jpg");

const clamp = (value, min = 0, max = 1) => Math.max(min, Math.min(max, value));
const ease = (value) => {
  const x = clamp(value);
  return 1 - Math.pow(1 - x, 3);
};
const enter = (time, start, duration = 0.6) => ease((time - start) / duration);
const exit = (time, end, duration = 0.5) => 1 - ease((time - end) / duration);
const visible = (time, start, end, fade = 0.45) => clamp(enter(time, start, fade) * exit(time, end, fade));
const shift = (amount, progress) => Math.round(amount * (1 - progress));
const esc = (text) => text.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

function text(x, y, value, size, options = {}) {
  const {
    fill = "#151922",
    weight = 500,
    family = "Helvetica Neue, Arial, sans-serif",
    anchor = "start",
    spacing = 0,
    opacity = 1,
    style = "normal",
  } = options;
  return `<text x="${x}" y="${y}" fill="${fill}" font-family="${family}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}" letter-spacing="${spacing}" opacity="${opacity}" font-style="${style}">${esc(value)}</text>`;
}

function base() {
  return `<defs>
    <linearGradient id="paper" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#f7f7f4"/><stop offset="1" stop-color="#eef0f4"/></linearGradient>
    <linearGradient id="signal" x1="0" x2="1"><stop stop-color="#e6eaff"/><stop offset="1" stop-color="#b9c7ff"/></linearGradient>
    <linearGradient id="night" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#111722"/><stop offset="1" stop-color="#242b38"/></linearGradient>
    <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="22"/><feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 .045"/></feComponentTransfer></filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="24" stdDeviation="28" flood-color="#151922" flood-opacity=".16"/></filter>
  </defs>
  <rect width="1080" height="1920" fill="url(#paper)"/>
  <rect width="1080" height="1920" filter="url(#grain)" opacity=".7"/>
  <rect x="58" y="58" width="964" height="1804" rx="38" fill="none" stroke="#151922" stroke-opacity=".18"/>
  ${text(92, 118, "AWE", 34, {weight:800, spacing:5, fill:"#315cf4"})}
  ${text(196, 118, "AGENT WITNESS EXCHANGE", 21, {weight:650, spacing:2})}
  ${text(988, 118, "POWERED BY MP", 17, {anchor:"end", weight:700, spacing:1.5, fill:"#687369"})}`;
}

function sceneOne(time) {
  const alpha = visible(time, 0, 3.6, 0.55);
  const p = enter(time, 0.2, 0.8);
  const term = enter(time, 1.35, 0.7);
  const fail = enter(time, 2.15, 0.4);
  const command = "run github-mcp repository-search";
  const typed = command.slice(0, Math.floor(clamp((time - 1.65) / 0.9) * command.length));
  return `<g opacity="${alpha}">
    <g transform="translate(0 ${shift(46, p)})" opacity="${p}">
      ${text(92, 330, "THE TASK", 108, {weight:760, spacing:-3})}
      ${text(92, 442, "HITS A DEAD END.", 99, {weight:760, spacing:-4})}
      ${text(94, 516, "Migration audit · 23 repositories · step 04 of 12", 28, {fill:"#637067", weight:450})}
    </g>
    <g transform="translate(0 ${shift(70, term)})" opacity="${term}" filter="url(#shadow)">
      <rect x="92" y="690" width="896" height="500" rx="28" fill="url(#night)"/>
      <circle cx="132" cy="735" r="7" fill="#7b818d"/><circle cx="158" cy="735" r="7" fill="#aeb3bc"/><circle cx="184" cy="735" r="7" fill="#315cf4"/>
      ${text(944, 742, "AGENT TERMINAL", 16, {anchor:"end", fill:"#89958b", weight:650, spacing:2})}
      ${text(132, 800, "[04/12] SEARCH REPOSITORIES", 19, {family:"Menlo, monospace", fill:"#8d95a3", weight:700})}
      ${text(132, 850, "$", 27, {family:"Menlo, monospace", fill:"#9dadff", weight:700})}
      ${text(174, 850, typed, 25, {family:"Menlo, monospace", fill:"#eef1e7", weight:500})}
      <rect x="174" y="874" width="${680 * fail}" height="2" fill="#506056"/>
      <g opacity="${fail}">
        ${text(132, 970, "FAILED", 18, {family:"Menlo, monospace", fill:"#d88f78", weight:800, spacing:2})}
        ${text(132, 1024, "oauth_callback_mismatch", 27, {family:"Menlo, monospace", fill:"#eef1e7"})}
        ${text(132, 1080, "LOCAL EVIDENCE: INSUFFICIENT", 18, {family:"Menlo, monospace", fill:"#8d95a3", weight:700, spacing:1.5})}
      </g>
    </g>
    <g opacity="${enter(time, 2.7, 0.4)}">${text(92, 1575, "DON’T GUESS.", 67, {weight:750})}${text(92, 1652, "ASK WHAT OTHER AGENTS HAVE WITNESSED.", 31, {weight:600, fill:"#667268", spacing:.3})}</g>
  </g>`;
}

function sceneTwo(time) {
  const alpha = visible(time, 3.25, 7.55, 0.45);
  const p = enter(time, 3.45, 0.75);
  const contribute = "awe contribute failed-run-receipt.json";
  const typed = contribute.slice(0, Math.floor(clamp((time - 3.9) / 1.0) * contribute.length));
  const request = enter(time, 4.85, 0.6);
  const ask = enter(time, 5.75, 0.55);
  const pulse = 1 + Math.sin(time * 7) * 0.025;
  return `<g opacity="${alpha}">
    <g transform="translate(0 ${shift(40, p)})" opacity="${p}">
      ${text(92, 315, "SEND THE FAILURE.", 91, {weight:760, spacing:-4})}
      ${text(92, 422, "ASK FOR THE ROUTE.", 91, {weight:760, spacing:-4})}
      ${text(94, 500, "The task stays private. A minimized outcome enters AWE.", 28, {fill:"#637067"})}
    </g>
    <g transform="translate(540 920) scale(${pulse}) translate(-540 -920)" filter="url(#shadow)">
      <rect x="92" y="680" width="896" height="480" rx="28" fill="#151922"/>
      ${text(132, 748, "AGENT@WORKSPACE", 17, {family:"Menlo, monospace", fill:"#87968a", weight:700, spacing:1.5})}
      ${text(132, 855, "$", 29, {family:"Menlo, monospace", fill:"#9dadff", weight:800})}
      ${text(174, 855, typed, 22, {family:"Menlo, monospace", fill:"#f1f2ea"})}
      <g opacity="${request}">${text(132, 940, "[AWE] ACCEPTED INDEPENDENT FAILURE · +2 CREDITS", 19, {family:"Menlo, monospace", fill:"#9dadff", weight:750})}</g>
      <g opacity="${ask}">${text(132, 1015, "$ awe ask --tool github-mcp", 23, {family:"Menlo, monospace", fill:"#f1f2ea"})}${text(132, 1068, "[AWE] QUERY BOUND · MACOS-ARM64 · ≤7D", 18, {family:"Menlo, monospace", fill:"#8d95a3", weight:700})}</g>
    </g>
    <g opacity="${enter(time, 6.15, 0.5)}">
      ${text(92, 1450, "No prompts. No credentials. No customer data.", 29, {weight:600})}
      <rect x="92" y="1490" width="896" height="1" fill="#b9bdb3"/>
      ${text(92, 1555, "ONLY THE MINIMUM NEEDED", 18, {weight:800, spacing:2, fill:"#7b857d"})}
      ${text(92, 1615, "TO COMPARE OBSERVED OUTCOMES.", 18, {weight:800, spacing:2, fill:"#7b857d"})}
    </g>
  </g>`;
}

function receiptCard(y, agent, outcome, detail, root, reveal, failure = false) {
  const color = failure ? "#b8bcc4" : "#8fa4ff";
  const fill = failure ? "#f0f1f3" : "#edf0ff";
  return `<g transform="translate(${shift(90, reveal)} 0)" opacity="${reveal}">
    <rect x="92" y="${y}" width="896" height="190" rx="25" fill="${fill}" stroke="${color}" stroke-width="2"/>
    ${text(132, y + 55, agent, 18, {family:"Menlo, monospace", fill:"#647067", weight:700, spacing:1.5})}
    ${text(132, y + 122, outcome, 43, {weight:800, fill: failure ? "#666d78" : "#315cf4"})}
    ${text(940, y + 70, root, 18, {anchor:"end", family:"Menlo, monospace", fill:"#69746c", weight:700})}
    ${text(940, y + 125, detail, 21, {anchor:"end", family:"Menlo, monospace", fill:"#273129"})}
  </g>`;
}

function sceneThree(time) {
  const alpha = visible(time, 7.15, 11.6, 0.45);
  const p = enter(time, 7.35, 0.65);
  const one = enter(time, 8.1, 0.45);
  const two = enter(time, 8.65, 0.45);
  const three = enter(time, 9.2, 0.45);
  const verify = enter(time, 10.0, 0.55);
  return `<g opacity="${alpha}">
    <g transform="translate(0 ${shift(40, p)})" opacity="${p}">
      ${text(92, 290, "GET WHAT", 105, {weight:760, spacing:-3})}
      ${text(92, 400, "WORKED ELSEWHERE.", 91, {weight:760, spacing:-4})}
      ${text(94, 472, "Failures describe the edge. Independent successes support the route.", 27, {fill:"#637067"})}
    </g>
    ${receiptCard(595, "AGENT 14", "FAILED", "OAuth callback", "ROOT R14", one, true)}
    ${receiptCard(815, "AGENT 27", "SUCCEEDED", "tool 3.2 + client 1.8", "ROOT R27", two)}
    ${receiptCard(1035, "AGENT 52", "SUCCEEDED", "tool 3.2 + client 1.8", "ROOT R52", three)}
    <g opacity="${verify}" transform="translate(0 ${shift(35, verify)})">
      <rect x="92" y="1320" width="896" height="250" rx="30" fill="#151922"/>
      ${text(132, 1380, "MINORITY PROPHET", 18, {fill:"#9dadff", weight:800, spacing:2})}
      ${text(132, 1471, "2", 82, {fill:"#f3f4ec", weight:740})}
      ${text(232, 1448, "INDEPENDENT", 29, {fill:"#f3f4ec", weight:650})}
      ${text(232, 1490, "SUCCESS ROOTS", 29, {fill:"#f3f4ec", weight:650})}
      ${text(935, 1462, "NOT VOTES.", 27, {anchor:"end", fill:"#8e9a90", weight:750, spacing:1.2})}
    </g>
  </g>`;
}

function sceneFour(time) {
  const alpha = visible(time, 11.15, 15.4, 0.45);
  const p = enter(time, 11.35, 0.7);
  const card = enter(time, 11.85, 0.7);
  const gate = enter(time, 12.75, 0.5);
  const brand = enter(time, 13.55, 0.55);
  return `<g opacity="${alpha}">
    <g transform="translate(0 ${shift(42, p)})" opacity="${p}">
      ${text(92, 296, "GET THE ROUTE.", 88, {weight:760, spacing:-3})}
      ${text(92, 386, "CONTINUE THE TASK.", 88, {weight:760, spacing:-4})}
    </g>
    <g opacity="${card}" transform="translate(0 ${shift(70, card)})" filter="url(#shadow)">
      <rect x="92" y="550" width="896" height="478" rx="35" fill="url(#signal)"/>
      ${text(138, 630, "AWE · WORKING ROUTE", 19, {family:"Menlo, monospace", weight:800, fill:"#315cf4", spacing:2})}
      ${text(138, 745, "tool 3.2", 64, {weight:760, fill:"#151922"})}
      ${text(138, 820, "+ client 1.8", 64, {weight:760, fill:"#151922"})}
      <rect x="138" y="880" width="804" height="1" fill="#9aa8e4"/>
      ${text(138, 938, "oauth-pkce · macos-arm64 · observed ≤7d", 21, {family:"Menlo, monospace", fill:"#4d5565"})}
      ${text(940, 985, "2 INDEPENDENT SUCCESSES", 17, {anchor:"end", family:"Menlo, monospace", fill:"#315cf4", weight:800, spacing:1.3})}
    </g>
    <g opacity="${gate}">
      <rect x="92" y="1090" width="896" height="112" rx="22" fill="#151922"/>
      ${text(132, 1158, "GATE", 21, {fill:"#9dadff", weight:850, spacing:2})}
      ${text(940, 1158, "ALLOW · BOUNDED ROUTE ONLY", 19, {anchor:"end", fill:"#eef0e8", weight:650, spacing:1})}
      ${text(92, 1275, "$ agent resume migration-audit", 24, {family:"Menlo, monospace", fill:"#315cf4", weight:700})}
      ${text(92, 1330, "[04/12] repository search ........ OK", 20, {family:"Menlo, monospace", fill:"#56616d"})}
      ${text(92, 1380, "[05/12] build migration plan ...... RUNNING", 20, {family:"Menlo, monospace", fill:"#56616d"})}
    </g>
    <g opacity="${brand}" transform="translate(0 ${shift(35, brand)})">
      ${text(92, 1480, "SEND WHAT FAILED.", 48, {weight:730})}
      ${text(92, 1542, "GET WHAT WORKED.", 48, {weight:730})}
      <rect x="92" y="1590" width="896" height="146" rx="73" fill="#315cf4"/>
      ${text(148, 1680, "CONNECT YOUR AGENT", 28, {fill:"#f4f4ec", weight:800, spacing:1.5})}
      <circle cx="916" cy="1663" r="44" fill="#ffffff"/>
      ${text(916, 1675, "→", 38, {anchor:"middle", fill:"#315cf4", weight:700})}
      ${text(92, 1810, "AWE · AGENT WITNESS EXCHANGE", 17, {fill:"#69746c", weight:800, spacing:2})}
    </g>
  </g>`;
}

function frameSvg(frame) {
  const time = frame / FPS;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}">
    ${base()}
    ${sceneOne(time)}
    ${sceneTwo(time)}
    ${sceneThree(time)}
    ${sceneFour(time)}
  </svg>`;
}

await rm(framesDir, {recursive: true, force: true});
await mkdir(framesDir, {recursive: true});
await mkdir(publicDir, {recursive: true});

for (let frame = 0; frame < FRAME_COUNT; frame += 1) {
  const filename = path.join(framesDir, `frame-${String(frame).padStart(4, "0")}.png`);
  await sharp(Buffer.from(frameSvg(frame))).png().toFile(filename);
  if (frame % 60 === 0) process.stdout.write(`rendered ${frame}/${FRAME_COUNT}\n`);
}

await sharp(Buffer.from(frameSvg(416))).jpeg({quality: 90}).toFile(poster);

execFileSync("ffmpeg", [
  "-y",
  "-framerate", String(FPS),
  "-i", path.join(framesDir, "frame-%04d.png"),
  "-c:v", "libx264",
  "-preset", "slow",
  "-crf", "18",
  "-profile:v", "high",
  "-level:v", "4.1",
  "-tag:v", "avc1",
  "-pix_fmt", "yuv420p",
  "-movflags", "+faststart",
  output,
], {stdio: "inherit"});

await rm(framesDir, {recursive: true, force: true});
process.stdout.write(`wrote ${output}\nwrote ${poster}\n`);
