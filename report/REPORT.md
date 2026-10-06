# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Hải Nam | 2A202602476 | Toàn bộ (cá nhân): cài đặt harness, chạy thí nghiệm, đánh giá skill, báo cáo |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: OpenAI `gpt-6-luna` qua cổng tương thích OpenAI (`AZURE_OPENAI_ENDPOINT=https://api.openai.com/v1`, đi nhánh `ChatOpenAI` của `model.py`); `LAB_TEMPERATURE=1` (mô hình từ chối `temperature=0`: "Only the default (1) value is supported"); `recursion_limit=60` (mặc định).
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, langchain-openai 1.6.7; máy chủ Windows 11, mọi lần chạy tác tử và `pytest` diễn ra trong Docker (`python:3.12-slim`, `Dockerfile` của lab); `git`, `verify_freeze.py`, `check_breakdown.py` chạy trên máy chủ với `PYTHONPATH=src`.
- Số lần chạy tác vụ đã dùng / ngân sách: **48 lần chạy có kết quả** + 1 lần bị ngắt (máy dừng giữa chừng, không có `run.json`, đã chạy lại) + 3 lần gọi curator. Chi tiết: 6 lần chạy tác vụ học bị loại do lỗi CRLF (`results-crlf/`, xem mục 9), 6 lần tác vụ học chính thức, 3 lần thử skill thế hệ 1 (`results-curator-gen1/`), 3 lần Phần 3.4 (`results/skills-auto-dev/`), 12 lần chính thức sau `freeze`, 18 lần lặp cho thử thách 6e. Tổng 3 367 813 token input + 189 227 token output ≈ 0,43 USD theo giá niêm yết của `gpt-6-luna` (0,10 / 0,50 USD mỗi triệu token). Đề không đặt ngân sách cố định.
- Commit của tag `freeze`: `aca12f0` ("freeze skills", 2026-10-06 12:43:53 +07:00); giả thuyết ở commit `1feb37c` ("hypotheses") ngay trước đó.

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

