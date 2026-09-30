CREATE TABLE IF NOT EXISTS openid_aiim_ck_capture (
  run_id TEXT NOT NULL,
  seq INTEGER NOT NULL CHECK(seq >= 0),
  at TEXT NOT NULL,
  record_json TEXT NOT NULL CHECK(json_valid(record_json)),
  PRIMARY KEY (run_id, seq)
);

CREATE INDEX IF NOT EXISTS idx_openid_aiim_ck_capture_at
ON openid_aiim_ck_capture(at);
