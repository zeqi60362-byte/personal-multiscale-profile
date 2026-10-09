# Personal Multiscale Profile

An early-stage Codex skill for building a dated, evidence-bounded model of a
person through structured interviews, artifacts, decision histories, and
longitudinal updates.

This project is intentionally **not** a personality test. It does not produce a
single score, diagnose anyone, or support hiring, admissions, clinical,
disciplinary, or other high-impact decisions.

## What It Produces

The profile is organized across five scales:

- Micro: attention, habits, reactions, and recurring friction.
- Meso: capabilities, roles, collaboration, output, and learning patterns.
- Macro: values, motivations, identity narratives, and long-term direction.
- Temporal: continuity, change, turning points, and recurring loops.
- Contextual: environments, constraints, resources, and growth conditions.

Every conclusion is separated into evidence, interpretation, confidence, and
unknowns. Earlier versions are preserved so the profile can evolve over time.

## Repository Layout

```text
personal-multiscale-profile/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|   |-- profile-template.json
|   |-- profile-template.md
|   `-- question-bank.json
|-- references/
|   |-- interview-protocol.md
|   |-- profile-schema.md
|   `-- safety-and-privacy.md
`-- scripts/
    |-- check_skill.py
    `-- validate_profile.py
```

## First Draft Status

Version: `0.1.0`

This repository is a working draft. The planned iterations are:

1. Test the six-round interview on a real baseline session.
2. Refine questions based on which prompts produce concrete evidence.
3. Add a longitudinal comparison workflow.
4. Add export formats for Markdown, JSON, and a concise one-page summary.
5. Add optional, user-controlled integrations only after the local workflow is
   stable.

## Use

Copy or link this folder into your Codex skills directory when you want to use
it locally. The skill can then be invoked as:

```text
$personal-multiscale-profile
```

The first session should establish consent, scope, and the data sources that
may be used. Personal profiles should remain outside the repository.

Local validation:

```bash
python scripts/check_skill.py
python scripts/validate_profile.py assets/profile-template.json
python scripts/validate_profile.py --self-test
```

## Privacy

The repository contains the method and templates only. Real profiles, contact
details, health information, legal records, and other sensitive material are
excluded by `.gitignore` and should stay in a private, user-controlled
location.

## License

License not yet selected.

## 中文说明

这是一个用于“个人多尺度画像”的 Codex skill 初稿。它通过结构化问答、作品与
决策记录、以及后续更新，建立一个有时间戳、带证据等级、允许矛盾和未知项的
个人工作模型。它不是心理测验，不输出人的总分，也不用于招聘、录取、临床或
其他高影响决策。

当前仓库只包含方法与模板，不应上传真实个人画像或敏感资料。