`report/table.md` (sinh bởi `python -m lab.compare`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 5/8 | 8/8 |
| logs-learn | 6/9 | 6/9 | 9/9 |
| code-eval | 7/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 7/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.66 | 0.66 | 1.00 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.86 |
| **Mean tokens per run** | 52,017 | 117,985 | 68,794 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

`python scripts/check_breakdown.py` (chạy sau tag `freeze`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          61,041      0/3
baseline      learn    18/18         0/9           42,992      0/3
subagents     eval     18/18         0/12         134,213      0/3
subagents     learn    18/18         0/9          101,756      0/3
skills-auto   eval     18/18         8/12          72,056      3/3
skills-auto   learn    18/18         9/9           65,532      3/3
```

Check thất bại của `skills-auto` trên tác vụ đánh giá: `code-eval` → `rule_version_bump`; `data-eval` → `rule_clean_csv`, `rule_sorted_keys_format`; `logs-eval` → `rule_source_line`.

Lần chạy có `error` hoặc `skills_modified = true`: **không có** trong `results/`; mọi `skills_modified` đều `false`. Sự cố và cách xử lý:
- **Lỗi CRLF** (hạ tầng): 6 lần chạy tác vụ học đầu tiên bị loại và chuyển sang `results-crlf/` (mục 9).
- **Ngắt giữa chừng**: lần chạy `skills-auto --tasks all` đầu tiên bị dừng khi máy ngắt phiên, chỉ để lại thư mục `code-eval` rỗng. Đã xóa thư mục rỗng và chạy lại toàn bộ 6 tác vụ (đều sau tag).
- **`verify_freeze.py` trên Windows** báo sai vì hai lý do: `hash_skills` đưa dấu phân cách `\` của Windows vào hash, và `skills/auto/README.md` (tệp có sẵn) bị checkout thành CRLF. Chạy trên một bản `git clone` sạch trong Linux (như quy trình chấm) cho kết quả **`checked 6 runs of skill conditions: OK`**.

## 8. Phân tích

**Đính chính về giả thuyết.** H1 và H3 (commit `1feb37c`) trích điểm trung bình tác vụ học là "0,631". Đó là số của 6 lần chạy bị lỗi CRLF đã loại; số đúng của `baseline` và `subagents` là **0,664**. Giả thuyết được giữ nguyên như đã commit; hướng dự đoán không phụ thuộc vào con số này.

1. **Tác vụ học:** chỉ `skills-auto` cải thiện, 0,664 → **1,000** (+0,336); `subagents` = `baseline` = 0,664. **Tác vụ đánh giá:** chỉ `skills-auto` cải thiện, 0,597 → **0,862** (+0,265); `subagents` = 0,597.
   - Không có điều kiện nào cải thiện tác vụ học mà không cải thiện tác vụ đánh giá. Tuy vậy mức tăng của `skills-auto` giảm khi chuyển sang tác vụ đánh giá (+0,336 → +0,265) và không còn đạt tuyệt đối (code 10/11, data 7/9, logs 9/10). Đây là dấu hiệu **tổng quát hóa một phần**: phần chuyển giao là các quy ước dùng chung, phần mất là quy ước mới và chi tiết quá khớp (câu 2 và 5).
   - Đối chiếu giả thuyết: **H1 đúng** (điểm bằng nhau, token ×2,20). **H2 đúng** (0,862 nằm trong khoảng dự đoán 0,80–0,90, phần tăng nằm hoàn toàn ở check quy ước). **H3 đúng** về hướng (mức tăng nhỏ hơn) và cả hai nguyên nhân dự đoán đều quan sát được.
2. **Check kỹ thuật** đạt 18/18 ở mọi điều kiện và vai trò, nên skill không giúp và cũng không làm hại nhóm này. **Check quy ước**:
   - Tác vụ học: 0/9 → 9/9.
   - Tác vụ đánh giá: 0/12 → 8/12. Trong 12 check quy ước của tác vụ đánh giá có 9 check tái sử dụng quy ước của tác vụ học và 3 check **mới** (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`). Skill giúp đạt **8/9** check tái sử dụng (trượt `rule_clean_csv`) và **0/3** check mới.
   - Lý do: curator chỉ học từ phản hồi `detail` của tác vụ học. Ba quy ước mới không bao giờ xuất hiện ở đó, không có trong đề, và `detail` của tác vụ đánh giá luôn rỗng. Ví dụ: vết `code-eval` cho thấy tác tử đọc `bookings/__init__.py` (kết quả: `__version__ = "1.4.2"`) nhưng không tăng số phiên bản, vì không có gì nói phải làm vậy.
3. **Một check skill giúp đạt: `rule_schema_header` (`logs-eval`).**
   - `skills_read=1`; vết cho thấy lệnh đầu tiên là `read_file /skills/log-json-outputs/SKILL.md`, có dòng "Always include top-level `\"schema_version\": 2` and `\"generated_by\": \"log-triage\"`". Check đạt ở 3/3 lần lặp, trong khi `baseline` đạt 0/3.
   - Đối chứng cho thấy nội dung skill là yếu tố quyết định: skill thế hệ 1 chỉ ghi "include every required top-level key and exact constant value" mà không nêu hằng số, và với skill đó chính check này **thất bại** ở `logs-learn` (`results-curator-gen1/`).

   **Một check skill không giúp: `rule_clean_csv` (`data-eval`).**
   - Skill được đọc (`skills_read=1`, lần lặp 1 đọc cả 3 skill) và **được làm theo đúng từng chữ**: vết có `writerow(['order_id', 'timestamp_utc', 'region', 'amount_cents'])` và ghi chuỗi rỗng vào cột `region` cho mọi dòng.
   - Quy ước của tác vụ đánh giá (đọc `check.py` sau tag `freeze`) yêu cầu header `order_id,timestamp_utc,category,amount_cents`. Đây là trường hợp *skill sai do quá khớp*, không phải skill không được đọc.
   - Cùng tác vụ đó, `rule_money_in_cents` và `rule_meta_block` đạt: phần tổng quát của cùng skill vẫn chuyển giao được.
4. **Chi phí.** Token trung bình mỗi lần chạy trên tác vụ đánh giá (bảng mục 7): `baseline` 61 042, `subagents` 134 214 (**×2,20**), `skills-auto` 72 056 (×1,18).
   - Trên 9 lần chạy đánh giá mỗi điều kiện (kết quả chính + 2 lần lặp, thử thách 6e): 49 199 / 120 120 / 61 855 token. Điểm trên 100k token là **1,21 / 0,50 / 1,39**, nên `skills-auto` hiệu quả nhất: điểm tăng 44% mà token chỉ tăng khoảng 26%.
   - Chưa tính chi phí một lần của curator (3 lần gọi, runner không đo).
   - **Đa tác tử không đáng chi phí** trong thí nghiệm này: không tăng điểm ở bất kỳ tác vụ nào, tốn ×2,2–2,4 token và ×2,5–3,5 thời gian. Nguyên nhân là lỗi duy nhất (quy ước không có trong đề) không giải được bằng cách chia việc.
5. **Rò rỉ:**
   - Prompt của curator chỉ chứa lần chạy tác vụ học (`role == "learn"`, kiểm bởi `test_04`).
   - Bộ chặn `validate_skill` đã **loại** một skill thế hệ 2 chứa từ `orders`. Từ này lấy từ câu RULE của tác vụ học nhưng trùng tên tệp của tác vụ đánh giá; vì quy tắc so khớp chuỗi đơn giản nên đây có thể là chặn giả, nhưng an toàn.
   - Bộ skill cuối qua `validate_skill` không có vấn đề nào và không chứa định danh của tác vụ đánh giá.

   **Quá khớp:**
   - `tabular-data-outputs` ghi cứng header `order_id,timestamp_utc,region,amount_cents` và tên vùng `North/South/East/West` của dữ liệu học. Trên dữ liệu đánh giá (cột `category`), chi tiết này **gây hại** như câu 3 đã phân tích.
   - Biện pháp đã dùng: thêm vào prompt curator chỉ dẫn "dùng danh từ chung thay danh từ riêng của một bộ dữ liệu", và xóa skill chứa tên dịch vụ cụ thể (`payment-service`).
   - Các biện pháp này chưa đủ vì chính câu RULE của tác vụ học chứa tên cột. Đề xuất: curator nên trừu tượng hóa thành "header = khóa định danh, timestamp_utc, *cột phân loại của bộ dữ liệu*, amount_cents".
6. **Nhiễu.**
   - Cùng bộ skill trên tác vụ học: Phần 3.4 (`results/skills-auto-dev/`) đạt 10/10, 8/8, 9/9; sau `freeze` cũng đạt 10/10, 8/8, 9/9. **Chênh lệch điểm 0,000.** Token thì khác: trung bình 51 942 so với 65 533 (+26%), riêng `code-learn` 81 306 so với 120 903 (+49%).
   - Thử thách 6e (phụ lục) cho cùng kết luận trên tác vụ đánh giá: dao động điểm bằng 0 ở cả 9 ô, dù mô hình chạy ở `temperature=1`.
   - Hệ quả:
     - Chênh lệch điểm +0,265 của `skills-auto` lớn hơn nhiều so với nhiễu quan sát được.
     - Chênh lệch token ×2,2 của `subagents` cũng vượt nhiễu.
     - Phần token tăng thêm ×1,18 của `skills-auto` nằm trong vùng dao động token giữa các lần chạy (±26–49%), nên không đủ để kết luận skill làm tăng chi phí.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô nhỏ:** 3 tác vụ mỗi vai trò, 12 check quy ước ở tác vụ đánh giá, trong đó chỉ 3 check là quy ước mới. Mức tăng 0,265 và tỉ lệ 0/3 cho quy ước mới dựa trên rất ít điểm dữ liệu, nên không thể suy ra cho tác vụ khác loại. Kết luận chỉ nên hiểu là "trên 3 họ tác vụ này".
2. **Một mô hình duy nhất, nhiệt độ bắt buộc bằng 1:** `gpt-6-luna` từ chối `temperature=0`, nên điều kiện khác với hướng dẫn (`LAB_TEMPERATURE=0`) và khác các nhóm dùng mô hình khác. Điểm ổn định tuyệt đối qua 3 lần lặp có thể là đặc điểm riêng của mô hình này; với mô hình yếu hơn, nhiễu điểm có thể lớn và bảng mục 7 cần nhiều lần lặp hơn.
3. **Thiết kế tác vụ ưu ái skill:** toàn bộ lỗi của `baseline` là quy ước chỉ biết được qua phản hồi (nhóm E), còn check kỹ thuật đã bão hòa 18/18. Vì vậy thí nghiệm chỉ đo được giá trị của skill ở vai trò "truyền quy ước", không đo được khả năng cải thiện kỹ năng kỹ thuật. Đây cũng là lý do kết quả khác với trung bình của SkillsBench.
4. **Bậc tự do của người làm thí nghiệm:** prompt curator được sửa 2 lần sau khi xem kết quả thế hệ 1 trên tác vụ học (trong giới hạn 2 lần chạy lại, trước `freeze`, không dùng dữ liệu đánh giá). Nếu giữ thế hệ 1, `data` có thể không cải thiện (thế hệ 1 đạt 5/8 trên `data-learn`). Con số 0,862 là của **quy trình curator đã chỉnh**, không phải của curator "nguyên bản".
5. **Vết không đầy đủ:** `trace.md` chỉ có luồng chính và cắt mỗi mục ở 1 500 ký tự; việc subagent làm bên trong không hiện ra. Các giải thích cơ chế ở mục 5 và 8 (ví dụ header `clean.csv`) dựa trên phần vết còn lại, nên không loại trừ được hoàn toàn cách giải thích khác.
6. **Sự cố hạ tầng đã xử lý:**
   - Với `core.autocrlf=true`, Windows checkout `tasks/` thành CRLF, làm `tests_not_modified` thất bại giả (hash `efb5e7…` so với `79e05f…` của bản gốc) và thêm `\r` vào dữ liệu.
   - Mọi lần chạy hợp lệ dùng bản `tasks/` xuất nguyên gốc từ git (`git -c core.autocrlf=false archive HEAD tasks`), gắn **chỉ đọc** đè lên `/lab/tasks` trong Docker. Tệp trong kho không bị sửa.
   - 6 lần chạy bị ảnh hưởng được giữ ở `results-crlf/` và không dùng làm bằng chứng.

## 10. Kết luận

Trên 3 họ tác vụ với mô hình `gpt-6-luna`, skill do curator tự sinh từ phản hồi của tác vụ học nâng điểm trung bình tác vụ đánh giá từ 0,597 lên 0,862 với chi phí token gần như không đổi, còn đa tác tử không tăng điểm mà tốn gấp khoảng 2,2 lần token. Toàn bộ phần tăng đến từ các quy ước được tái sử dụng (8/9 check); skill không giúp được quy ước mới (0/3). Ở một chỗ, skill còn gây hại do chép nguyên chi tiết của dữ liệu học (header `clean.csv`). Điểm ổn định tuyệt đối qua 3 lần lặp, nên các chênh lệch điểm trên là thật với cấu hình này, dù quy mô quá nhỏ để khái quát. Đề xuất tiếp theo: cho curator trừu tượng hóa tên cột và tên tệp riêng của bộ dữ liệu thành vai trò của chúng, rồi đo lại trên một tập tác vụ đánh giá lớn hơn có nhiều quy ước mới.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự).** Mọi lệnh `python` chạy trong Docker với
  `docker run --rm --env-file .env -v "${PWD}:/lab" -v "<bản xuất tasks LF>:/lab/tasks:ro" lab-deepagents …`.
  Bản xuất được tạo bằng `git -c core.autocrlf=false archive HEAD tasks | tar -x -C <thư mục>`.
  1. `docker build -t lab-deepagents .`; `pytest` (29 passed); kiểm tra mô hình bằng `make_model().invoke('Reply with OK')`; `python scripts/tour.py`.
  2. (Bị loại, CRLF) `python -m lab.runner --condition baseline --tasks data-learn`, `… --tasks code-learn logs-learn`, `--condition subagents --tasks learn` → chuyển sang `results-crlf/`.
  3. `python -m lab.runner --condition baseline --tasks learn`; `python -m lab.runner --condition subagents --tasks learn`.
  4. `python -m lab.curator` (thế hệ 1); `python -m lab.runner --condition skills-auto --tasks learn --results results-curator-gen1`; chuyển skill thế hệ 1 sang `results-curator-gen1/skills-gen1/`.
  5. Sửa prompt curator; `python -m lab.curator` (thế hệ 2); sửa prompt lần nữa; `python -m lab.curator` (thế hệ 3); chuyển 2 skill thế hệ 2 sang `results-curator-gen1/deleted/`.
  6. `python -m lab.runner --condition skills-auto --tasks learn`; `mv results/skills-auto results/skills-auto-dev`.
  7. `git commit -m "hypotheses"`; `git commit --allow-empty -m "freeze skills"`; `git tag freeze`.
  8. `python -m lab.runner --condition baseline --tasks eval`; `… --condition subagents --tasks eval`; `… --condition skills-auto --tasks all` (lần đầu bị ngắt, chạy lại toàn bộ).
  9. `python scripts/verify_freeze.py` (trên bản `git clone` sạch trong Linux, image có git); `python -m lab.compare > report/table.md`; `python scripts/check_breakdown.py`.
  10. Thử thách 6e: `for rep in 1 2; for c in baseline subagents skills-auto: python -m lab.runner --condition $c --tasks eval --results results-rep$rep`; `python extras/noise_summary.py results results-rep1 results-rep2 --role eval > report/noise.md`.

