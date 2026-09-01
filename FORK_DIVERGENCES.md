# Fork divergences

BriarForge/hermes-agent vs NousResearch/hermes-agent.

This file is the source of truth for fork-only intent. It is **not** a replay recipe — there are no SHAs to cherry-pick across a tag sync. Each entry states the behavior the tree must preserve, in plain English, so the next sync can implement it on whatever upstream files exist at the time.

## Snapshot

| Field | Value |
|---|---|
| Generated (UTC) | 2026-09-01T00:04Z |
| Upstream release tag | `v2026.8.31` (`29112bef09`) `chore: release v0.21.0 (2026.8.31)` |
| Fork HEAD | `485f4d2de0` `docs: add D2/D3 to FORK_DIVERGENCES for update-warning fixes` |
| Tag is an ancestor of HEAD | yes (`git merge-base --is-ancestor v2026.8.31 HEAD` = 0) |
| `origin/main...HEAD` | `2 0` (local, unpushed) |
| Active English divergences | **3** (D1, D2, D3) |
| Re-implemented this sync | D2 and D3 on the v2026.8.31 tree (no new upstream tag) |

Counts change on every fetch and every sync. Regenerate this table when you refresh the ledger.

## Authored divergences (plain-English intent)

### D1 — Install & Update E2E on forks

A fork of this repo does not carry `vYYYY.M.D` release tags. `actions/checkout fetch-tags` only sees `origin`. Running the `Install & Update E2E` schedule on a fork fails the tag-picker every tick and emails the fork owner on every run.

**What must be true on the tree (after every release-tag sync):**

1. The scheduled `Install & Update E2E` run is suppressed on a fork (`github.event_name == 'schedule'` AND `github.event.repository.fork` must skip). `workflow_dispatch` and `push tags` still run.
2. The `pick-releases` job, before invoking `pick-release-tags.sh`, checks whether local `v*` tags exist. If none, it fetches tags from `github.event.repository.parent.clone_url`, falling back to `https://github.com/NousResearch/hermes-agent.git`.
3. The picker error message names the fork case in addition to the shallow-clone case, so future fork owners know why tag selection failed.
4. Items 1–3 are applied to whichever file currently owns the schedule in upstream — `install-e2e.yml` today; `install-e2e-run.yml` or a renamed equivalent if upstream moves the trigger. The intent travels with the schedule, not with the filename.

**How to run the absorption test on a new release tag:** `git show <NEW_TAG>:.github/workflows/install-e2e.yml` (and any renamed successor). If the file already satisfies 1–3, drop D1 from this ledger. Otherwise, edit the upstream-renamed file in place and `git-aoife commit`.

**Realization on the current tree (snapshot, not a replay source):** D1 is satisfied by `ce24c19a61` `ci(install-e2e): skip schedule on forks, fetch upstream tags when missing` (replay carryover from the v2026.8.18 era; present in this fork's HEAD as a commit on top of `v2026.8.31`). The next sync that moves to a tag where upstream already does 1–3 must drop D1 and adopt upstream's version. The next sync that moves to a tag where upstream does NOT do 1–3 must re-implement D1 on whatever file owns the schedule — **not** cherry-pick `ce24c19a61` across.

### D2 — Dashboard Vite config is silent under native configLoader

`hermes update` rebuilds `web/` with Vite 8. The dashboard config currently uses `__dirname` for alias roots, which the native configLoader does not support, and the React Compiler babel pass dominates the build so plugin-timings prints a yellow notice. Both show up as warnings on every update even when the code is already current.

**What must be true on the tree (after every release-tag sync):**

1. `web/vite.config.ts` resolves `@` and `@hermes/shared` with `import.meta.dirname`, not `__dirname`.
2. `build.rolldownOptions.checks.pluginTimings` is `false` so the expected babel-dominated build does not warn.

**How to run the absorption test on a new release tag:** `git show <NEW_TAG>:web/vite.config.ts`. If aliases already use `import.meta.dirname` and plugin timings do not warn on `npm run build` in `web/`, drop D2. Otherwise edit the current Vite config in place (file name may change) and `git-aoife commit`.

**Realization on the current tree (snapshot, not a replay source):** D2 is satisfied by `c3befa1367` `fix: silence hermes update warnings from vite and macOS git dirt`. Do not cherry-pick that SHA across a reset.

### D3 — No case-colliding `agent@Agents-Mac-mini.local` contributor files

Upstream tracks both `contributors/emails/agent@Agents-Mac-mini.local` (`skip-agent`) and `contributors/emails/agent@agents-Mac-mini.local` (`momomojo`). They cannot coexist on a case-insensitive filesystem, so `git status` is always dirty and `hermes update` autostashes every run. Upstream already deleted both once (`693c0e1c62`); release automation put them back.

**What must be true on the tree (after every release-tag sync):**

1. Neither spelling is tracked. They are stale agent identifiers, not real contributors.
2. The working tree is clean of both paths so `hermes update` does not autostash.

**How to run the absorption test on a new release tag:** `git ls-tree -r --name-only <NEW_TAG> | grep -i 'contributors/emails/agent@.*gents-Mac-mini.local'`. If the tag has neither file, drop D3. If either or both exist, delete both and `git-aoife commit`. Do not keep one spelling: the two blobs disagree (`skip-agent` vs `momomojo`).

**Realization on the current tree (snapshot, not a replay source):** D3 is satisfied by the same `c3befa1367` commit as D2. Do not cherry-pick that SHA across a reset.

## Local state (not divergences)

Present on this worktree at generation time. Not committed. Not a divergence until committed on the fork.

- Stash `{0}`: `pre-hermes-update-20260831T212527Z-vite-dirname` (Mike's earlier `import.meta.dirname` experiment). Stashed, not popped. D2 now covers this in the tree; leave the stash parked.

## Playbook (matches `/Users/mike/Projects/BriarForge/AGENTS.md` § Hermes fork updates)

1. `git fetch upstream --tags --prune`.
2. Pick the highest `vYYYY.M.D` newer than current HEAD. Hard-stop if none.
3. Create `backup/pre-hermes-update-<stamp>-<oldtag>` from current HEAD. Push best-effort.
4. `git checkout main && git reset --hard <NEW_TAG>`. No SHA cherry-pick.
5. For each entry in this ledger, run the absorption test on the **new tag's** files (file names may have changed). Drop entries that upstream already satisfies; re-implement the rest from scratch on the current files; `git-aoife commit` each.
6. Rewrite this ledger (the one you're reading) so it lists only what still diverges, in English.
7. `git-aoife push aoife main` (default push). If history was rewritten at step 4, add `--force-with-lease`. Never bare `git push`. Never `declan-murphy-bf`.
8. Verify: tag is ancestor of HEAD; `origin/main...HEAD` = `0 0`; tree clean or only known throwaway dirt; stash `{0}` intact.
9. Do **not** run `hermes update` in any path that pulls `upstream/main`. Release-tag sync is a separate ritual.
