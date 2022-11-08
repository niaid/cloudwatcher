# Presets

In order to improve the UX when using `cloudwatcher metric` comamnd. The `cloudwatcher` package provides a few presets that can be used to query the data reported by `CloudWatchAgent` within certain systems. Additionally, custom presets can be defined by the user and used in the same way.

Presets are JSON-formatted files that provide parameter bundles for `MetricWatcher` initialization.

## Usage

The presets are used if `--preset-name` or `--preset-path` option is provided. The `--preset-name` option can be used to select one of the built-in presets. The `--preset-path` option can be used to select a custom preset.

Importantly, the settings defined in the preset can be extended or overridden by the user by providing additional arguments to the `cloudwatcher metric` command, e.g. `--dimensions key:value --metric-id test`.

### Custom preset command example

The custom preset can be defined in a JSON file, for example:

```json linenums="1" title="custom_preset.json"
{
  "namespace": "MetricNamespace",
  "dimensions_list": [
    {
      "Name": "InstanceId",
      "Value": "i-0c4d9523c99fbc1da"
    },
    {
      "Name": "cpu",
      "Value": "cpu-total"
    }
  ],
  "metric_name": "cpu_usage_user",
  "metric_id": "my_metric_id",
  "metric_unit": "Percent"
}
```

The above preset can be used by passing the `--preset-path` option:

```bash
cloudwatcher metric --preset-path custom_preset.json
```

### Built-in preset command example

The built-in presets can be used by passing the `--preset-name` option:

```bash
cloudwatcher metric --preset-name nepehele_mem
```
