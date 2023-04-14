# 0L Prometheus Exporter

FastAPI server that exposes `/metrics` endpoint to be scraped by Prometheus.


## Tech

- https://fastapi.tiangolo.com
- https://github.com/prometheus/client_python
- https://prometheus.io
- https://grafana.com

## Prometheus

Example scraping job

```yaml
- job_name: ol-exporter-tower-1
  scrape_interval: 15s
  scrape_timeout: 5s
  static_configs:
    - targets:
        - 'ACCOUNT1'
        - 'ACCOUNT2'
        - 'ACCOUNTN'
      labels:
        ol_client: 'someone'
        __metrics_path__: '/metrics/tower'
        instance: 'ol-exporter.monitoring.svc:8000'
  relabel_configs:
    - source_labels: [ __address__ ]
      target_label: __param_account
    - source_labels: [ instance ]
      target_label: __address__
    - target_label: instance
      replacement: ''
```
