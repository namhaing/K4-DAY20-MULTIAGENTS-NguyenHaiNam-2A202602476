# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Hải Nam | 2A202602476 | Toàn bộ (cá nhân): cài đặt harness, chạy thí nghiệm, đánh giá skill, báo cáo |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenAI `gpt-6-luna` qua cổng tương thích OpenAI (`AZURE_OPENAI_ENDPOINT=https://api.openai.com/v1`, đi nhánh `ChatOpenAI` của `model.py`); `LAB_TEMPERATURE=1` (mô hình từ chối `temperature=0`: "Only the default (1) value is supported"); `recursion_limit=60` (mặc định).
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, langchain-openai 1.6.7; máy chủ Windows 11, mọi lần chạy tác tử và `pytest` diễn ra trong Docker (`python:3.12-slim`, `Dockerfile` của lab); `git`, `verify_freeze.py`, `check_breakdown.py` chạy trên máy chủ với `PYTHONPATH=src`.
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

Viết sau Phần 3.4, trước khi chạy bất kỳ tác vụ đánh giá nào và trước tag `freeze`. Căn cứ: mục 4 (100% check thất bại ở tác vụ học là quy ước `rule_`, check kỹ thuật đạt 18/18), mục 5, mục 6, cùng SkillsBench và SkillEvolBench (`guides/pseudocode/04_curator.md`) và ghi nhận của Anthropic rằng đa tác tử tốn khoảng 15 lần token.

- H1 (subagents so với baseline): Trên tác vụ đánh giá, `subagents` có điểm **bằng** `baseline` (chênh lệch điểm trung bình ≤ 0,05) nhưng tốn khoảng **2–3 lần token**. Lý do: ở tác vụ học, hai điều kiện có điểm giống hệt (0,631) vì lỗi duy nhất là quy ước Acme không có trong đề, và subagent cũng không thể biết quy ước đó; trong khi token trung bình tăng 2,37 lần (101,8k so với 43,0k).
- H2 (skills-auto so với baseline): `skills-auto` đạt điểm **cao nhất** trên tác vụ đánh giá, khoảng 0,80–0,90 so với ~0,6 của `baseline`, và toàn bộ phần tăng nằm ở check quy ước được tái sử dụng từ tác vụ học (tiền tính bằng cent, khối `meta`, `clean.csv`, tên dịch vụ, thứ tự sắp xếp, header schema, type hint, test hồi quy, changelog); check kỹ thuật không đổi. Dự đoán này trái với kết quả trung bình của SkillsBench (skill tự sinh không có lợi) vì ở đây lỗi tập trung vào quy ước học được từ phản hồi, đúng loại tri thức thủ tục mà skill truyền đạt được.
- H3 (tác vụ học so với tác vụ đánh giá): Mức tăng của `skills-auto` trên tác vụ đánh giá **nhỏ hơn** trên tác vụ học (học: 0,631 → 1,000 ở Phần 3.4). Hai nguyên nhân: (1) mỗi tác vụ đánh giá có một quy ước **mới** không có trong skill, nên `skills-auto` không đạt 1,0; (2) skill chứa chi tiết gắn với dữ liệu học (ví dụ header `clean.csv` với các cột và tên vùng cụ thể), có thể không khớp dữ liệu đánh giá, là dấu hiệu quá khớp như SkillEvolBench mô tả.

## 3. Làm quen Deep Agents (Phần 0.3)

