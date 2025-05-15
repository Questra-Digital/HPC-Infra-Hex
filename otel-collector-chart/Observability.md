## Implementation Steps
1. Installed Prometheus/Grafana via Helm
2. Instrumented Flask app with:
   - HTTP request counter
   - Latency histogram
   - Custom user metric
3. Configured Prometheus to scrape `/metrics`
4. Imported Grafana dashboards

## Metrics Collected
| Metric                | Type       | PromQL Example                     |
|-----------------------|------------|------------------------------------|
| HTTP Request Rate     | Counter    | `rate(http_requests_total[5m])`    |
| Error Rate (4xx/5xx)  | Counter    | `http_requests_total{status=~"4.."}` |
| Latency (p95)         | Histogram  | `histogram_quantile(0.95, ...)`    |
| Active Users          | Gauge      | `active_users`                     |