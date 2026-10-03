import { sql } from "drizzle-orm";
import { check, index, primaryKey, sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

// Sites applies this add-only D1 migration before the capture Worker is uploaded.
// Existing exchange tables remain under db/schema.mjs and are not migrated here.
export const openidAiimCkCapture = sqliteTable("openid_aiim_ck_capture", {
  runId: text("run_id").notNull(),
  seq: integer("seq").notNull(),
  at: text("at").notNull(),
  recordJson: text("record_json").notNull(),
}, (table) => [
  primaryKey({ columns: [table.runId, table.seq] }),
  check("openid_aiim_ck_capture_seq_nonnegative", sql`${table.seq} >= 0`),
  check("openid_aiim_ck_capture_record_json_valid", sql`json_valid(${table.recordJson})`),
  index("idx_openid_aiim_ck_capture_at").on(table.at),
]);

export const openidAiimDescopeCapture = sqliteTable("openid_aiim_descope_capture", {
  runId: text("run_id").notNull(),
  seq: integer("seq").notNull(),
  at: text("at").notNull(),
  recordJson: text("record_json").notNull(),
}, (table) => [
  primaryKey({ columns: [table.runId, table.seq] }),
  check("openid_aiim_descope_capture_seq_nonnegative", sql`${table.seq} >= 0`),
  check("openid_aiim_descope_capture_record_json_valid", sql`json_valid(${table.recordJson})`),
  index("idx_openid_aiim_descope_capture_at").on(table.at),
]);
