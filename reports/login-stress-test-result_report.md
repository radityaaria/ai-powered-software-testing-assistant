# k6 Performance Test Report

## Test Summary

| Metric | Value |
|---|---:|
| Test Name | k6 Performance Test |
| Test Type | real k6 summary |
| P95 Response Time | 9754.80 ms |
| Average Response Time | 4744.89 ms |
| Error Rate | 0.00% |
| Total Requests | 4509 |
| Threshold P95 | 3000 ms |
| Threshold Error Rate | 10.00% |
| Final Status | FAIL |
| Performance Category | WARNING |

## Interpretation

Test gagal karena p95 response time melebihi threshold, meskipun error rate masih rendah. Ini menunjukkan adanya masalah latency.

## Recommendation

Terdapat indikasi latency yang perlu diperhatikan. Disarankan melakukan analisis pada backend, query database, proses autentikasi, dan penggunaan CPU.
