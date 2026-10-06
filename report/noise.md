Lặp lại: results, results-rep1, results-rep2 (vai trò `eval`)

| Điều kiện | Tác vụ | Điểm từng lần | Trung bình | Dao động (max-min) | Token TB |
|---|---|---|---|---|---|
| baseline | code-eval | 0.64, 0.64, 0.64 | 0.64 | 0.00 | 80,365 |
| baseline | data-eval | 0.56, 0.56, 0.56 | 0.56 | 0.00 | 38,647 |
| baseline | logs-eval | 0.60, 0.60, 0.60 | 0.60 | 0.00 | 28,584 |
| subagents | code-eval | 0.64, 0.64, 0.64 | 0.64 | 0.00 | 189,805 |
| subagents | data-eval | 0.56, 0.56, 0.56 | 0.56 | 0.00 | 84,872 |
| subagents | logs-eval | 0.60, 0.60, 0.60 | 0.60 | 0.00 | 85,685 |
| skills-auto | code-eval | 0.91, 0.91, 0.91 | 0.91 | 0.00 | 117,247 |
| skills-auto | data-eval | 0.78, 0.78, 0.78 | 0.78 | 0.00 | 39,377 |
| skills-auto | logs-eval | 0.90, 0.90, 0.90 | 0.90 | 0.00 | 28,941 |

| Điều kiện | Số lần chạy | Điểm TB | Điểm TB thấp nhất / cao nhất theo lần lặp | Kỹ thuật đạt | Quy ước đạt | Token TB | Điểm / 100k token |
|---|---|---|---|---|---|---|---|
| baseline | 9 | 0.597 | 0.597 / 0.597 | 54/54 | 0/36 | 49,199 | 1.21 |
| subagents | 9 | 0.597 | 0.597 / 0.597 | 54/54 | 0/36 | 120,120 | 0.50 |
| skills-auto | 9 | 0.862 | 0.862 / 0.862 | 54/54 | 24/36 | 61,855 | 1.39 |
