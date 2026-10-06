# CHECKLIST thực hiện Lab: Self evolving Agentic (Deep Agents)

> Checklist cá nhân, tổng hợp từ `README.md`, `GUIDE.md`, `RUBRIC.md`, `REPORT_TEMPLATE.md` và `guides/pseudocode/`.
> Đánh dấu `[x]` khi xong. Làm **đúng thứ tự**: thứ tự các bước là một phần của điểm (giả thuyết trước `freeze`, `freeze` trước khi chạy tác vụ đánh giá).

## Trạng thái hiện tại (cập nhật 2026-10-06)

| Phần | Trạng thái |
|---|---|
| 0. Cài đặt, làm quen | Xong, trừ việc sửa CRLF (xem 0.1) |
| 1. Harness (30 điểm tự động) | Xong: 29/29 test đạt, đã commit `0c0234b`; bản sửa `final_message` chưa commit |
| 2. Tác vụ học + phân loại lỗi | ⚠️ Đã chạy 6 lần nhưng **kết quả không hợp lệ do lỗi CRLF**, phải chạy lại; chưa phân loại lỗi |
| 3. Curator | Mới cài xong `curate_skills`; chưa chạy curator, chưa có skill |
| 4. Giả thuyết, freeze, chạy chính thức | Chưa làm |
| 5. Báo cáo | Mới điền mục 1 và mục 3 |
| 6. Bonus (+5) | Chưa làm |

**Việc chặn tiếp theo:** sửa CRLF ở mục 0.1 (bạn tự chạy lệnh), sau đó chạy lại toàn bộ Phần 2.

---

## Luật vàng (vi phạm = trừ 10 điểm mỗi lỗi)

- [x] KHÔNG sửa `tests/`, `tasks/`, `scripts/`, `model.py`, `tasks.py`, `grading.py`, `testing.py`, `compare.py`.
- [x] KHÔNG sửa các phần "CÓ SẴN" trong file sinh viên: hằng số `PATHS_NOTE`, `BASE_PROMPT`, `SKILLS_NOTE`, `SUBAGENTS_NOTE` (agent.py); `render_trace`, `main`, `CONDITIONS` (runner.py); `validate_skill`, `parse_skill_blocks` (curator.py). Chỉ cài các hàm `TODO`.
- [x] KHÔNG sửa tay nội dung `skills/auto/` (chỉ được xóa skill hoặc chạy lại curator, tối đa 2 lần, có ghi lý do).
- [x] KHÔNG mở `tasks/*-eval/check.py`, không chạy tác vụ `eval` trước khi có tag `freeze`.
- [x] KHÔNG commit `.env`, không để khóa API lọt vào `results/`, `trace.md`, báo cáo.
- [ ] Số liệu trong báo cáo phải khớp `results/` (giảng viên chạy lại `lab.compare`). *(kiểm tra lại khi viết báo cáo)*

---

## Phần 0. Cài đặt và làm quen

### 0.1. Môi trường (lưu ý riêng cho Windows)

Shell của tác tử dùng `/bin/sh` và `PATH` dạng Linux (`:`), nên trên Windows **phải chạy trong Docker** (hoặc cài WSL Ubuntu). Máy hiện có Docker 28.5, WSL chỉ có `docker-desktop` → dùng Docker.

