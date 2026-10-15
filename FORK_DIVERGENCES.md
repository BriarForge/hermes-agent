# Fork divergences

BriarForge/hermes-agent vs NousResearch/hermes-agent.

This file is the source of truth for fork-only intent. It is **not** a replay recipe — there are no SHAs to cherry-pick across a tag sync. Each entry states the behavior the tree must preserve, in plain English, so the next sync can implement it on whatever upstream files exist at the time.

## Snapshot

| Field | Value |
|---|---|
| Generated (UTC) | 2026-10-15T21:39Z |
| Upstream release tag | `v0.22.2` (`7b77e29eed`) `d923a5eb48 Release 0.22.2 from release/0.22.1 with the published v0.22.1 as a parent` |
| Fork HEAD | `b6a707c4f9` `ci: drop case-colliding agent@agents-Mac-mini.local contributor file` (+ this ledger commit) |
| Tag is an ancestor of HEAD | yes (`git merge-base --is-ancestor v0.22.2 HEAD` = 0) |
| `origin/main...HEAD` | rewritten this sync; push with `--force-with-lease` |
| Active English divergences | **1** (D3) |
| Dropped this sync (upstream satisfies) | D1, D2 |
| Re-implemented this sync | D3 on the v0.22.2 tree |

Counts change on every fetch and every sync. Regenerate this table when you refresh the ledger.

## Authored divergences (plain-English intent)

### D3 — No case-colliding `agent@Agents-Mac-mini.local` contributor files

Upstream tracks `contributors/emails/agent@agents-Mac-mini.local` (`momomojo`). It previously also tracked `contributors/emails/agent@Agents-Mac-mini.local` (`skip-agent`). They cannot coexist on a case-insensitive filesystem, so `git status` is always dirty and `hermes update` autostashes every run. Upstream already deleted both once (`693c0e1c62`); release automation put at least one spelling back.

**What must be true on the tree (after every release-tag sync):**

1. Neither spelling is tracked. They are stale agent identifiers, not real contributors.
2. The working tree is clean of both paths so `hermes update` does not autostash.

**How to run the absorption test on a new release tag:** `git ls-tree -r --name-only <NEW_TAG> | grep -i 'contributors/emails/agent@.*gents-Mac-mini.local'`. If the tag has neither file, drop D3. If either or both exist, delete both and `git-aoife commit`. Do not keep one spelling: the two blobs disagree (`skip-agent` vs `momomojo`).

**Realization on the current tree (snapshot, not a replay source):** D3 is satisfied by `b6a707c4f9` `ci: drop case-colliding agent@agents-Mac-mini.local contributor file` on `v0.22.2` (lowercase spelling only was present; deleted). Do not cherry-pick that SHA across a reset.

## Absorbed this sync (do not re-implement)

### D1 — Install & Update E2E on forks — absorbed on `v0.22.2`

Upstream `install-e2e.yml` on `v0.22.2` no longer has a `schedule:` trigger. The comment block now says it never runs on pull requests, pushes to main, or a schedule; remaining triggers are `workflow_dispatch` and `workflow_call` from the stable-release gate. Intent items 1–3 (skip schedule on forks; fetch parent tags when a fork has none; name the fork case in the picker error) are vacuously satisfied because there is no scheduled fork tick to fail. Dropped. If a future tag reintroduces `on.schedule` on the Install & Update E2E owner file, restore this entry.

### D2 — Dashboard Vite config is silent under native configLoader — absorbed on `v0.22.2`

`web/vite.config.ts` on `v0.22.2` resolves `@` and `@hermes/shared` via `fileURLToPath(new URL(".", import.meta.url))` (`configDir`), not `__dirname`. There is no `build.rolldownOptions.checks.pluginTimings` key, so the babel-dominated build cannot print that yellow notice. Dropped.

## Local state (not divergences)

Present on this worktree at generation time. Not committed. Not a divergence until committed on the fork.

- Named checkout `/home/mike/Work/BriarForge/hermes-agent` had no `.git` (macOS inode-share did not survive the omarchy move). This sync cloned `BriarForge/hermes-agent` to `/tmp/briarforge-hermes-agent`, then replaced the named checkout's contents with that tree so the cron path is a real worktree again.
- Live install at `/home/mike/.hermes/hermes-agent` is a separate NousResearch clone. Do not reset it as if it were the fork.
- Host `gh` default account is `McoreD` (interactive `gh auth status` hangs in this cron). Push identity is SSH `github-aoife` as `aoife-brennan-bf`, which is what `git-aoife` uses.

## Playbook (matches `/home/mike/Work/BriarForge/ss/AGENTS.md` § Hermes fork updates)

1. `git fetch upstream --tags --prune`.
2. Pick the highest release tag newer than current HEAD (`vYYYY.M.D` or, after the 0.22 scheme change, `v0.Y.Z`). Hard-stop if none.
3. Create `backup/pre-hermes-update-<stamp>-<oldtag>` from current HEAD. Push best-effort.
4. `git checkout main && git reset --hard <NEW_TAG>`. No SHA cherry-pick.
5. For each entry in this ledger, run the absorption test on the **new tag's** files (file names may have changed). Drop entries that upstream already satisfies; re-implement the rest from scratch on the current files; `git-aoife commit` each.
6. Rewrite this ledger (the one you're reading) so it lists only what still diverges, in English.
7. `git-aoife push aoife main` (default push). If history was rewritten at step 4, add `--force-with-lease`. Never bare `git push`. Never `declan-murphy-bf`.
8. Verify: tag is ancestor of HEAD; `origin/main...HEAD` = `0 0`; tree clean or only known throwaway dirt; stash `{0}` intact.
9. Do **not** run `hermes update` in any path that pulls `upstream/main`. Release-tag sync is a separate ritual.
