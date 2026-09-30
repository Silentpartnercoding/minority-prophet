CREATE TABLE `openid_aiim_ck_capture` (
	`run_id` text NOT NULL,
	`seq` integer NOT NULL,
	`at` text NOT NULL,
	`record_json` text NOT NULL,
	PRIMARY KEY(`run_id`, `seq`),
	CONSTRAINT "openid_aiim_ck_capture_seq_nonnegative" CHECK("openid_aiim_ck_capture"."seq" >= 0),
	CONSTRAINT "openid_aiim_ck_capture_record_json_valid" CHECK(json_valid("openid_aiim_ck_capture"."record_json"))
);
--> statement-breakpoint
CREATE INDEX `idx_openid_aiim_ck_capture_at` ON `openid_aiim_ck_capture` (`at`);