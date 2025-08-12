# asf-example

**This is not an official release of the Apache Software Foundation (ASF).**

This is an example test package issued by Tooling at the ASF. It contains no stable user facing functionality. We do not make guarantees about any of the interfaces contained herein, nor the continued existence of this package.

The purpose of this package is to test:

- Proposed package naming conventions and version schemes within ASF Infra and ASF Tooling
- GHA workflows for trickle down use in other ASF Tooling projects
- Interaction with the ATR platform presently under development by ASF Tooling

The proposed packaging conventions are:

- Use the `asf-*` prefix scheme for PyPI package names to align with PEP 752
- Use `asf.*` for package interfaces, utilising PEP 420 namespacing
- Ensure that package code is in `src/asf/*/` only
- Ensure that `src/asf/*/` contains an `__init__.py`
- Use `0.N.0` for versions, starting with `0.1.0`
- Increment `N` for each released version, avoiding patch versions
- Optionally use `0.(N+1).0-devM` for non-release `main` commits
- Start with `-dev1` if using non-release `main` commit versions

A package having three commits on `main`, then a release, then two more commits to `main`, then another release, will for example use the following versions:

```
0.1.0-dev1
0.1.0-dev2
0.1.0-dev3
0.1.0
0.2.0-dev1
0.2.0-dev2
0.2.0
```
