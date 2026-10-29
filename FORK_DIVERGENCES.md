# Fork divergences

BriarForge/hermes-agent vs NousResearch/hermes-agent. This English intent ledger is not a SHA replay recipe. Assess each item against the next release tag's behavior, regardless of filenames; drop it if upstream satisfies it, otherwise re-implement on the new tree.

## Snapshot

- Baseline: upstream release `v0.22.5` (`56b6a31fed`); fork HEAD adds D1, D3 and this ledger.
- Previous baseline: `v0.22.4`; sync on 2026-10-30 AWST.
- Active divergences: D1, D3. Both re-implemented on this tag. D2 was already absorbed on `v0.22.2`.

## D1 — Install & Update E2E on forks

Forks often have no origin release tags. A manual dispatch or workflow call must still pick real upstream release baselines rather than fail or sample canaries. If scheduled triggers return, skip schedules on forks; never suppress manual dispatch or workflow calls. Before picking, if local release tags are absent on a fork, fetch them from `github.event.repository.parent.clone_url` (fallback `https://github.com/NousResearch/hermes-agent.git`). Both the shell and Python pickers must use local fetched tags when origin has no release refs; they must not try to fetch those same refs from fork origin. Error messages must mention the fork/shallow-clone case. Accept both CalVer and semver stable release names. Follow the schedule and picker if upstream renames the files.

On `v0.22.5`, `.github/workflows/install-e2e.yml` has no schedule, but still has `workflow_dispatch` and `workflow_call`; its pick-releases checkout fetches missing parent tags. `scripts/sandbox/pick-release-tags.sh` and `scripts/releases/pick_tags.py` fall back to local refs when origin has no release tags. Reassess behavior on each new tag rather than replaying a commit.

## D3 — No case-colliding agent contributor files

Neither `contributors/emails/agent@agents-Mac-mini.local` nor `contributors/emails/agent@Agents-Mac-mini.local` should be tracked. The stale agent IDs previously collided on case-insensitive filesystems and caused dirty checkouts and updater autostashes. On the next tag check *both* names case-insensitively; if upstream has neither, drop D3; otherwise remove both from the tree. On `v0.22.5`, the lowercase spelling returned and was removed.

## Absorbed

D2 (Vite dashboard config): already satisfied by upstream on `v0.22.2`; do not re-implement.

## Host note

`/home/mike/Work/BriarForge/hermes-agent` is the fork checkout. `/home/mike/.hermes/hermes-agent` is a separate installed upstream clone; do not reset it as if it were this fork. Update only via a release-tag-safe path, never an updater path that syncs upstream/main.
