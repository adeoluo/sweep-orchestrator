# Changelog

All notable changes to this project are documented here. The file is generated
from Conventional Commits by [git-cliff](https://git-cliff.org) when a release is cut
with `make cut-release`.

## Unreleased

### Features

- Add successive halving and Hyperband multi-fidelity schedulers
- Add multi-objective Pareto optimization and importance analysis
- Add pruners, the parallel sweep runner, evaluation, and CLI
- Add HTTP service, benchmarks, and full documentation
- Add production observability (metrics and readiness) and reword footer

### Bug fixes

- Correct Hyperband bracket count for exact resource powers (#12)

### Documentation

- Use plain, factual wording (#11)
- Standard README structure and language framing (#14)
- Vertical layered architecture diagram
- Horizontal layered architecture diagram
- Compact horizontal architecture diagram
- Recorded demos of more commands, with their vhs tapes (#1)
- Recorded demos of the HTTP service and more commands (#2)
- Describe the supply chain accurately (#3)

### Build and CI

- Run CodeQL on main and on a weekly schedule only

### Maintenance

- Scaffold sweep-orchestrator project
- Bump continuous integration action versions and dev dependencies
- Remove Dependabot configuration
