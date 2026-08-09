# Research lifecycle records

Add one JSON file per newly enrolled experiment or imported result. Use the
schema in `research/integrity/research-record.schema.json`.

Keep files flat. If an identifier contains `/`, replace each slash with `--` in
the filename; for example, `LIR-5/PHEME` uses `LIR-5--PHEME.json`.

Do not edit a `canonical` or `imported` record in place. Corrections and
remediations receive a new identifier and record so the prior outcome remains
visible.
