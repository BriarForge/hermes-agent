# Fork divergences

BriarForge/hermes-agent vs NousResearch/hermes-agent.

This file is the changelog for **authored** fork drift. Lag is not drift.

## Snapshot

| Field | Value |
|---|---|
| Generated (UTC) | 2026-08-23T03:33:21Z |
| Fork HEAD | `55f51e5fe0` `ci(install-e2e): skip schedule on forks, fetch upstream tags when missing` |
| Upstream `main` | `fd760435c6` `test(bedrock): make the botocore stub windows airtight` |
| Merge-base | `e624e9fde5` `chore: map contributor email for #88864 salvage` |
| Ahead (`upstream/main..HEAD`) | **1** authored commit |
| Behind (`HEAD..upstream/main`) | **996** (lag, rebasable; not a fork change) |

Counts are a snapshot. They change on the next `git fetch`. Regenerate this file after any fork commit or upstream sync.

## How to regenerate

```bash
cd /Users/mike/Projects/BriarForge/hermes-agent
git-declan fetch upstream main
echo "fork=$(git rev-parse --short HEAD)"
echo "upstream=$(git rev-parse --short upstream/main)"
echo "merge_base=$(git rev-parse --short $(git merge-base HEAD upstream/main))"
echo "ahead=$(git rev-list --count upstream/main..HEAD)"
echo "behind=$(git rev-list --count HEAD..upstream/main)"
git log --pretty='format:%h|%aI|%an|%s' upstream/main..HEAD
git diff --name-status upstream/main...HEAD
```

Then edit this file: refresh the snapshot table, add a dated entry for each new SHA in `upstream/main..HEAD`, drop entries that have been merged into upstream (no longer in that range).

Source of truth is git, not this file. If they disagree, regenerate.

## Divergence vs lag

- **Divergence (track here):** commits on the fork that are not on `upstream/main`. Range: `upstream/main..HEAD`.
- **Lag (do not invent entries for):** commits on `upstream/main` that the fork has not merged yet. Range: `HEAD..upstream/main`. Rebase or merge to shrink it. The current 996 is lag only.

Uncommitted dirty/untracked work is **not** a divergence until it is committed on the fork.

## Authored divergences

### 2026-08-23 — ci(install-e2e): skip schedule on forks, fetch upstream tags when missing

| Field | Value |
|---|---|
| SHA | `55f51e5fe0` |
| Author | Declan Murphy `<278305138+declan-murphy-bf@users.noreply.github.com>` |
| Date | 2026-08-23T09:11:47+08:00 |
| Files | `.github/workflows/install-e2e.yml`, `scripts/sandbox/pick-release-tags.sh` |
| Class | fork-only **and** upstream candidate |
| Proof | Actions run [32609830207](https://github.com/BriarForge/hermes-agent/actions/runs/32609830207): `Pick release tags` succeeded after `No local release tags; fetching from https://github.com/NousResearch/hermes-agent.git` then `Testing updates from: ["v2026.8.19"]` |

**Why it exists.** This fork has zero `vYYYY.M.D` release tags. `actions/checkout` `fetch-tags: true` only sees origin. The 12h `Install & Update E2E` schedule (`20 7,19 * * *`) failed every tick and emailed the fork owner (17 scheduled failures, 0 successes).

**What it does.** Skip the scheduled job on forks (`if: github.event_name != 'schedule' || !github.event.repository.fork`). Manual / tag-push still run and fetch tags from `github.event.repository.parent.clone_url` (fallback `https://github.com/NousResearch/hermes-agent.git`). Picker error text now names the fork case, not only shallow clones.

**Upstream?** Yes. Same two files exist on NousResearch/hermes-agent. The schedule skip is one `if:` line; the picker message is docs. Cherry-pick `55f51e5fe0` onto a fresh upstream-based branch and open a PR against NousResearch/hermes-agent. Use `git-declan` for the push.

## Local state (not divergences)

Present on this worktree at generation time. Not committed. Do not `git add` them as part of a divergence refresh.

- Dirty: `contributors/emails/agent@agents-Mac-mini.local` (pre-existing; leave it)
- Untracked: `tinker-atropos/` (leave it)

## Playbook

1. After a fork-only commit: add a dated section under **Authored divergences**, bump the snapshot.
2. After merging/rebasing `upstream/main`: regenerate counts; delete any SHA that no longer appears in `upstream/main..HEAD` (it landed upstream or was dropped).
3. Candidate for upstream: cherry-pick onto a branch from `upstream/main`, push via the per-person wrapper, PR to NousResearch/hermes-agent.
4. Never treat `behind` as a list of fork changes.
