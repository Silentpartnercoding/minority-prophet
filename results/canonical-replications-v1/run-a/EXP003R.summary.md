# EXP003 replica -- summary

| adversary | lineage | aggregator | acc | minority-recovery | brier | abstain |
|---|---|---|---|---|---|---|
| composed | declared | majority | 0.405 | 0.000 | 0.467 | 0.000 |
| composed | declared | competence | 0.503 | 0.130 | 0.211 | 0.055 |
| composed | declared | evidence_root | 0.990 | 0.983 | 0.047 | 0.000 |
| composed | inferred | majority | 0.405 | 0.000 | 0.467 | 0.000 |
| composed | inferred | competence | 0.503 | 0.130 | 0.211 | 0.055 |
| composed | inferred | evidence_root | 0.511 | 0.119 | 0.195 | 0.090 |
| composed | none | majority | 0.405 | 0.000 | 0.467 | 0.000 |
| composed | none | competence | 0.503 | 0.130 | 0.211 | 0.055 |
| composed | none | evidence_root | 0.405 | 0.000 | 0.467 | 0.000 |
| false_citation | declared | majority | 0.365 | 0.000 | 0.498 | 0.000 |
| false_citation | declared | competence | 0.503 | 0.173 | 0.228 | 0.085 |
| false_citation | declared | evidence_root | 0.990 | 0.984 | 0.049 | 0.000 |
| false_citation | inferred | majority | 0.365 | 0.000 | 0.498 | 0.000 |
| false_citation | inferred | competence | 0.503 | 0.173 | 0.228 | 0.085 |
| false_citation | inferred | evidence_root | 0.990 | 0.984 | 0.050 | 0.000 |
| false_citation | none | majority | 0.365 | 0.000 | 0.498 | 0.000 |
| false_citation | none | competence | 0.503 | 0.173 | 0.228 | 0.085 |
| false_citation | none | evidence_root | 0.365 | 0.000 | 0.498 | 0.000 |
| none | declared | majority | 0.390 | 0.000 | 0.478 | 0.000 |
| none | declared | competence | 0.497 | 0.138 | 0.222 | 0.065 |
| none | declared | evidence_root | 0.975 | 0.959 | 0.050 | 0.000 |
| none | inferred | majority | 0.390 | 0.000 | 0.478 | 0.000 |
| none | inferred | competence | 0.497 | 0.138 | 0.222 | 0.065 |
| none | inferred | evidence_root | 0.975 | 0.959 | 0.051 | 0.005 |
| none | none | majority | 0.390 | 0.000 | 0.478 | 0.000 |
| none | none | competence | 0.497 | 0.138 | 0.222 | 0.065 |
| none | none | evidence_root | 0.390 | 0.000 | 0.478 | 0.000 |
| paraphrase | declared | majority | 0.410 | 0.000 | 0.464 | 0.000 |
| paraphrase | declared | competence | 0.516 | 0.127 | 0.218 | 0.080 |
| paraphrase | declared | evidence_root | 0.980 | 0.975 | 0.050 | 0.000 |
| paraphrase | inferred | majority | 0.410 | 0.000 | 0.464 | 0.000 |
| paraphrase | inferred | competence | 0.516 | 0.127 | 0.218 | 0.080 |
| paraphrase | inferred | evidence_root | 0.980 | 0.975 | 0.050 | 0.000 |
| paraphrase | none | majority | 0.410 | 0.000 | 0.464 | 0.000 |
| paraphrase | none | competence | 0.516 | 0.127 | 0.218 | 0.080 |
| paraphrase | none | evidence_root | 0.410 | 0.000 | 0.464 | 0.000 |
| sybil | declared | majority | 0.340 | 0.000 | 0.518 | 0.000 |
| sybil | declared | competence | 0.503 | 0.193 | 0.231 | 0.115 |
| sybil | declared | evidence_root | 0.985 | 0.977 | 0.052 | 0.000 |
| sybil | inferred | majority | 0.340 | 0.000 | 0.518 | 0.000 |
| sybil | inferred | competence | 0.503 | 0.193 | 0.231 | 0.115 |
| sybil | inferred | evidence_root | 0.942 | 0.911 | 0.101 | 0.045 |
| sybil | none | majority | 0.340 | 0.000 | 0.518 | 0.000 |
| sybil | none | competence | 0.503 | 0.193 | 0.231 | 0.115 |
| sybil | none | evidence_root | 0.340 | 0.000 | 0.518 | 0.000 |
| timing | declared | majority | 0.390 | 0.000 | 0.478 | 0.000 |
| timing | declared | competence | 0.497 | 0.138 | 0.222 | 0.065 |
| timing | declared | evidence_root | 0.975 | 0.959 | 0.050 | 0.000 |
| timing | inferred | majority | 0.390 | 0.000 | 0.478 | 0.000 |
| timing | inferred | competence | 0.497 | 0.138 | 0.222 | 0.065 |
| timing | inferred | evidence_root | 0.980 | 0.967 | 0.050 | 0.010 |
| timing | none | majority | 0.390 | 0.000 | 0.478 | 0.000 |
| timing | none | competence | 0.497 | 0.138 | 0.222 | 0.065 |
| timing | none | evidence_root | 0.390 | 0.000 | 0.478 | 0.000 |

## Lineage inference quality

| adversary | precision | recall | F1 | root-set acc |
|---|---|---|---|---|
| none | 0.998 | 1.000 | 0.999 | 0.991 |
| paraphrase | 0.999 | 1.000 | 0.999 | 0.994 |
| false_citation | 0.865 | 0.866 | 0.865 | 0.991 |
| sybil | 0.550 | 0.529 | 0.539 | 0.829 |
| timing | 0.995 | 1.000 | 0.998 | 0.972 |
| composed | 0.331 | 0.314 | 0.322 | 0.769 |