1. `scripts/tour.py` liệt kê 9 công cụ: công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; shell `execute`; giao việc `task`. Chỉ `execute` chạy lệnh trên hệ điều hành (qua `LocalShellBackend`, thư mục làm việc là sandbox).
2. Mô tả của `task` giới thiệu subagent `general-purpose` là tác tử đa năng để tìm kiếm và làm việc nhiều bước, "has access to all tools as the main agent". Về ngữ cảnh: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report", tức subagent không thấy hội thoại của tác tử chính, chỉ thấy prompt được giao.
3. System prompt mặc định rỗng (`''`), nên hành vi được định hướng qua mô tả công cụ. Từ `task`: "Put full detail in the prompt and state exactly what it should return". Từ `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Kết quả `baseline` trên tác vụ học: `code-learn` 7/10, `data-learn` 5/8, `logs-learn` 6/9 (`results/baseline/`).

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | "RULE: every public function … has type annotations on all parameters and on the return value"; tác tử chỉ sửa thân hàm (`edit_file` trên `pricing.py`, `export.py`, `report.py`). |
| code-learn | `rule_regression_tests` | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3)"; vết không có lệnh ghi tệp nào trong `tests/`. |
| code-learn | `rule_changelog` | E | "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' …"; tác tử không đọc và không sửa `CHANGELOG.md`. |
| data-learn | `rule_money_in_cents` | E | "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)"; đề chỉ nói `north_q1_revenue` là "number". |
| data-learn | `rule_meta_block` | E | "RULE: answer.json has an object `meta` = {source, rows_in, rows_used}"; thông điệp cuối chỉ nêu `answer.json` với các khóa của đề. |
| data-learn | `rule_clean_csv` | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents …"; không có `write_file` nào cho `clean.csv`. |
| logs-learn | `rule_service_names` | E | "RULE: service names … lower-case with '-' replaced by '_' (payment-service -> payment_service)". |
| logs-learn | `rule_sorted_errors` | E | "RULE: `errors` is sorted by service, then by timestamp_utc, ascending". |
| logs-learn | `rule_schema_header` | E | "RULE: the top-level object has \"schema_version\": 2 and \"generated_by\": \"log-triage\"". |

**Bằng chứng phủ định cho nhóm A–D và F** (`python scripts/check_breakdown.py`): check kỹ thuật `baseline` đạt **18/18**, check quy ước đạt **0/9**.
- A (bỏ qua đặc tả): tác tử đọc `workspace/README.md` trong `data-learn` và `logs-learn`; đọc mọi tệp nguồn và `tests/test_report.py` trong `code-learn`. Các check theo docstring (`low_stock_follows_docstring`, `csv_quoting_follows_docstring`) đều đạt.
- B (không kiểm chứng): `code-learn` chạy `pytest` trước và sau khi sửa; `visible_suite_passes` đạt.
- C (vá triệu chứng): `other_caller_fixed` đạt, tức lỗi được sửa ở hàm dùng chung `parse_price`.
- D (dữ liệu bẩn): `duplicate_rows_removed`, `missing_amount_orders` (giá trị `-999`), `timestamps_utc`, `repeat_counts` đều đạt.
- F (báo cáo sai sự thật): thông điệp cuối của cả ba lần chạy chỉ nêu các tệp thực sự được tạo hoặc sửa.

**Nhận xét.** 9/9 check thất bại (100%) thuộc nhóm E. Nguyên nhân chung: đề chỉ nói "checked by Acme's review bot against the Acme … conventions" mà không nêu nội dung; `grep` trên các workspace học cho thấy quy ước không có trong README hay CHANGELOG. Vì vậy không có cách nào đạt các check này nếu chưa nhận phản hồi. Đây đúng là loại lỗi mà skill có thể phòng ngừa: phản hồi `detail` phát biểu chính xác quy tắc, curator chỉ cần chuyển nó thành chỉ dẫn. Lỗi hạ tầng (xem mục 9: lỗi CRLF làm `tests_not_modified` thất bại giả trong `results-crlf/`) không được dùng làm bằng chứng.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế), trong `src/lab/subagents.py`:
  - `explorer`: chỉ đọc, báo cáo yêu cầu, định dạng, quy ước và bẫy dữ liệu kèm ví dụ. Lý do: tách việc đọc đặc tả (nhóm lỗi A) khỏi việc làm.
  - `implementer`: thực hiện thay đổi, chạy test hoặc script, báo cáo tệp đã đổi. Lý do: giữ ngữ cảnh của tác tử chính gọn.
  - `reviewer`: kiểm tra độc lập theo đề và quy ước, không sửa. Lý do: phòng nhóm lỗi B và F.
  - Mọi `description` nêu *khi nào* gọi ("Use BEFORE…", "Use to carry out…", "Use AFTER…").
- `subagent_calls` ở từng tác vụ và nhận xét: `code-learn` 3 (explorer → implementer → reviewer), `data-learn` 2 (explorer → implementer), `logs-learn` 2 (explorer → implementer). Tác tử chính luôn giao việc, đúng theo `SUBAGENTS_NOTE`, nhưng chỉ gọi `reviewer` ở 1/3 tác vụ. Ở `data-learn` và `logs-learn`, nó tự kiểm tra bằng `read_file` và `execute` sau khi `implementer` trả về.
- Thông tin thiếu hoặc thừa khi giao việc:
  - Lời giao cho `explorer` rất ngắn (200–205 ký tự, ví dụ "Inspect workspace README and sales CSV, determine data conventions …"). Lời giao cho `implementer` dài và chép lại gần đủ đặc tả của đề (1 021–1 221 ký tự).
  - Có việc làm thừa: sau khi `explorer` báo cáo, tác tử chính vẫn tự `ls` và `read_file` lại chính các tệp đó (code-learn: 4 lần `read_file` ngay sau `task(explorer)`). Vậy báo cáo của subagent được kiểm tra lại, nhưng phải trả bằng token.
  - Thông tin cần nhất (quy ước Acme) không có ở đâu để truyền đi, nên giao việc không thể bù đắp nhóm lỗi E: điểm `subagents` = `baseline` ở cả 3 tác vụ (7/10, 5/8, 6/9).
- Ảnh hưởng đến token và thời gian: token trung bình 101 756 so với 42 992 (**×2,37**). Từng tác vụ: code 128 075 so với 48 949, data 77 063 so với 39 623, logs 100 132 so với 40 405. Thời gian tăng khoảng 3,5 lần (172,8 s / 97,3 s / 94,6 s so với 50,6 s / 27,3 s / 26,4 s). `trace.md` chỉ có luồng chính nên token nằm phần lớn ở các lượt gọi bên trong subagent mà vết không hiện.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: **3 lần** (lần đầu và 2 lần chạy lại, đúng giới hạn). Không sửa tay skill nào. Bản lưu của mọi thế hệ nằm trong `results-curator-gen1/`.
  - **Thế hệ 1** (3 skill: `repository-fix-compliance`, `data-cleaning-output-contracts`, `log-output-normalization`): hợp lệ về định dạng nhưng viết quy ước dạng có điều kiện ("emit integer cents wherever required", "Sort `errors` … when specified", "include every required top-level key and exact constant value" mà không nêu hằng số). Chạy thử trên tác vụ học (`results-curator-gen1/skills-auto/`): code 10/10, data **5/8 dù đọc cả 3 skill**, logs 8/9 (trượt `rule_schema_header`). Vết `data-learn` cho thấy tác tử đọc skill rồi chỉ ghi `answer.json`: vì đề không "specify" quy ước nên chỉ dẫn có điều kiện không kích hoạt. Chuyển cả 3 sang `skills-gen1/` (xóa khỏi `skills/auto/`). Lý do: sai so với `detail` (yếu hơn quy tắc; ví dụ type hint chỉ cho hàm "you add or modify" trong khi quy tắc là mọi hàm public).
  - Sửa prompt curator (mã của sinh viên, `src/lab/curator.py`): dòng `RULE:` là quy ước không có trong đề, phải viết thành mệnh lệnh không điều kiện, giữ đúng tên tệp, khóa và hằng số.
  - **Thế hệ 2** (chạy lại lần 1): ghi `python-package-fix-workflow`, `log-triage-output-conventions`. Skill dữ liệu `sales-data-output-conventions` bị `validate_skill` loại vì "mentions evaluation material: orders". Bộ chặn rò rỉ hoạt động; từ "orders" lấy từ chính câu RULE của tác vụ học nhưng trùng với tên tệp của tác vụ đánh giá.
  - Thêm vào prompt chỉ dẫn chung "dùng danh từ chung (record, row, entity…) thay danh từ riêng của một bộ dữ liệu". Chỉ dẫn này không chứa thông tin nào của tác vụ đánh giá.
  - **Thế hệ 3** (chạy lại lần 2, giữ nguyên 2 skill thế hệ 2 trong thư mục): ghi `python-package-maintenance`, `tabular-data-outputs`, `log-json-outputs`. Xóa 2 skill thế hệ 2 vì trùng chức năng. `python-package-fix-workflow` có `description` hẹp ("…package that **requires** regression tests and changelog updates", trong khi đề không bao giờ nói vậy nên tác tử có thể không chọn đọc). `log-triage-output-conventions` trùng nội dung với `log-json-outputs` và chứa tên dịch vụ của dữ liệu học (`payment-service`). Bộ skill cuối (đóng băng) gồm 3 skill của thế hệ 3.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `python-package-maintenance` | Tổng quát cho mọi gói Python: không nêu tên gói, hàm hay tệp nguồn nào; `tests/test_regressions.py`, `CHANGELOG.md`, `## Unreleased` là tên do quy ước yêu cầu. | Đúng, khớp cả 3 `detail` (type hint cho **mọi** hàm public, ≥3 test hồi quy, định dạng bullet changelog). Bước 4 (chạy test từ thư mục gốc, điều tra lỗi collection) là quy trình đúng. | 5 dòng thân. `description` rộng: "Use when fixing bugs or adding tests and documentation in a Python package." Được đọc ở `code-learn` (`skills_read=1`); điểm 7/10 → **10/10**. |
