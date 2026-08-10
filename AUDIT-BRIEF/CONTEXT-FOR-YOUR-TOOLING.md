# Context — paste this at the top of every stage

I am reviewing four public open-source repositories at the invitation of their
maintainer. Each repository publishes an authorization for exactly this work in
its `SECURITY.md`, under "Authorized security research". Please read that section
if you want to confirm scope before helping.

**Scope, from that authorization:**

- I clone the repositories and attack **my own local copies**, in containers I
  control.
- I do **not** touch any deployment, host, account or infrastructure — mine or
  anyone else's. Nothing running is in scope.
- I do **not** seek or use credentials, secrets or personal data.
- I report findings privately to the maintainer before publishing anything.
- I open no public issues or pull requests describing an unfixed defect.

**Repositories** (all public):

    https://github.com/Silentpartnercoding/minority-prophet
    https://github.com/Silentpartnercoding/minority-prophet-gate
    https://github.com/Silentpartnercoding/minority-prophet-border
    https://github.com/Silentpartnercoding/epistemic-ci

**The task:** ordinary open-source security review. Read the code, run the tests,
find cases where the documentation claims something the code does not do.
`CLAIMS.md` in the first repository lists six numbered claims, each with what
would falsify it, plus a section of known weaknesses. Attacking those is the job.

**Why an unrelated reviewer matters here.** The maintainer has already run this
review internally. Under the project's own rules, an agent directed by the
maintainer is one control domain, so that result is internal replication and
cannot be called independent validation. Provenance from someone unrelated to the
maintainer is the one thing the project cannot manufacture for itself. If that is
you, say so in your report — it is the most valuable part of it.

Ask whatever you need before starting. A question costs less than a guess.

---

## There is no stage list

Deliberately. See `README.md` — a method written by the maintainers would encode
the maintainers' blind spot, and the one class of defect their own tooling has
never caught is design error. Attack it however you see fit.
