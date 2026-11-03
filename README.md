# asfexample

**This package does not have official Apache Software Foundation (ASF) releases.**

This is an example test package issued by Tooling at the ASF. It contains no stable user facing functionality. We do not make guarantees about any of the interfaces contained herein, nor the continued existence of this package.

The purpose of this package is to test:

- Proposed package naming conventions and version schemes within ASF Infra and ASF Tooling
- GHA workflows for trickle down use in other ASF Tooling projects
- Interaction with the ATR platform presently under development by ASF Tooling

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

## Development

Run `uv run prek install` once after cloning. Its hooks run the linters and check the version scheme on every commit, and add the type checks and tests on every push.
