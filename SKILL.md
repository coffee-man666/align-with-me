---
name: align-with-me
description: Align plans and implementation work with the user's intended, observable experience before building. Use when planning or carrying out a product, workflow, automation, or system change; do not use for simple factual answers or purely read-only analysis.
---

# Align With Me

Keep the user's intended experience, not the implementation, as the source of truth.

## Choose the Skill Installation Scope

When the user asks to install this skill or a skill package from a repository, ask them to choose the installation scope before writing files:

- **Project layer**: `<project>/.agents/skills/<skill-name>`, available to that project and its collaborators.
- **User layer**: `$CODEX_HOME/skills/<skill-name>`; when `CODEX_HOME` is not set, use `~/.codex/skills/<skill-name>`, available across the user's projects.

Do not choose silently. After the user chooses, install only to that scope and report the final path. If the source repository provides `scripts/install_skill.py`, use it. Treat an existing target as potentially user-owned: do not overwrite differing contents without explicit permission. Confirm that the installed `SKILL.md` exists before claiming success.

## Gate Implementation on Intent

Before discussing architecture, presenting a plan, editing files, or making changes, write this restatement in the user's language:

> You want: when you do X, you'll see Y, and you'll verify it by Z.

Replace X, Y, and Z with concrete use cases rather than specifications. Ask the user to confirm or correct the restatement, and wait for explicit sign-off before building. If the user has already explicitly approved the same restatement in the current conversation, do not ask again.

Brief read-only inspection is allowed when it is needed to understand X, Y, or Z. Do not let that inspection turn into architecture work before sign-off.

## Make Assumptions Vetoable

After sign-off, show an **Assumption ledger** before relying on ambiguous parts of the request. Label each entry as an assumption and state it plainly enough for the user to veto. If an assumption would materially change the outcome or scope, route it to the user as a decision instead of proceeding on it. Omit the ledger when there are no meaningful assumptions.

## Separate the Plan

When a plan is useful or requested, its plan portion must contain these two explicitly labeled lists:

### MVP

Include only the smallest end-to-end work that demonstrates the signed-off outcome. Every item must include a user-perceivable acceptance demo at the highest abstraction level the user can operate: for example, a command they run and output they see, a table they inspect, or a before/after behavior.

Internal checks such as unit tests may supplement the demo, but never substitute for it.

### Extensions

Put performance work, elegance, extra robustness, and “while we're at it” ideas here. Give each item a one-line justification and append the exact marker: **You can ignore this for now.** If there are no extensions, say so explicitly.

Do not quietly move extension work into the MVP.

## Route Decisions, Own Details

Ask the user only for choices that genuinely depend on their preferences or materially alter the observable outcome, risk, cost, or scope. Own ordinary technical choices silently.

When a necessary decision involves an unfamiliar concept, explain it with exactly the detail needed:

- a one-line plain-language definition;
- “The decision this affects is …”;
- “You do/do not need to understand this because …”.

Minimize what the user must learn in order to make the decision.

## Finish at the User's Layer

Demonstrate the completed MVP using the promised user-perceivable acceptance checks. Lead the handoff with what the user can now do, what they will see, and how they can verify it. Mention internal tests only as supporting evidence.