- [x] Tạo `.env` từ mẫu: `Copy-Item .env.example .env`
- [x] Điền `.env` (chọn **một** cách, không để dấu nháy quanh giá trị vì `--env-file` của Docker không bỏ nháy):
  - Cách 1: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT_MODEL` (giá trị giảng viên cấp).
  - Cách 2: `LAB_MODEL=deepseek:deepseek-chat` + `DEEPSEEK_API_KEY`.
  - Giữ `LAB_TEMPERATURE=0`. **Thực tế:** đang dùng OpenAI `gpt-6-luna`, mô hình này chỉ nhận `temperature=1` nên `.env` đặt `LAB_TEMPERATURE=1` (đã ghi vào báo cáo mục 1).
- [x] Kiểm tra `.env` bị ignore: `git status` không được thấy `.env`.
- [x] Tạo báo cáo: `New-Item -ItemType Directory -Force report; Copy-Item REPORT_TEMPLATE.md report/REPORT.md`
- [x] Build image (PowerShell, ở gốc repo): `docker build -t lab-deepagents .`
- [x] Vào container: `docker run --rm -it --env-file .env -v "${PWD}:/lab" lab-deepagents`
  - Mọi lệnh `pytest`, `python -m lab.runner`, `python -m lab.curator`, `python -m lab.compare` chạy **trong container**.
  - Nếu trong container báo `ModuleNotFoundError: lab` → chạy lại `pip install -e .` trong container.
- [x] Môi trường host (cho các lệnh cần `git`, vì image `python:3.12-slim` không có git):
  `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e .`
  → dùng host cho `git commit/tag`, `python scripts/verify_freeze.py`, `python scripts/check_breakdown.py`.
- [ ] ⚠️ **Sửa CRLF (CHƯA LÀM, đang chặn Phần 2).** Do `core.autocrlf=true`, cả 34 tệp trong `tasks/` đang ở dạng CRLF. Check `tests_not_modified` của `code-learn` vì thế luôn thất bại (hash `efb5e7…` so với bản gốc `79e05f…`), và dữ liệu `.log`/`.csv` có thêm ``. Chạy trong PowerShell ở gốc repo:
  ```powershell
  git config --local core.autocrlf input
  Remove-Item -Recurse -Force tasks
  git checkout -- tasks
  git ls-files --eol tasks | Select-String "w/crlf"   # phải không in ra dòng nào
  ```
  Sau đó cất kết quả cũ (`results` → `results-crlf`) và chạy lại Phần 1.4 + 2.1.

### 0.2. Kiểm tra môi trường

- [x] `pytest tests/test_01_provided.py` → **`12 passed`** (đã chạy cả bộ: 29 passed).
- [x] Kiểm tra kết nối mô hình (tốn rất ít token):
  `python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"` → in `OK`.
- [x] Ghi lại vào báo cáo mục 1: tên mô hình, `LAB_TEMPERATURE`, `recursion_limit` (mặc định 60), `pip show deepagents` (0.7.21), "chạy trong Docker python:3.12-slim".

### 0.3. Làm quen Deep Agents (không tốn token)