| `tabular-data-outputs` | Phần lớn tổng quát (cent, `meta`, chống trùng, UTC). **Có chi tiết riêng của dữ liệu học**: header `order_id,timestamp_utc,region,amount_cents` và tên vùng `North/South/East/West`, chép từ quy tắc nên được phép, nhưng gắn với một lược đồ cụ thể. | Đúng với tác vụ học (khớp `detail` từng chữ). Rủi ro: trên bộ dữ liệu khác cột, bước 3–4 có thể sai hoặc không áp dụng được (xem H3). | 6 dòng thân. `description`: "Use when analyzing tabular records and producing structured JSON or cleaned CSV outputs." Được đọc ở `data-learn` (`skills_read=1`); 5/8 → **8/8**. |
| `log-json-outputs` | Tổng quát cho log → JSON; tên khóa (`errors`, `timestamp_utc`, `schema_version`, `generated_by`) là quy ước. | Đúng, khớp 3 `detail`. | 5 dòng thân. `description`: "Use when parsing logs into structured JSON error records and service summaries." Được đọc ở `logs-learn` (`skills_read=1`); 6/9 → **9/9**. |

Ở Phần 3.4 (`results/skills-auto-dev/`), mỗi tác vụ đọc đúng 1 skill của họ mình, không đọc skill của họ khác, và `skills_modified=false`. Token trung bình 51 942 (×1,21 so với `baseline`).

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
