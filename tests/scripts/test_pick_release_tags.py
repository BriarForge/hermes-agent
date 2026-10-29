"""The release-tag picker reads origin, not the local checkout, and keeps CalVer order."""
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "sandbox" / "pick-release-tags.sh"


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _pick(repo, *args):
    return subprocess.run(["bash", str(SCRIPT), *args, "--repo", str(repo)], check=True, capture_output=True, text=True).stdout.strip()


def _origin_with_tags(root, tags):
    origin = root / "origin.git"
    _git(root, "init", "--bare", "-b", "main", str(origin))
    seed = root / "seed"
    _git(root, "init", "-b", "main", str(seed))
    _git(seed, "config", "user.name", "fixture")
    _git(seed, "config", "user.email", "fixture@example.invalid")
    for tag in tags:
        _git(seed, "commit", "--allow-empty", "-m", tag)
        _git(seed, "tag", tag)
    _git(seed, "push", str(origin), "main", "refs/tags/*:refs/tags/*")
    return origin


def test_picking_reads_origin_not_local_tags(tmp_path):
    # CalVer names where version order is the chronology but lexicographic
    # order is not: v2026.4.13 sorts before v2026.4.3 as plain text.
    origin = _origin_with_tags(tmp_path, ["v2026.4.3", "v2026.4.13", "v2026.9.15"])
    # --no-local forces the transport, so the tagless clone truly lacks the
    # tag objects, not just their refs.
    _git(tmp_path, "clone", "--no-local", str(origin), str(tmp_path / "with-tags"))
    _git(tmp_path, "clone", "--no-local", "--no-tags", str(origin), str(tmp_path / "tagless"))
    assert _pick(tmp_path / "tagless", "--count", "2") == '["v2026.4.3","v2026.9.15"]'
    # Only the picked tags are materialized; unselected releases are not fetched.
    assert set(_git(tmp_path / "tagless", "tag", "--list").stdout.split()) == {"v2026.4.3", "v2026.9.15"}
    expected = '["v2026.4.3","v2026.4.13","v2026.9.15"]'
    assert _pick(tmp_path / "tagless", "--count", "5") == expected
    assert _pick(tmp_path / "with-tags", "--count", "5") == expected


def test_picking_accepts_semver(tmp_path):
    origin = _origin_with_tags(tmp_path, ["v0.27.0"])
    _git(tmp_path, "clone", "--no-local", "--no-tags", str(origin), str(tmp_path / "tagless"))
    assert _pick(tmp_path / "tagless") == '["v0.27.0"]'


def test_picking_fork_local_parent_tags(tmp_path):
    origin = _origin_with_tags(tmp_path, ["canary-v0.22.5"])
    fork = tmp_path / "fork"
    _git(tmp_path, "clone", "--no-local", "--no-tags", str(origin), str(fork))
    _git(fork, "tag", "v0.22.4")
    _git(fork, "tag", "v0.22.5")
    assert _pick(fork) == '["v0.22.4","v0.22.5"]'
    from scripts.releases.pick_tags import pick_tags
    assert pick_tags(fork, 2) == ["v0.22.4", "v0.22.5"]