- [x] `python scripts/tour.py`
- [x] Trả lời vào **mục 3** của `report/REPORT.md` (rubric 6.4 bắt buộc có):
  - [x] Câu 1: Danh sách công cụ mặc định (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`, ...). Công cụ chạy lệnh: `execute`.
  - [x] Câu 2: Mô tả của `task` nói gì về subagent `general-purpose`; subagent thấy ngữ cảnh nào (chỉ prompt được giao).
  - [x] Câu 3: Trích nguyên văn 1 câu hướng dẫn hành vi trong mô tả `task` và 1 câu trong mô tả `execute`.

---

## Phần 1. Hoàn thiện harness (30 điểm, chấm tự động)

Làm theo thứ tự 1.1 → 1.2 → 1.3 (`build_agent` gọi `get_subagents`).

### 1.1. `src/lab/subagents.py` → `get_subagents()` (đọc `guides/pseudocode/02_subagents.md`)

- [x] Trả về list **≥ 2** dict (khuyến nghị 3), mỗi dict có `name` (duy nhất, chữ thường/gạch ngang), `description`, `system_prompt`.
- [x] Gợi ý 3 vai trò:
  - [x] `explorer`: đọc README, docstring, mẫu dữ liệu, đề bài; báo cáo sự thật và quy ước; **không sửa** tệp.
  - [x] `implementer`: thực hiện thay đổi, chạy test/script, báo cáo tệp đã đổi và kết quả.
  - [x] `reviewer`: kiểm tra độc lập kết quả với đề bài + trường hợp biên; **không sửa**.
- [x] `description` viết như chỉ dẫn hành động: "Use when ..." (khi nào gọi), không chung chung (rubric 3.1).
- [x] `system_prompt` có phạm vi rõ: được làm gì, không được làm gì, báo cáo cuối gồm những gì.
- [x] KHÔNG tự viết quy ước đường dẫn trong `system_prompt` (`build_agent` sẽ nối `PATHS_NOTE`).
- [x] `pytest tests/test_02_agent.py -k subagents`

### 1.2. `src/lab/agent.py` (đọc `guides/pseudocode/01_agent.md`)

- [x] TODO 1 – import: `create_deep_agent`, `LocalShellBackend` (từ `deepagents.backends`), `make_model`, `get_subagents`, `sys`.
- [x] TODO 2 – `make_backend(sandbox)`:
  - [x] `env = {"PATH": str(Path(sys.executable).parent) + ":/usr/local/bin:/usr/bin:/bin", "HOME": str(sandbox), "PYTHONDONTWRITEBYTECODE": "1"}`
  - [x] `LocalShellBackend(root_dir=sandbox, virtual_mode=True, inherit_env=False, env=env, timeout=120)`
  - [x] Tuyệt đối không `inherit_env=True` (lộ khóa API); không quên `env` (mất `python`).
- [x] TODO 3 – `build_agent(sandbox, mode="single", use_skills=False, model=None)`:
  - [x] `mode` ∉ {`single`, `subagents`} → `raise ValueError`.
  - [x] `prompt = BASE_PROMPT`; `kwargs = {}`.
  - [x] Nếu `subagents`: `kwargs["subagents"] = [{**s, "system_prompt": s["system_prompt"] + " " + PATHS_NOTE} for s in get_subagents()]`; `prompt += SUBAGENTS_NOTE`.
  - [x] Nếu `use_skills`: `kwargs["skills"] = ["/skills/"]`; `prompt += SKILLS_NOTE`.
  - [x] `return create_deep_agent(model=model or make_model(), system_prompt=prompt, backend=make_backend(sandbox), **kwargs)`
  - [x] KHÔNG dùng `permissions=` (gây `NotImplementedError`).
- [x] `pytest tests/test_02_agent.py` → **9 passed** (10 điểm).

### 1.3. `src/lab/runner.py` → `run_task(...)` (đọc `guides/pseudocode/03_runner.md`)

- [x] Lấy `cfg = CONDITIONS[condition]`, `task = get_task(task_id)`, `skills_dir = ROOT / cfg["skills_dir"]` hoặc `None`.
- [x] `out = Path(results_dir) / condition / task_id`; `mkdir(parents=True, exist_ok=True)`.
- [x] `sandbox = Path(tempfile.mkdtemp())` – nằm NGOÀI repo.
- [x] `record = {"task", "condition", "role": task.role, "error": None, "timestamp": datetime.now(timezone.utc).isoformat()}`.
- [x] Trong `try:`
  - [x] `prepare_sandbox(task, sandbox, skills_dir)`; `before = hash_dir(sandbox / "skills")`; `record["skills_sha256"] = before`.
  - [x] `agent = build_agent(sandbox, mode=cfg["mode"], use_skills=skills_dir is not None, model=model)`.
  - [x] `usage = UsageMetadataCallbackHandler()` (từ `langchain_core.callbacks`); `t0 = time.time()`.
  - [x] `try: result = agent.invoke({"messages": [{"role": "user", "content": task.instruction}]}, config={"callbacks": [usage], "recursion_limit": recursion_limit})` → `messages = result["messages"]`, `final = messages[-1].text` (dùng `.text`: `gpt-6-luna` trả về danh sách block kèm reasoning mã hóa; bản sửa này chưa commit).
  - [x] `except Exception as e:` → `record["error"] = f"{type(e).__name__}: {e}"`, `messages = []`, `final = ""` (không ném lỗi ra ngoài).
  - [x] `record["seconds"] = round(time.time() - t0, 1)`.
  - [x] `record["tokens"] = {"input", "output", "total"}` = tổng `input_tokens`/`output_tokens`/`total_tokens` trên `usage.usage_metadata.values()`.
  - [x] `calls = [tc for m in messages if isinstance(m, AIMessage) for tc in m.tool_calls]`.
  - [x] `tool_calls = len(calls)`; `subagent_calls` = số call `name == "task"`.
  - [x] `skills_read` = số **tên skill khác nhau** từ các call `read_file` có `"skills/"` trong `args["file_path"]` (tên = phần ngay sau `skills/`, cắt tại `/`; dùng `set`).
  - [x] `skills_modified = hash_dir(sandbox / "skills") != before`; `final_message = final`.
  - [x] `g = grade(task, sandbox / "workspace")`; `record.update(score, passed, total, checks)` từ `g`.
  - [x] Ghi `out / "trace.md"` = `render_trace(messages)` (encoding utf-8).
- [x] `finally:` `shutil.rmtree(sandbox, ignore_errors=True)`.
- [x] Ghi `out / "run.json"` (`json.dumps(record, indent=2, ensure_ascii=False)`, utf-8); `return record`.
- [x] `pytest tests/test_03_runner.py` → **6 passed** (12 điểm).

### 1.4. Chạy thật lần đầu (tính vào kết quả baseline, không chạy lại)

> ⚠️ Đã chạy (5/8, 33k token) nhưng chạy khi `tasks/` còn CRLF → phải chạy lại sau khi sửa 0.1.

- [x] `python -m lab.runner --condition baseline --tasks data-learn`
- [x] Có `results/baseline/data-learn/run.json` và `trace.md`; `tokens.total > 0`; `checks` có danh sách, check thất bại có `detail`.
- [x] Mở `trace.md` kiểm tra không có `python: command not found`, không có `/workspace/...` lỗi, không có khóa API.
- [x] Commit mã: `git add -A; git commit -m "Implement harness: agent, subagents, runner"` (đã commit `0c0234b`)

---

## Phần 2. Chạy tác vụ học và phân loại lỗi (14 + 10 điểm)

### 2.1. Chạy (CHỈ tác vụ học)

> ⚠️ Cả 6 lần đã chạy, không lỗi API, nhưng **không hợp lệ do CRLF** → chạy lại sau khi sửa 0.1. Số liệu tham khảo (lần chạy CRLF): baseline 6/10, 5/8, 6/9 (72.6k, 33.0k, 18.2k token); subagents 6/10, 5/8, 6/9 (171.0k, 106.6k, 62.3k token; `subagent_calls` = 3, 3, 1).

- [x] `python -m lab.runner --condition baseline --tasks code-learn logs-learn`
- [x] `python -m lab.runner --condition subagents --tasks learn`
- [ ] Kiểm tra `results/baseline/` và `results/subagents/` đủ 3 tác vụ học, không có `error` do hạ tầng (nếu có: chạy lại đúng tác vụ đó, ghi chú trong báo cáo).
- [ ] Ghi lại từng lệnh đã chạy vào **Phụ lục** báo cáo (rubric 6.4 – tái lập).

### 2.2. Phân loại lỗi → báo cáo mục 4 (rubric 2.2: 10 điểm)

- [ ] Mở `checks` trong `run.json` + `trace.md` của `code-learn`, `data-learn`, `logs-learn` (điều kiện `baseline`).
- [ ] Mỗi check thất bại = 1 dòng bảng: tác vụ | tên check | nhóm A–G | trích `detail` hoặc vết.
  - A bỏ qua đặc tả · B không kiểm chứng · C vá triệu chứng · D bỏ sót dữ liệu bẩn · **E vi phạm quy ước (`rule_`, `detail` bắt đầu `RULE:`)** · F báo cáo sai sự thật · G khác.
- [ ] Phân loại **≥ 4** check thất bại (mức 9–10 điểm).
- [ ] Chạy `python scripts/check_breakdown.py` (host) → lấy số check kỹ thuật đạt/tổng làm **bằng chứng phủ định** cho A–D nếu hầu hết lỗi là E.
- [ ] Viết nhận xét: nhóm lỗi chiếm đa số, nguyên nhân chung, skill có phòng ngừa được không.
- [ ] Không dùng lỗi hạ tầng (API, timeout) làm bằng chứng.

### 2.3. Quan sát `subagents` → báo cáo mục 5 (rubric 3.3: 4 điểm)

- [ ] Liệt kê subagent đã định nghĩa (tên, vai trò, lý do thiết kế).
- [ ] `subagent_calls` từng tác vụ; subagent nào được gọi, bao nhiêu lần (xem call `task` trong `trace.md`, trường `subagent_type`).
- [ ] Nếu có giao việc: thông điệp giao việc có đủ quy tắc + đường dẫn không? Báo cáo của subagent có được kiểm tra lại không?
- [ ] Nếu `subagent_calls = 0`: ghi nhận là kết quả hợp lệ và giải thích vì sao.
- [ ] So sánh `tokens.total` và `seconds` với `baseline` cùng tác vụ.
- [ ] Commit: `git add -A; git commit -m "Learning runs: baseline and subagents"`

---

## Phần 3. Self-evolving: curator (16 điểm)

### 3.1. Cài `curate_skills` trong `src/lab/curator.py` (đọc `04_curator.md`, `05_skill_quality.md`)

- [x] `out_dir` mặc định `ROOT / "skills" / "auto"` (import `ROOT` từ `.tasks`).
- [x] Duyệt `Path(results_dir) / source_condition / "*" / "run.json"`; **bỏ qua mọi run có `role != "learn"`**.
- [x] Với mỗi run: đọc `trace.md` (nếu có), lấy ~6000 ký tự **cuối**; `failed = [(c["name"], c["detail"]) for c in checks if not c["passed"]]`.
- [x] Nếu không run nào có `failed` → in cảnh báo, `return []` và **không gọi model**.
- [x] Dựng prompt theo mẫu trong `04_curator.md`: max_skills, quy tắc tổng quát/không đáp án/không id tác vụ, khuôn `=== SKILL: <name> === ... === END ===`, rồi mỗi run: tên + `detail` từng check thất bại + vết.
- [x] `reply = (model or make_model()).invoke(prompt).content`.
- [x] Với mỗi `(name, text)` trong `parse_skill_blocks(reply)`: dừng khi đủ `max_skills`; bỏ qua nếu `validate_skill(text, expected_name=name)` có vấn đề; ngược lại ghi `out_dir / name / "SKILL.md"` (mkdir, utf-8, kết thúc bằng `\n`).
- [x] Trả về list đường dẫn đã ghi.
- [x] `pytest tests/test_04_curator.py` → **2 passed** (8 điểm).
- [x] `pytest` (toàn bộ) → tất cả đạt (12 + 9 + 6 + 2 = 29 test).

### 3.2. Chạy curator

- [ ] `python -m lab.curator` → in `wrote .../skills/auto/<name>/SKILL.md`.
- [ ] Nếu báo "không có check thất bại" hoặc không ghi skill nào → kiểm tra lại `results/baseline/`, đọc lý do `validate_skill` từ chối.

### 3.3. Đánh giá từng skill → báo cáo mục 6 (rubric 4.2: 5 điểm)

Với **mỗi** skill trong `skills/auto/`, điền một dòng bảng:

- [ ] Tổng quát hay chỉ lặp lại chi tiết tác vụ học (tên tệp, hàm, cột, con số)?
- [ ] Đúng hay sai: so với `detail` của bot đánh giá; có chỉ dẫn nào gây hại không?
- [ ] Độ dài (số dòng), `description` có bắt đầu "Use when ..." và đủ rộng không?
- [ ] Không rò rỉ: không có tên/con số của tác vụ đánh giá.
- [ ] Nếu xóa skill hoặc chạy lại curator (≤ 2 lần): ghi số lần chạy, skill bị xóa, **lý do**. Không sửa tay nội dung.

### 3.4. Kiểm tra skill có được dùng (chỉ tác vụ học)

- [ ] `python -m lab.runner --condition skills-auto --tasks learn`
- [ ] Xem `skills_read` từng tác vụ (0 = không đọc skill nào); đối chiếu `trace.md` xem có làm theo từng quy tắc không; so với `baseline`.
- [ ] Nếu `skills_read = 0` ở mọi tác vụ → cân nhắc chạy lại curator (vẫn trong giới hạn 2 lần).
- [ ] **Sao lưu kết quả dev** (để ước lượng nhiễu ở mục 8.6): trong container `mv results/skills-auto results/skills-auto-dev`
  (`lab.compare` và `verify_freeze` bỏ qua thư mục đổi tên này).
- [ ] Commit: `git add -A; git commit -m "Curator skills and skills-auto dev runs"`

---

## Phần 4. Giả thuyết → đóng băng → đo lại (10 điểm + liên quan 4.3, 6.1)

### 4.0. Giả thuyết (TRƯỚC khi thấy bất kỳ điểm nào của tác vụ đánh giá)

- [ ] Điền mục 2 `report/REPORT.md`, mỗi dòng phải có nội dung sau dấu `:` (script kiểm tra đúng định dạng `- H1 (...): <nội dung>`):
  - [ ] H1 (subagents so với baseline): dự đoán + lý do (token ~ nhiều hơn, giao việc thiếu quy tắc...).
  - [ ] H2 (skills-auto so với baseline): dự đoán + căn cứ (phân loại lỗi mục 4; SkillsBench: skill tự sinh trung bình không có lợi).
  - [ ] H3 (tác vụ học so với đánh giá): dự đoán về quá khớp (SkillEvolBench), quy ước mới của eval không có trong skill.
- [ ] Commit (host): `git add -A; git commit -m "hypotheses"` (message phải **bắt đầu** bằng `hypotheses`).

### 4.1. Đóng băng

- [ ] Xác nhận `skills/auto/` là bản cuối cùng.
- [ ] (host) `git add -A; git commit --allow-empty -m "freeze skills"; git tag freeze`
- [ ] Từ đây **không đụng** `skills/`.
- [ ] Ghi hash commit của tag vào báo cáo mục 1: `git rev-parse freeze`.

### 4.2. Chạy chính thức (sau tag)

- [ ] `python -m lab.runner --condition baseline --tasks eval`
- [ ] `python -m lab.runner --condition subagents --tasks eval`
- [ ] `python -m lab.runner --condition skills-auto --tasks all`
- [ ] Mọi run có `error` → chạy lại riêng tác vụ đó, ghi chú trong báo cáo mục 7.
- [ ] (host) `python scripts/verify_freeze.py` → **`OK`** (checked 6 runs).
- [ ] Đủ 3 × 6 = 18 thư mục kết quả: `results/{baseline,subagents,skills-auto}/<6 tác vụ>/` (rubric 2.1, 3.2, 4.3).

### 4.3. Bảng so sánh

- [ ] Trong container: `python -m lab.compare > report/table.md`
- [ ] Kiểm tra: 3 cột điều kiện, 6 hàng tác vụ, hàng tổng hợp (điểm TB, token TB, số run có đọc skill).
- [ ] KHÔNG sửa tay `table.md` (giảng viên chạy lại để đối chiếu).

### 4.4. Thống kê hỗ trợ

- [ ] (host) `python scripts/check_breakdown.py` → lưu output để dán vào mục 7.
- [ ] Commit: `git add -A; git commit -m "Official runs, comparison table"`

---

## Phần 5. Báo cáo `report/REPORT.md` (20 điểm)

- [ ] Xóa các dòng hướng dẫn bắt đầu bằng `>`.
- [ ] **Mục 1** – thông tin: họ tên, MSSV (2A202602476), mô hình, nhiệt độ, `recursion_limit`, phiên bản deepagents, OS + Docker, số lần chạy đã dùng, commit `freeze`.
- [ ] **Mục 2** – H1–H3 (đã commit trước `freeze`; không sửa nội dung giả thuyết sau đó, chỉ đánh giá đúng/sai ở mục 8).
- [ ] **Mục 3** – 3 câu trả lời Phần 0.3.
- [ ] **Mục 4** – bảng phân loại lỗi ≥ 4 dòng + nhận xét + bằng chứng phủ định.
- [ ] **Mục 5** – subagents.
- [ ] **Mục 6** – số lần chạy curator, bảng đánh giá từng skill.
- [ ] **Mục 7** – dán `report/table.md` + output `check_breakdown.py`; nêu run có `error`/`skills_modified=true` và cách xử lý.
- [ ] **Mục 8** – trả lời đủ 6 câu, mỗi câu có số liệu (rubric 6.2: 8 điểm):
  - [ ] 8.1 Cải thiện tác vụ học vs đánh giá; dấu hiệu quá khớp nếu chỉ cải thiện tác vụ học.
  - [ ] 8.2 Tách check kỹ thuật vs check quy ước `rule_`; quy ước **mới** ở eval có được skill giúp không, vì sao.
  - [ ] 8.3 Một check skill giúp đạt + một check skill không giúp, dẫn chứng `skills_read` và `trace.md`.
  - [ ] 8.4 Chi phí: token TB mỗi điều kiện, điểm/token, đa tác tử có đáng không.
  - [ ] 8.5 Rò rỉ/quá khớp trong skill và cách phòng tránh.
  - [ ] 8.6 Nhiễu: so `results/skills-auto-dev` (Phần 3.4) với `results/skills-auto` (sau freeze) trên tác vụ học.
- [ ] **Mục 9** – ≥ 3 hạn chế, mỗi cái nêu ảnh hưởng đến kết luận (3 tác vụ/vai trò, chạy 1 lần, nhiễu, tác vụ do giảng viên thiết kế, 1 mô hình, trace không có bên trong subagent).
- [ ] **Mục 10** – kết luận ≤ 5 câu, chỉ khẳng định điều số liệu hỗ trợ, 1 đề xuất cải tiến.
- [ ] **Phụ lục** – danh sách lệnh theo thứ tự; thử thách mở rộng (nếu làm).
- [ ] Đối chiếu mọi con số trong báo cáo với `run.json` / `table.md` (sai lệch bị trừ 5–10).

---

## Phần 6. Thử thách mở rộng (tùy chọn, +5) – chọn MỘT

> Chưa làm. Chỉ được tính điểm khi Phần 0–5 đã hoàn thành.

- [ ] Chỉ làm khi Phần 0–5 đã xong.
- [ ] Gợi ý dễ nhất: **6e – lặp đo nhiễu**: chạy lại mỗi điều kiện trên eval ≥ 2 lần với `--results results-rep1`, `--results results-rep2`; báo cáo trung bình và khoảng dao động.
- [ ] Hoặc **6d – subagent có skill**: thêm `"skills": ["/skills/"]` cho subagent (thư mục kết quả riêng, không phá kết quả chính).
- [ ] Ghi đủ 5 tiêu chí: thiết kế tách biệt, số liệu so sánh, phân tích vết, hạn chế + bước tiếp, mã tái lập được.

---

## Kiểm tra cuối trước khi nộp

- [ ] `pytest` (trong container) → toàn bộ đạt.
- [ ] `python scripts/verify_freeze.py` (host) → `OK`.
- [ ] `python -m lab.compare` khớp với `report/table.md`.
- [ ] `git diff freeze -- skills/` rỗng.
- [ ] `git status` sạch; `.env` không có trong lịch sử: `git log --all -- .env` rỗng.
- [ ] Tìm khóa API bị lộ: `git grep -n -i "api_key\|sk-" -- results report` không ra khóa thật.
- [x] `git diff d982034 --stat -- tests tasks scripts src/lab/model.py src/lab/tasks.py src/lab/grading.py src/lab/testing.py src/lab/compare.py` rỗng (so với `d982034` – commit gốc mới nhất của giảng viên; đã kiểm tra: rỗng).
- [ ] Nộp đủ: 4 file `src/lab/{agent,subagents,runner,curator}.py`, `skills/auto/`, `results/` (run.json + trace.md), `report/REPORT.md`, `report/table.md`.
- [ ] `git push` (kèm tag): `git push; git push origin freeze`

---

## Ngân sách số lần chạy (ghi vào báo cáo mục 1)

| Giai đoạn | Lệnh | Số run |
|---|---|---|
| 1.4 | baseline data-learn | 1 |
| 2.1 | baseline code-learn, logs-learn | 2 |
| 2.1 | subagents learn | 3 |
| 3.2 | curator (1 lần gọi LLM, tối đa 3 lần chạy) | 1–3 |
| 3.4 | skills-auto learn (dev) | 3 |
| 4.2 | baseline eval + subagents eval | 6 |
| 4.2 | skills-auto all | 6 |
| | **Tổng tối thiểu** | **21 run + curator** |

## Xử lý sự cố nhanh

| Triệu chứng | Cách xử lý |
|---|---|
| `python: command not found` trong trace | Sai `PATH` trong `make_backend`. |
| `No such file or directory: '/workspace/...'` | Không sửa `BASE_PROMPT`; kiểm tra subagent đã được nối `PATHS_NOTE`. |
| `NotImplementedError ... permissions` | Bỏ tham số `permissions=`. |
| 401 / `AuthenticationError` | Sai `.env` hoặc giá trị có dấu nháy (Docker `--env-file` giữ nguyên nháy). |
| 404 từ gateway | Sai endpoint/deployment → hỏi giảng viên. |
| 429 | Chạy tuần tự, chờ rồi chạy lại. |
| Run quá dài / tốn token | `--recursion-limit 40`, ghi chú trong báo cáo. |
| `verify_freeze` báo skill khác | Có thể do CRLF sau checkout lại; không sửa `skills/` sau tag. |
| `test_01` báo tác vụ đạt điểm tối đa | Vô tình sửa `tasks/*/workspace` → `git checkout -- tasks/`. |
| `git` không chạy trong container | Chạy git và các script dùng git trên host (venv Windows). |
