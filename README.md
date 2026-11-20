# asfexample

**This package does not have official Apache Software Foundation (ASF) releases.**

This is an example test package issued by Tooling at the ASF. It contains no stable user facing functionality. We do not make guarantees about any of the interfaces contained herein, nor the continued existence of this package.

The purpose of this package is to test:

- Proposed package naming conventions and version schemes within ASF Infra and ASF Tooling
- GHA workflows for trickle down use in other ASF Tooling projects
- Interaction with the ATR platform presently under development by ASF Tooling

## Reporting issues

Report bugs at https://github.com/apache/tooling-asf-example/issues.

**Do NOT report security vulnerabilities through public GitHub issues.** Please report security vulnerabilities to the Apache Security Team by emailing **security@apache.org**. This is a private mailing list. Please send one plain-text, unencrypted, email for each vulnerability you are reporting. For complete details on reporting and the process, see the [ASF Security Team](https://www.apache.org/security/) page.

## Proposed conventions

The proposed packaging conventions are:

- Use `asf${NAME}` or `${NAME}` for PyPI package names, depending on whether the package is for ASF use only or not
- Ensure that package code is in `${NAME}/` only
- Use `0.0.N` for versions, starting with `0.0.1`
- Increment `N` for each released version
- Use `0.0.(N+1).dev0+dev` for non-release `main` commits, starting with `0.0.1.dev0+dev`

The `+dev` makes it a local version, which PyPI will not accept, so a build from source can never be published as a release. The `.dev0` makes it a pre-release, so installers that can see both choose the release.

A package having three commits on `main`, then a release, then two more commits to `main`, then another release, will for example use the following versions:

```
0.0.1.dev0+dev
0.0.1.dev0+dev
0.0.1.dev0+dev
0.0.1
0.0.2.dev0+dev
0.0.2.dev0+dev
0.0.2
```

These packaging conventions are proposed only for ASF Infra and Tooling packages which will be published to PyPI. Other packages, for internal use, may use any packaging conventions. Aligning with these conventions, if adopted, would, however, make it easier to promote internal packages to PyPI.

## Releasing

To release, run `sh scripts/phase.sh release` on an up to date `main`. It changes the version from `0.0.N.dev0+dev` to `0.0.N`, commits, tags that commit `v0.0.N`, and pushes the commit and the tag together.

The upload waits until two members of ASF Tooling approve it at https://releases.apache.org/gates.

Afterwards, run `sh scripts/phase.sh develop` to change the version to `0.0.(N+1).dev0+dev`, commit, and push.

## Development

Run `uv run prek install` once after cloning. Its hooks run the linters and check the version scheme on every commit, and add the type checks and tests on every push.

### Keeping your branch up to date

`main` has no merge commits, which are the commits that `git merge` and a plain `git pull` make when they join two lines of work. GitHub refuses any push to `main` that contains one, and the checks fail on any pull request that contains one.

So never merge `main` into your branch. To catch up, move your commits on top of the latest `main`, then replace your branch on GitHub:

```shell
git pull --rebase origin main
git push --force-with-lease
```

The button on a pull request page that updates the branch merges by default, so if you use it, choose its rebase option instead. If you push to `main` directly, run `git config pull.rebase true` once, so that `git pull` never makes a merge commit.

The same two commands fix a pull request whose checks fail with "merge commits are not allowed, so rebase instead". They also fix one that was started during a release and fails the version check, once the release has finished.