- **Thử thách mở rộng – hướng 6e: lặp lại để đo nhiễu.**
  - *Thiết kế.* Chạy lại cả 3 điều kiện trên 3 tác vụ đánh giá thêm 2 lần, tức 18 lần chạy, với cùng bộ skill đã đóng băng và sau tag `freeze`. Kết quả ghi vào thư mục riêng `results-rep1/` và `results-rep2/`, nên không ảnh hưởng `results/`, `lab.compare` hay `verify_freeze.py`. Tổng hợp bằng script mới `extras/noise_summary.py`: chỉ đọc `run.json`, không gọi mô hình, không sửa tệp có sẵn. Kết quả ở `report/noise.md`.
  - *Số liệu* (3 lần chạy mỗi ô; điểm từng lần, trung bình, dao động; token trung bình):

    | Điều kiện | code-eval | data-eval | logs-eval | Điểm TB (9 lần) | Token TB | Điểm / 100k token |
    |---|---|---|---|---|---|---|
    | baseline | 0,64 ×3 (dao động 0) | 0,56 ×3 (0) | 0,60 ×3 (0) | 0,597 | 49 199 | 1,21 |
    | subagents | 0,64 ×3 (0) | 0,56 ×3 (0) | 0,60 ×3 (0) | 0,597 | 120 120 | 0,50 |
    | skills-auto | 0,91 ×3 (0) | 0,78 ×3 (0) | 0,90 ×3 (0) | 0,862 | 61 855 | 1,39 |

    Check kỹ thuật đạt 54/54 ở cả 3 điều kiện. Check quy ước: 0/36, 0/36, 24/36. Dao động token giữa các lần: `subagents code-eval` 152 699–214 109; `baseline code-eval` 54 083–124 453; `skills-auto code-eval` 95 058–155 057.
  - *So với kết quả chính.* Điểm trung bình của 9 lần trùng hoàn toàn với 1 lần chạy chính (0,597 / 0,597 / 0,862), nên bảng ở mục 7 không bị nhiễu điểm làm lệch. Token trung bình của 9 lần thấp hơn của lần chạy chính (ví dụ `baseline` 49 199 so với 61 042), cho thấy con số token của một lần chạy đơn lẻ không đáng tin bằng con số điểm.
  - *Cơ chế (từ vết).* Ba lần chạy `skills-auto` của mỗi tác vụ trượt **đúng cùng các check**:
    - `rule_version_bump`: 3/3 lần.
    - `rule_clean_csv` + `rule_sorted_keys_format`: 3/3 lần.
    - `rule_source_line`: 3/3 lần.

    Mỗi lần đều đọc đúng skill của họ mình (`skills_read` ≥ 1, `skills_modified=false`). Như vậy thất bại là có hệ thống (skill thiếu quy ước mới hoặc chứa chi tiết quá khớp), không phải ngẫu nhiên. Ở `temperature=1`, mô hình thay đổi đường đi (số tool call 18–29 ở `baseline code-eval`), nhưng các check nhị phân chỉ phụ thuộc vào việc tác tử *có biết* quy ước hay không, nên điểm không đổi.
  - *Hạn chế và bước tiếp theo.*
    - 3 lần mỗi ô vẫn ít: dao động 0 không chứng minh phương sai bằng 0, chỉ cho thấy phương sai nhỏ hơn độ phân giải của 9–11 check.
    - Lặp lại chưa bao gồm curator: chạy curator nhiều lần sẽ cho nhiều bộ skill khác nhau, và đó mới là nguồn biến thiên lớn nhất (thế hệ 1 so với thế hệ 3 khác nhau 3 check trên `data-learn`).
    - Bước tiếp theo: lặp curator 3–5 lần, mỗi bộ skill đo 3 lần, để tách phương sai do curator khỏi phương sai do tác tử.
  - *Tái lập.* `extras/noise_summary.py` có docstring và lệnh mẫu; toàn bộ `run.json` và `trace.md` của các lần lặp nằm trong `results-rep1/` và `results-rep2/`.

- **Ghi chú khác.**
  - `final_message` của 6 lần chạy trong `results-crlf/` lưu nguyên danh sách content block (có cả reasoning đã mã hóa) vì mô hình trả về theo định dạng Responses API. `run_task` đã sửa sang `messages[-1].text` trước mọi lần chạy hợp lệ.
  - Tìm mẫu `sk-…` trong `results/` có khớp một chuỗi ngẫu nhiên bên trong khối reasoning mã hóa. Đối chiếu trực tiếp với khóa trong `.env` cho thấy không tệp nào chứa khóa API.
