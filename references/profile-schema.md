# Profile Schema

## Design Principles

- A profile is a dated working model, not a verdict.
- Evidence and interpretation are stored separately.
- A missing observation stays `unknown`; it is not converted into a low score.
- Confidence describes the evidence, not the person's worth or potential.
- Contradictions are represented, not averaged away.
- There is no overall score, rank, type, diagnosis, or probability of success.

## Scales

### Micro

Attention, habits, reactions, preferences, energy patterns, recurring friction,
and small behavioral loops.

### Meso

Capabilities, skills, roles, collaboration, output quality, learning methods,
and project-level behavior.

### Macro

Enacted values, motivations, identity narratives, long-term direction, and
non-negotiable boundaries.

### Temporal

Continuity, change, turning points, momentum, recurring cycles, and the
relationship between earlier and current behavior.

### Contextual

Environments, constraints, resources, incentives, relationships, and the
conditions under which behavior changes.

## Evidence Types

| Code | Type | Meaning |
|---|---|---|
| `self_report` | Self-report | What the subject says about themselves |
| `artifact` | Artifact | Work, writing, code, recordings, or other output |
| `third_party` | Third-party | Authorized feedback from another person |
| `observation` | Observation | Behavior directly visible in the current interaction |
| `public_record` | Public record | Publicly available and relevant information |
| `inference` | Inference | A model interpretation derived from other evidence |

Inferences do not count as independent evidence.

## Confidence

- `high`: multiple independent, specific, recent pieces of evidence agree.
- `medium`: at least one strong source and no strong contradiction.
- `low`: limited, indirect, stale, or highly context-dependent evidence.

Confidence must be absent or `unknown` when evidence is missing.

## Required JSON Shape

See [../assets/profile-template.json](../assets/profile-template.json) for a
complete synthetic example.

Top-level fields:

- `schema_version`
- `profile_id`
- `subject`
- `created_at`
- `updated_at`
- `status`
- `consent`
- `scales`
- `evidence`
- `contradictions`
- `development_targets`
- `revision_history`

Each scale entry contains:

- `summary`
- `evidence_ids`
- `confidence`
- `unknowns`
- `interpretation`

Each evidence record contains:

- `id`
- `type`
- `captured_at`
- `summary`
- `reliability`
- `sensitive`
- optional `quote`
- optional `context`

## Update Rules

1. Create a new `profile_id` or incremented version for each snapshot.
2. Preserve the prior file.
3. Add new evidence instead of editing old evidence in place.
4. Record what changed and why in `revision_history`.
5. Mark conclusions as `confirmed`, `weakened`, `contradicted`, or `unknown`.
6. Keep development targets small, observable, and revisable.

## Prohibited Fields and Uses

Do not add:

- `overall_score`, `personality_score`, `potential_score`, or similar;
- trait probabilities;
- diagnoses;
- protected-trait inferences;
- suitability ratings for jobs, schools, credit, insurance, or clinical care;
- a hidden weighting that converts the scales into a single judgment.
