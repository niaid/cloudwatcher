# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## [0.1.0] - 2022-11-08

### Added

- presets functionality to improve UX

### Changed

- merged `--dimension-name` and `--dimension-value` into `--dimensions` option

### Removed

- defaults for `--id`, `-unit`, `--stat` etc. Presets should be used instead
- `query_kwargs` argument

## [0.0.6] - 2022-05-03

### Added

- A possibility to query dimensions other than `InstanceId` via `--dimension-name` option.

### Removed

- `-iid/--instance-id` option. Use a combination of `--dimension-name` and `--dimension-value` from now.

## [0.0.4] - 2022-04-28

### Added

- A possibility to specify EC2 query presets for CloudWatch metrics -- `query_presets` argument
- A possibility to specify EC2 query key word arguments -- `query_kwargs` argument

## [0.0.3] - 2022-04-25

### Added

- Added support for log saving to file: `cloudwatcher log --save`

## [0.0.2] - 2022-04-25

### Added

- Initial release
