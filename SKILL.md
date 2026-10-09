---
name: personal-multiscale-profile
description: "Build and update an evidence-bounded, multi-scale profile of a consenting person through structured interviews, artifacts, decision histories, and longitudinal check-ins. Use for self-understanding and reflective development, not psychometric testing, diagnosis, ranking, or high-impact decisions."
---

# Personal Multiscale Profile

Create a working model of how a person thinks, acts, develops, and responds to
context. The profile is a dated snapshot, not a fixed identity, diagnosis, or
composite score.

## Operating Boundary

Use this skill only when the subject has asked to be profiled or has explicitly
consented through an authorized process. Do not mine unrelated chats, files,
email, browsing history, or prior conversations. Use only the sources brought
into the current task.

Never use this skill for hiring, promotion, admissions, clinical decisions,
credit, insurance, discipline, ranking, or any other high-impact decision.
Never produce a single "person score" or infer worth, integrity, intelligence,
protected traits, or future performance.

Before collecting sensitive information, read
[references/safety-and-privacy.md](references/safety-and-privacy.md).

## Workflow

1. Establish purpose, subject, time horizon, and permitted data sources.
2. Choose a mode:
   - Baseline: run the six interview rounds and build the first profile.
   - Update: compare new evidence with the latest dated profile.
   - Focused: examine one scale, decision, or question without rebuilding the
     whole profile.
   - Third-party: profile only an authorized subject; label every conclusion
     as an inference from limited evidence.
3. Read [references/interview-protocol.md](references/interview-protocol.md)
   and use [assets/question-bank.json](assets/question-bank.json). Ask a small
   batch at a time. Prefer concrete events over personality adjectives.
4. Record evidence before interpretation. Keep self-report, artifacts,
   third-party feedback, observations, and inferences separate.
5. Synthesize across the five scales in
   [references/profile-schema.md](references/profile-schema.md). Include
   contradictions, missing evidence, and conditions that would change the
   conclusion.
6. Offer a concise synthesis in conversation. Create or update a profile file
   only when the user asks for persistence.
7. For JSON profiles, use
   [assets/profile-template.json](assets/profile-template.json) and run:

   ```bash
   python scripts/validate_profile.py path/to/profile.json
   ```

8. Preserve earlier revisions. Add a dated snapshot for updates instead of
   silently rewriting the past.

## Scales

- Micro: attention, habits, reactions, preferences, recurring friction.
- Meso: capabilities, roles, collaboration, output, and learning patterns.
- Macro: values, motivations, identity narratives, and long-term direction.
- Temporal: continuity, change, turning points, momentum, and recurring loops.
- Contextual: environments, constraints, resources, and conditions for growth.

## Output Rules

- Lead with evidence, then interpretation, then confidence.
- Use `high`, `medium`, or `low` confidence; never imply precision without it.
- Treat absence of evidence as unknown, not as a low score.
- Label an inference as an inference even when it feels intuitive.
- Describe tensions rather than forcing a contradiction into one answer.
- Avoid moralizing, flattery, diagnosis, and deterministic language.
- End an update with 1-3 possible experiments or questions to test next.

## Core Files

- Interview procedure:
  [references/interview-protocol.md](references/interview-protocol.md)
- Profile structure and evidence levels:
  [references/profile-schema.md](references/profile-schema.md)
- Consent, privacy, and safety:
  [references/safety-and-privacy.md](references/safety-and-privacy.md)
- Question bank: [assets/question-bank.json](assets/question-bank.json)
- JSON template: [assets/profile-template.json](assets/profile-template.json)
- Human-readable template:
  [assets/profile-template.md](assets/profile-template.md)
- Validator: [scripts/validate_profile.py](scripts/validate_profile.py)
