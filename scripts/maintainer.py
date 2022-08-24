#! /usr/bin/env python3
# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import re
import shutil
import subprocess


def run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, check=True, **kwargs)


def capture(cmd, **kwargs):
    return run(cmd, capture_output=True, **kwargs).stdout.decode("utf-8")


def do_build(args):
    run("python3 -m build .")


def do_test(args):
    run('PYTHONPATH="$(realpath src):${PYTHONPATH}" pytest tests')


def do_clean(args):
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("src/bitbangrelay.egg-info"):
        shutil.rmtree("src/bitbangrelay.egg-info")


def do_release(args):
    do_clean(args)

    args.release = True
    do_set_version(args)
    release_commit = capture("git rev-parse HEAD").strip()

    do_build(args)

    with open("dist/RELEASE_NOTES.txt", "w") as f:
        f.write(f"bitbangrelay {args.version}\n")
        text = capture(f"markdown-extract -n ^{args.version} ChangeLog.md")
        f.write(text)

    file_list = (
        "RELEASE_NOTES.txt "
        f"bitbangrelay-{args.version}.tar.gz bitbangrelay-{args.version}-py3-none-any.whl"
    )
    with open("dist/SHA256SUMS", "w") as f:
        text = capture(f"sha256sum {file_list}", cwd="dist")
        f.write(text)
    with open("dist/B3SUMS", "w") as f:
        text = capture(f"b3sum {file_list}", cwd="dist")
        f.write(text)
    file_list += " SHA256SUMS B3SUMS"
    if args.sign:
        run("gpg --detach-sign -a dist/SHA256SUMS")
        run("gpg --detach-sign -a dist/B3SUMS")
        file_list += " SHA256SUMS.asc B3SUMS.asc"

    run(f"git tag -a -F dist/RELEASE_NOTES.txt v{args.version} HEAD")
    if not args.no_gitlab:
        run("git push origin")
        run(f"git push origin {release_commit}:refs/heads/release")
        run(f"git push origin v{args.version}")
        run(
            f"glab release create v{args.version} -F RELEASE_NOTES.txt {file_list}",
            cwd="dist",
        )
        run(
            "twine upload -r gitlab-bitbangrelay "
            f"bitbangrelay-{args.version}.tar.gz "
            f"bitbangrelay-{args.version}-py3-none-any.whl",
            cwd="dist",
        )
    if not args.no_github:
        run("git push gh")
        run(f"git push gh {release_commit}:refs/heads/release")
        run(f"git push gh v{args.version}")
        run(
            f"gh release create v{args.version} -F RELEASE_NOTES.txt {file_list}",
            cwd="dist",
        )
    if not args.no_pypi:
        run(
            "twine upload "
            f"bitbangrelay-{args.version}.tar.gz "
            f"bitbangrelay-{args.version}-py3-none-any.whl",
            cwd="dist",
        )


def do_release_signatures(args):
    file_list = "SHA256SUMS.asc B3SUMS.asc"
    if not args.no_gitlab:
        run(f"glab release upload v{args.version} {file_list}", cwd="release")
    if not args.no_github:
        run(f"gh release upload v{args.version} {file_list}", cwd="release")


def do_set_version(args):
    with open("src/bitbangrelay/__init__.py", "r+") as f:
        text = re.sub(r"(__version__ =).*\n", rf'\1 "{args.version}"\n', f.read())
        f.seek(0)
        f.write(text)
        f.truncate()
    msg = "Release" if args.release else "Bump version to"
    run(f'git commit -asm "{msg} {args.version}"')


def do_no_command(args):
    print("Missing command! Try `./scripts/maintainer.py --help`")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.set_defaults(cmd_fn=do_no_command)
    subparsers = parser.add_subparsers(
        dest="cmd", title="Maintainer commands", metavar="command"
    )

    build_cmd = subparsers.add_parser(name="build", help="Build a wheel")
    build_cmd.set_defaults(cmd_fn=do_build)

    test_cmd = subparsers.add_parser(name="test", help="Run test suite")
    test_cmd.set_defaults(cmd_fn=do_test)

    clean_cmd = subparsers.add_parser(
        name="clean", help="Remove build output from the source tree"
    )
    clean_cmd.set_defaults(cmd_fn=do_clean)

    release_cmd = subparsers.add_parser(
        name="release", help="Release a new version of this project"
    )
    release_cmd.set_defaults(cmd_fn=do_release)
    release_cmd.add_argument("version", help="Version string for the new release")
    release_cmd.add_argument(
        "-s", "--sign", action="store_true", help="Sign release with gpg"
    )
    release_cmd.add_argument(
        "--no-gitlab",
        action="store_true",
        help="Disable push to SanCloud gitlab instance",
    )
    release_cmd.add_argument(
        "--no-github",
        action="store_true",
        help="Disable push to GitHub",
    )
    release_cmd.add_argument(
        "--no-pypi",
        action="store_true",
        help="Disable push to PyPI",
    )

    release_signatures_cmd = subparsers.add_parser(
        name="release-signatures",
        help="Push release signatures to GitHub and/or GitLab",
    )
    release_signatures_cmd.set_defaults(cmd_fn=do_release_signatures)
    release_signatures_cmd.add_argument(
        "version", help="Release to push signatures for (must already be released)"
    )
    release_signatures_cmd.add_argument(
        "--no-gitlab",
        action="store_true",
        help="Disable pushing signatures to SanCloud gitlab instance",
    )
    release_signatures_cmd.add_argument(
        "--no-github",
        action="store_true",
        help="Disable pushing signatures to public github repositories",
    )

    set_version_cmd = subparsers.add_parser(
        name="set-version", help="Set version string & commit"
    )
    set_version_cmd.set_defaults(cmd_fn=do_set_version)
    set_version_cmd.add_argument("version", help="New version string")
    set_version_cmd.add_argument(
        "-r",
        "--release",
        action="store_true",
        help="This version bump is for a release",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    args.cmd_fn(args)


if __name__ == "__main__":
    main()
