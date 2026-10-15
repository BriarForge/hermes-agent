# Fork divergences

BriarForge/hermes-agent vs NousResearch/hermes-agent.

This file is the source of truth for fork-only intent. It is **not** a replay recipe — there are no SHAs to cherry-pick across a tag sync. Each entry states the behavior the tree must preserve, in plain English, so the next sync can implement it on whatever upstream files exist at the time.

## Snapshot

| Field | Value |
|---|---|
| Generated (UTC) | 2026-10-15T21:45Z |
| Upstream release tag | `v0.22.2` (`7b77e29eed`) `d923a5eb48 Release 0.22.2 from release/0.22.1 with the published v0.22.1 as a parent` |
| Fork HEAD | D1 + D3 + this ledger on `v0.22.2` |
| Tag is an ancestor of HEAD | yes (`git merge-base --is-ancestor v0.22.2 HEAD` = 0) |
| Active English divergences | **2** (D1, D3) |
| Dropped this sync (upstream satisfies) | D2 |
| Re-implemented this sync | D1 (`install-e2e.yml` + `pick-release-tags.sh`), D3 (`contributors/emails/agent@agents-Mac-mini.local`) |

Counts change on every fetch and every sync. Regenerate this table when you refresh the ledger.

## Authored divergences (plain-English intent)

### D1 — Install & Update E2E on forks

A fork of this repo does not carry release tags (`vYYYY.M.D` or `v0.Y.Z`). `actions/checkout fetch-tags` only sees `origin`. Running the `Install & Update E2E` picker on a fork fails the tag-picker and emails the fork owner.

**What must be true on the tree (after every release-tag sync):**

1. Any scheduled `Install & Update E2E` run is suppressed on a fork (`github.event_name == 'schedule'` AND `github.event.repository.fork` must skip). `workflow_dispatch` and `workflow_call` still run.
2. The `pick-releases` job, before invoking `pick-release-tags.sh` / `pick_tags.py`, checks whether local `v*` tags exist. If none, it fetches tags from `github.event.repository.parent.clone_url`, falling back to `https://github.com/NousResearch/hermes-agent.git`.
3. The picker error message names the fork case in addition to the shallow-clone case, so future fork owners know why tag selection failed.
4. Items 1–3 are applied to whichever file currently owns the schedule / picker in upstream — `install-e2e.yml` today; `install-e2e-run.yml` or a renamed equivalent if upstream moves the trigger. The intent travels with the picker, not with the filename.

**How to run the absorption test on a new release tag:** `git show <NEW_TAG>:.github/workflows/install-e2e.yml` (and any renamed successor). If the file already satisfies 1–3, drop D1 from this ledger. Removing `on.schedule` is **not** enough: `workflow_dispatch` on a fork still needs items 2–3. Otherwise, edit the upstream-renamed file in place and `git-aoife commit`.

**Realization on the current tree (snapshot, not a replay source):** D1 is satisfied by `2eb05050e4` `ci(install-e2e): skip schedule on forks, fetch upstream tags when missing` on `v0.22.2`. Do not cherry-pick that SHA across a reset.

### D3 — No case-colliding `agent@Agents-Mac-mini.local` contributor files

Upstream tracks `contributors/emails/agent@agents-Mac-mini.local` (`momomojo`). It previously also tracked `contributors/emails/agent@Agents-Mac-mini.local` (`skip-agent`). They cannot coexist on a case-insensitive filesystem, so `git status` is always dirty and `hermes update` autostashes every run. Upstream already deleted both once (`693c0e1c62`); release automation put at least one spelling back.

**What must be true on the tree (after every release-tag sync):**

1. Neither spelling is tracked. They are stale agent identifiers, not real contributors.
2. The working tree is clean of both paths so `hermes update` does not autostash.

**How to run the absorption test on a new release tag:** `git ls-tree -r --name-only <NEW_TAG> | grep -i 'contributors/emails/agent@.*gents-Mac-mini.local'`. If the tag has neither file, drop D3. If either or both exist, delete both and `git-aoife commit`. Do not keep one spelling: the two blobs disagree (`skip-agent` vs `momomojo`).

**Realization on the current tree (snapshot, not a replay source):** D3 is satisfied by `b6a707c4f9` `ci: drop case-colliding agent@agents-Mac-mini.local contributor file` on `v0.22.2` (lowercase spelling only was present; deleted). Do not cherry-pick that SHA across a reset.

## Absorbed this sync (do not re-implement)

### D2 — Dashboard Vite config is silent under native configLoader — absorbed on `v0.22.2`

`web/vite.config.ts` on `v0.22.2` resolves `@` and `@hermes/shared` via `fileURLToPath(new URL(".", import.meta.url))` (`configDir`), not `__dirname`. There is no `build.rolldownOptions.checks.pluginTimings` key, so the babel-dominated build cannot print that yellow notice. Dropped.

## Local state (not divergences)

Present on this worktree at generation time. Not committed. Not a divergence until committed on the fork.

- Named checkout `/home/mike/Work/BriarForge/hermes-agent` had no `.git` (macOS inode-share did not survive the omarchy move). This sync cloned `BriarForge/hermes-agent` and replaced the named path so the cron path is a real worktree again. Remotes: `origin`/`aoife` → `git@github-aoife:BriarForge/hermes-agent.git`, `upstream` → `git@github.com:NousResearch/hermes-agent.git`.
- Live install at `/home/mike/.hermes/hermes-agent` is a separate NousResearch clone (`origin` = NousResearch). Do not reset it as if it were the fork. `hermes update` targets that install, not this checkout.
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
