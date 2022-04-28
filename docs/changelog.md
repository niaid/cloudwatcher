# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

## [0.0.5] - 2022-04-28

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
