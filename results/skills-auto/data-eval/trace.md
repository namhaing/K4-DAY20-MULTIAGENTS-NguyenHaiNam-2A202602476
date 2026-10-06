### Human
Analyse the order events in `workspace/orders.json` (see `workspace/README.md` for the field descriptions).

Write a file `workspace/answer.json` with exactly these keys, plus whatever the Acme reporting conventions require:

- `march_revenue_utc` (number): sum of `total` of the orders placed in March 2024, where the month is determined in **UTC**.
- `march_orders_utc` (integer): number of distinct orders counted in `march_revenue_utc`.
- `top_category` (string): the category with the highest total revenue over the whole file (lowercase name).
- `missing_total_orders` (integer): number of distinct orders whose total is missing.
- `duplicate_events_removed` (integer): number of duplicate events you removed.

Orders with a missing total must not be added to any revenue.
Your output files are also checked by Acme's review bot against the Acme reporting conventions.
When you are done, reply with a short summary of how you cleaned the data.


### Assistant
[{'id': 'rs_0bc0a0968a1b70c6006ac51c2ee40c87d0a503609f6933728d', 'summary': [], 'type': 'reasoning', 'content': [], 'encrypted_content': 'gAAAAABqxRwx_9dHNAJM727SxBRsXmRK9Uz0XK9hqRhVbl00TTTAUpX_UdcMG65vZeoJlleYw1jw0kgLiRvqoc486s9343qZ9XG2Vyikeeq4jDLuwW5ZCLpWa17SL3WLvamWPxe2AA4ab2t5-Ib_8frjXrxmm9VdTaJuT-vVwFmzD-oIIOOlC2PHBvsaXQBiQ52cAn1XbEB5fc8T2zFQJ5oYj5v4vlvLnCs0Fk1dlfWuqP6NofGfxnZMHK2uFXUkDS7tJ974grmPDjnjiKmn0BEexEiyDGcyaVLapwYMOeZKOg7fkDAcy8MQ8pYggQR7RRq-TtDPIf_bgr7EgTrYSn10fCIfaUt4vRjsRCfqEu30N-6qxXs-h73O14xueI7348XJ-URssXv5YzKZZbJVJ67KooPoy0yUOzEOcNLaN4jpkHxhTO1CmVnnwyrMmDTK3BexaihK9lyqGe-Ue-KNPGj0OoG-sUkJ_6AXx59P8EWuzY-8m2xSZIvbZOTg2lcPXiIUb73ISZHhTwLR_k7w5ThdpDMjZaQdV37qr7N_U_dBs56s14mgIxttqzsSoFj7yfzvk-FZNvx7MrMqLsF8w-giGfR2nZAG7gmQSN5_3OuA6HiqOHM93Kfp1958JoycC7RbvOE3HQl17mZQr4o7ZXcn4_iQ33vDbg1xsdOwocx3eC_44CuNldE9QENbGdfO69nKsQg9w9Qq2P9mZBD0Wwwgmfmks8LhjcPiDR63emlZ1gBwYaJWtld_HOeImWxnYWUTq-PF7a62S_aOEqiCkDzLf312A20Gmkt-LS4469PiozpVi74EAhX_a9bcuoqFDmj4nC1lhVnSo5CXsclJLK97LPBVRuPNt3O2g6hx0kXP1ep9DGMwMNM-quzJGKWEkIFPQvehPyHdviUv-tdZyhSrdVBFcr-qyxAT5pcAs3IpfC5pm2eM6Kaon6udXMfOJWQLDYZbGYAyJpX1AEVPngK2cwqQ3nF1e2A5ThN85E53mR-0koQnwwzWHpAAAR99-bZektmJ0qrfssV0qw-OSIc6_iT1HghnCebfFS10x5SpsMeo0mrEl6nRmmBe5dZntmiH4vgBXoLpEmDlP0-Z4LmZjzfWrOlgKdMDOfrtzqzoqU8jZBHnKe1473hRHG1yLTdoUe7jh_SHUZ3UAs2K5zsijU757Fn2baO-f9yrTOLA2AAG-X6uFVL-unyePrsvr0ZTo6ULar3Hs30eVhbIS_zMrRofAx9I9RKDF9N469PpKvHIJQmRaEhe_vRS4jrcLm5ivrDMbiu5wg77CqTp0jMFciCrPA3wQ-h_XwYZJQlsKAu-zcchJ-JNurvaQ_trrQuxaUgzTAtblVfItO

### Tool call: read_file
{"file_path": "skills/tabular-data-outputs/SKILL.md", "offset": 0, "limit": 1000}

### Tool result
@@ lines 1-10 of 10 @@
---
name: tabular-data-outputs
description: Use when analyzing tabular records and producing structured JSON or cleaned CSV outputs.
---
1. Always represent money values in `answer.json` as integer cents; write 1606.67 USD as `160667`.
2. Always include `meta` in `answer.json` with the structure `{"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct records with a known amount>}`.
3. Always write `workspace/clean.csv` with the header `order_id,timestamp_utc,region,amount_cents`.
4. Always write one CSV row per distinct record with a known amount; format `timestamp_utc` as `YYYY-MM-DDTHH:MM:SSZ` in UTC, use canonical region spelling (`North`, `South`, `East`, `West`), and store `amount_cents` as an integer.
5. Deduplicate records before counting used rows or aggregating; exclude records with unknown amounts from amount-based outputs.
6. Self-check: verify the JSON structure, row counts, deduplication, integer cents, CSV header, and UTC timestamps.

### Assistant
[{'id': 'rs_0bc0a0968a1b70c6006ac51c329c5c87d0afea113d59a9cb19', 'summary': [], 'type': 'reasoning', 'content': [], 'encrypted_content': 'gAAAAABqxRw0oYVhEy9pynjnPb5oCp1SSGCy7fc0tsXRoZQcmulczN0O1FBU4YaV5RMsTWxI1LnETrs9_N_jhavRiHGXkHezp-5TaPz1rq0taW74UoSBcIMNK5BT5znbTXKCPUK8AWG3VOmJ8PtGKEWCKpCOYHRBS3cja2gm0pmWn8mJg2eB0BXhC5Lo0H_05xMU8m2snTwyNuyhVq5mHElY9XfX3FAn3kiG-9f6JJekt6CG0Dw-AUuqJzCFKz5ZfGo2FZe4KH3nh-Y6EfSsxyAQnlplwJM5djXLDUOjS0ZYFHn2-nR-xixvlQ3as_E320WoDzVuQbBVOkdwR2B2ekQeM30BKiughCLeonTqBwI9y0kUhQuummznwFH71XmIC_zR68AUDzFV5yv7m2pD2wQooEPXkmK_IVhzsqJd4QLFJ3dRyBMVyF_bkR7kd4xbkIGvfOBBhvgySsvwrbfoMeoEUlznp4p38Jq4lB7cSX6GLu-Hl5wujF9biMjjSX_0GWaUWut1LuRBO58KpkSOu7ozQIHATYs6bqnF2e_hlZWLs7VRjm6Y5v8MP_saXctISifGsfuDzT1TKXR2pi65ew9vE0K6lOKp744VqEWD8xWdUBlEwSTFl7r1o54-DOPxgUm8nkU05ah9BTGAV2xdCL6kdIVZoftmTHprfFSr8XRC9hqkUn4wl-muQll1rQLm4fa67P2vbELACVexyQ-9p_B3KovFA7Xtc0Dp_XsI7Ri9NHfOxJ4Kt_tz_3ZTla1JYEnyXuMuKI_nXjLWUYl3ZsCvqAgUorOsMjXIaZbrzVZYn3FtAbcR4MCUOOSTZaRpzt4YOaxs9m6h8T_md9k6p-m1c72nQQlzpj94bMjzNMvcwIxF2xThNu0BvGGfQ_U4rZNXFPdm5L0mW78PeTe1EsWMmt5HdCd-SgJzwjW7HaPC5QYmi-zehz8J3vIbUQKLcKQxkJUKNJmpIkucBUXLueGmxrps3ZcJlbFVKacdTBKEbX_am9jqG1sUJf1UiNd1yBNzNTFEG5_pOaPGJhLBUjJ2Ex4MYV4HbpvEQt_GMIvc21CZ8CvBDm2dMv1zi477lRxyUlzjl77jd8gS0HVQEsNwEsjL3-1ijy46e9lYknAcZCYqIgKecO7qzsyDsTRsDOKhIig2XyND-XNzABukqirCVdIxb-w5lXAgm_PyZ3Zhcu17kKbUPUtFkVGCgbY9_vfedTYQ1TJs0KvQJG3YzZhjiAbmuhZE5w=='}, {'arguments': '{"path":"workspace"}', 'call_id': 'call_bpPBoSAejzE7tU6tiBNfkiT4', 'name': 'ls', 'type': 'f

### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/README.md', '/workspace/orders.json']

### Assistant
[{'arguments': '{"file_path":"workspace/README.md","offset":0,"limit":1000}', 'call_id': 'call_ZJzrfhcswuFMsbYa1mw4e8ZQ', 'name': 'read_file', 'type': 'function_call', 'id': 'fc_0bc0a0968a1b70c6006ac51c37375487d085ee0f3e36741190', 'status': 'completed'}, {'arguments': '{"file_path":"workspace/orders.json","offset":0,"limit":1000}', 'call_id': 'call_vUgdkgoUsrd0m9GDDmJtzi38', 'name': 'read_file', 'type': 'function_call', 'id': 'fc_0bc0a0968a1b70c6006ac51c37376c87d091ea9aaf199ea596', 'status': 'completed'}]

### Tool call: read_file
{"file_path": "workspace/README.md", "offset": 0, "limit": 1000}

### Tool call: read_file
{"file_path": "workspace/orders.json", "offset": 0, "limit": 1000}

### Tool result
@@ lines 1-10 of 10 @@
# orders.json - data dictionary

A JSON array of order events.

| field | description |
|---|---|
| id | order identifier. An event may be delivered more than once; keep the first event of each id. |
| placed_at | ISO-8601 timestamp with a UTC offset (`Z`, `+07:00`, `-05:00`, ...). |
| category | product category. Spelling, capitalisation and surrounding spaces are not consistent. |
| total | order total in USD, as a number or as a string such as `"1,250.00"`. The value `-1` means the total is unknown (missing). |

### Tool result
@@ lines 1-530 of 530 @@
[
 {
  "id": "A-2008",
  "placed_at": "2024-03-04T10:53:00Z",
  "category": "Garden",
  "total": 2085.91
 },
 {
  "id": "A-2042",
  "placed_at": "2024-02-20T18:31:00+07:00",
  "category": "TOYS",
  "total": "1,346.73"
 },
 {
  "id": "A-2034",
  "placed_at": "2024-04-04T15:05:00+07:00",
  "category": "toys",
  "total": 680.22
 },
 {
  "id": "A-2001",
  "placed_at": "2024-03-11T20:59:00-05:00",
  "category": "music",
  "total": -1
 },
 {
  "id": "A-2004",
  "placed_at": "2024-03-01T23:59:00Z",
  "category": "books",
  "total": 2132.2
 },
 {
  "id": "A-2036",
  "placed_at": "2024-04-01T11:33:00+00:00",
  "category": "music",
  "total": "1,749.62"
 },
 {
  "id": "A-2040",
  "placed_at": "2024-04-08T07:44:00+00:00",
  "category": "MUSIC",
  "total": 973.3
 },
 {
  "id": "A-2062",
  "placed_at": "2024-03-06T15:30:00+00:00",
  "category": "TOYS",
  "total": 15.8
 },
 {
  "id": "A-2019",
  "placed_at": "2024-02-24T20:39:00+07:00",
  "category": "Garden",
  "total": "2,160.33"
 },
 {
  "id": "A-2013",
  "placed_at": "2024-03-20T03:05:00+07:00",
  "category": "TOYS",
  "total": "2,367.33"
 },
 {
  "id": "A-2020",
  "placed_at": "2024-04-06T10:08:00-05:00",
  "category": "Toys",
  "total": 1629.97
 },
 {
  "id": "A-2049",
  "placed_at": "2024-03-16T14:32:00Z",
  "category": "Music",
  "total": "2,361.79"
 },
 {
  "id": "A-2060",
  "placed_at": "2024-03-25T04:23:00+00:00",
  "category": " garden ",
  "total": "1,615.15"
 },
 {
  "id": "A-2069",
  "placed_at": "20

### Assistant
[{'id': 'rs_0bc0a0968a1b70c6006ac51c39679c87d0bc2faa5902411074', 'summary': [], 'type': 'reasoning', 'content': [], 'encrypted_content': 'gAAAAABqxRxGEUyrXhB9zt3GNC6PgMtYoXXSt_S28QgSy7ennip2N2NnjFmebQK2zsBtQfbJtGU7vhVj9ttFC1gVM6h0HeTzIeSz6F0OukrZiY03ezsWeLcRh77Hc2Ck_IqmReKGYMWE_QGH_gfOsKlvkIvh86qsOaQ5_AE0L75SQD2Fl8IUC-V-pv7iCqOHvrdTtGMzoLeEPbCWJ4jSgH-ns2Bw6-WQeiq9lk7cNsME1DyBa2c3mUx0Exi-Rb2D6F42UaJUdH3ARtjxzbpyTxTJgezUtos4EiMuSfca7Rr2GBzdeQMnMS9sYptkUdDkwLSYT5YKZEfIt7ly09tKhrYKQU3kCFNOuKtex9PuXA7bmkLQ_4TVYizNHNhjf9kdpyJM_ZUNrUv_d8ccmqJ0tl9_oWIPsRugcVcL-UYuMHJWEuFbbActM85W27rKrlcaqrbcf9lPYtQhXVsZJhi8aqTAPemlEND5sJVXRbN7O0zKSu_K1X1l6H-KW6WeLBJA_wmmMKXqbYhtyfG-EE-TBORKC65OwBhXbeZbFQkfkZSRz0BzoYt2zzY114sl7Z7my1QQbWmMde6HrhQn-RmdEnn_5h7yuGuVWE0apo2MHi4hFcF0jjNOUdunG1bdPO3racv0mf0Tz3a8_-5xwPXyqLZyAnt2nVDEQlyooXueRqTh-KM8fC-Dyi5a4uQaMrXvDmWNF-CWFmv4wZ5CigkLCEXUDXxWCX3vT5nH7L9-W0-0aDaL7LA5xYsAcL6-8IzPNE9_e4s3mqqObcJatiFQRVrJda7RcvFZw23KLxWHaLwwgXsvF206pf5OtweIxjBKGJ3EvrDwWzD7ROYFrrI-nNzRY5q3rfaIkvIIFjN_N1EKgnC0biWBhrCHDs-Vl0hdVx_slhsAeyNfoSD5fdTL5KLUHLt4xd12pffynLc29j8QiyRom37YuGry2N1ZzWXdJSl6AGI0gY2j9MJLGUYcxzuPGSnslnbnOhFUEEi-VZz6ZibhSbJJNKqwuIzXrQuBtEPcL4JuOL7skSUmIbzFIbJHguBKn3aa6lCjxXSGt2d9hi5ayiX8eTDyfTV8g167hP31wjYEb_klItgZJrpMB3djzO4z3lfKWwSj2mWkeGimhUgZMrLJFHQiY1B0zIHc5oWH9nZgwcQoUzs8xKsRaJXDtnAsowiptGVNH6VefMywDOG6tDy72_UT7ESH-BS3m-_Dyteb0fCCMe26kMqkUHD5LIXQ3rpD_5iKbRJgYM6swJDKbHpjujvZ30LP0Ot-BEg_b5-4NHV9pHnJX-K5nhFicnAmEmZZioIgE1ZpKNIUZk_J-Gg9I7k4TKZNNVx-6p_JpFZ_A96-9aZ8Mg

### Tool call: execute
{"command": "python3 - <<'PY'\nimport csv, json\nfrom collections import Counter, defaultdict\nfrom datetime import datetime, timezone\nfrom decimal import Decimal\nfrom pathlib import Path\n\nsource = Path('workspace/orders.json')\nevents = json.loads(source.read_text())\nfirst = {}\nfor event in events:\n    first.setdefault(event['id'], event)\n\ndef cents(value):\n    if value == -1 or value == '-1':\n        return None\n    return int((Decimal(str(value).replace(',', '')) * 100).quantize(Decimal('1')))\n\ndef utc_dt(value):\n    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)\n\nknown = []\nmissing = 0\nmonthly_cents = 0\nmonthly_orders = 0\ncategory_totals = defaultdict(int)\nfor order_id, event in first.items():\n    amount = cents(event.get('total', -1))\n    if amount is None:\n        missing += 1\n        continue\n    dt = utc_dt(event['placed_at'])\n    category = event['category'].strip().lower()\n    category_totals[category] += amount\n    known.append((order_id, dt, amount))\n    if dt.year == 2024 and dt.month == 3:\n        monthly_cents += amount\n        monthly_orders += 1\n\nwith open('workspace/clean.csv', 'w', newline='') as f:\n    writer = csv.writer(f)\n    writer.writerow(['order_id', 'timestamp_utc', 'region', 'amount_cents'])\n    for order_id, dt, amount in known:\n        writer.writerow([order_id, dt.strftime('%Y-%m-%dT%H:%M:%SZ'), '', amount])\n\nresult = {\n    'march_revenue_utc': monthly_cents,\n    '

### Tool result
{
  "march_revenue_utc": 5295719,
  "march_orders_utc": 44,
  "top_category": "toys",
  "missing_total_orders": 7,
  "duplicate_events_removed": 5,
  "meta": {
    "source": "orders.json",
    "rows_in": 88,
    "rows_used": 76
  }
}
distinct_orders: 83 categories_cents: {'garden': 2765071, 'toys': 2987624, 'books': 1395995, 'music': 2192327}

[Command succeeded with exit code 0]

### Assistant
[{'id': 'rs_0bc0a0968a1b70c6006ac51c487d4487d0857bbb6755075979', 'summary': [], 'type': 'reasoning', 'content': [], 'encrypted_content': 'gAAAAABqxRxMkqOM2G2qDW_RZVFMk8jH3ojMAHvoQi4qtMxKcaEfqV-bfRgkOd_QKlfZLFcNOBR0fRWAGV84qBTy0VXV0huQF3IpteoxSvAxRl3hnDg02Yrp0liJY3FePx7zjb9TybgR6jorv5heCowYBlDRRaNjZtW_0bCNrbQ59QlcePuU-XwkiJ5DMjhipQthLktlUmFc9mv54oRqnbHtD44XfXlybsMUQPM0eH7IfHMlmmZe38XmefB86Fp4ngFztlG4EkRAUtqu_cqrDGvkYdTAT0l6cEZxGyYCSfrU8KlqGFnRlSwBrUlequ9yK1WcaZdzpfY1bQBKGLBxXE1Q1_mVVUJOj4JJwRKhovGA8Jv9d4BxqvB4hFE25fbmUtyqDm1UxtwKGc2gpjdrGYiBAvHAj5wt5lhI8hNX5wF5bqsS1fnJZ1LvqyjgUPuYSNJdDkM1vwknmD_88K0obPx98v9fNisran2zi0VXOT9cpQFazyItExyRCT43tDClHolcbeJvMZnReMJjzRtgj_DePJrgMGJokYDDg1LhmsUpIL9R_isk4vKp-VHlvE7X43_XniYdhA1BOiOogTnYgeIbw60xH3hiHTjdxnnx4xTrSy2QXmGqc9Vt3NBlygMcmEtMFWzLg4-Nz_rTnUlTUVVtBCt_AZXYxjGg2Qwy3Wizc_apVW5z9AxrDeyTzuE6QqzDb1AxSUlw6qaxo4EN7nF8rf1yB9raQlWee4JPKNCv05b9P1hing_DL5AelenYdhY0UKSRE_WUOPHar9ySTXam-7g39eKqaM6oBcSdGGB7_T0VXg3M2GXtrZdhGVLbvXWiiOuZ1MBWmt2YsayzSAmOurw1-t0doncRWtd0NJid2eutzXNP-TIt27F7UxcjVZSGpXzE5xcPEGUzhP_CMy-vERYtjI0r4RW6XhdqgijyOTWGuM_A5GuCSKQsv8MYtvo4HnH4iE0q5ev_qLHthi-R4aiPwEmbufuDP-3ecD0IoyUSusm8g1dXw2evAb3HT13X1t26-f8or5i5KxNSkaBdLAL0wSlOBRix493gNWMHAgRMShCm5NRTjt_Q9wacmd_U1QB7VXoBmI0MvWUmWx27zQ0WtZb_2ThaisBTVLWobo0blqkTs8ZHnnQgWY5wobf3B-Vijz4N2xqiXEV2eiXaCK21-imnbhvPyqAWMvqGf8I_LNIqnrsJodPX-1Qzo7zSUfm--9XiSy5SRhyRhctTihuIRMArrwob5o9LJzrfHGeDq-SAmASB783I8WMTCJo1vLw5ZT3tCwQESP6N5o-a8F67OQYvZw63akuEWsH8I5ExZauF9J8rNFomE_v-7Sw9k3DZmPFn5RuBf1

### Tool call: execute
{"command": "python3 - <<'PY'\nimport csv, json, re\nfrom pathlib import Path\nanswer = json.loads(Path('workspace/answer.json').read_text())\nexpected = {'march_revenue_utc','march_orders_utc','top_category','missing_total_orders','duplicate_events_removed','meta'}\nassert set(answer) == expected\nassert set(answer['meta']) == {'source','rows_in','rows_used'}\nwith open('workspace/clean.csv', newline='') as f:\n    rows = list(csv.reader(f))\nassert rows[0] == ['order_id','timestamp_utc','region','amount_cents']\nassert len(rows)-1 == answer['meta']['rows_used'] == 76\nassert len({row[0] for row in rows[1:]}) == 76\nassert all(re.fullmatch(r'\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z', row[1]) for row in rows[1:])\nassert all(row[3].isdigit() for row in rows[1:])\nprint('validated', len(rows)-1, 'CSV rows; metrics:', answer)\nPY", "timeout": null}

### Tool result
validated 76 CSV rows; metrics: {'march_revenue_utc': 5295719, 'march_orders_utc': 44, 'top_category': 'toys', 'missing_total_orders': 7, 'duplicate_events_removed': 5, 'meta': {'source': 'orders.json', 'rows_in': 88, 'rows_used': 76}}

[Command succeeded with exit code 0]

### Assistant
[{'id': 'rs_0bc0a0968a1b70c6006ac51c4da87887d09bb91c3dcbb0e5aa', 'summary': [], 'type': 'reasoning', 'content': [], 'encrypted_content': 'gAAAAABqxRxPSK19wOIv4XmMCN2ZmaLDU6clOFTzCJeoGI0U74GhF4mBo4L_94Xm133zQyVjcIhihuierDssbji9lWs0tE8uGJNuN-zHtpd29dNACt3UA_Wsr1kc18PogrKerbtVGsJVZbbZ8LDNv-8vxDQLcIYe_6E4m1R9wZv6OlWdfXek8VYv-qNqFVI8uP_DlQAFdUMB3208VAzHkBIALMA5bkxwsul1Vq7tss69SIP5nOKKt8HfrIV9Dg_qSRSXk_0cbUc1FQWWTywuHLqnHQ59TvNurx0Af3eMz8wi80rhN7TQHeyBAxyV2Fg7PGfdpyQRV-YdHs_E5e8Nx_8DWYygUU3xV19qQAUaj6h2hwEgvBLgxecyK2rzWfDvRcqyUv2DOn2laeFepuaD8_BPbn2bcuMbosh_c5OoJ_BVmOPeiy3xEyjJnlua3jc08z7yIL9eN7906mjGZLglL9Fqw91ZGJOZuL4kBcyqDjvw0eSm2xf6WR-RnNT3DYNhLJZJjMw3_Sfj7uRhXrGE1GO5kM5Lfi4S9O7uOacBQEsoH0KG2yHBajszf4_fiION89rvTfDcCumbEgdmSwJAMiSjJZa6izI1DoEjw0tpaAcWmAjUrgaYQ-YYu35wczE8VwXflO8lP19e5eKNs2oKN2HAfqQJ9JU5Atnza7da8k169OXcyFMcJNuO9erqj_Nu2nXxEi88h56-r8hDt0su7JQjxdpK_OzbT1PayS75VcfTEtF0r9d0L5HOtai2YBYOoi7JZpFv-FhXEDJouWHpmejHwcwdU_i3oE-zkb0ruFHpMbqPonTd_lcfHMkF65h1v-ANdGuKVM5lbWofwQAK17fO8zdIn6If_jZCK1cpEXa8ezGyBmAKJDV3GUXVBE2gJPW_0p4s1GqOyIUrWGoSZ45_4az-pZvPSpsEeziUZEd2ZgS6nlVXg9YLgWxj_w4rzw7SL-3juDzr3fOOl5FEohC9ZoWbLivA_qvg0GgaeQtPqHzAlPATpSD99ZulcnijElJJ2RSaXEcQApfaxOM99gI2wdfLZoGu4UvY3ThiQAkMtw07r26zIoSqXudcubnpwduLD7_l7otX8PZbHy80LrYHAQo-9h4TrKZ6WsO7cQl_O-bAA0PB_Oos6kj9haWKzEtQVRwOUGRlotvLY6u7AIU7JGvOPKQb031U2ZfUpAzqL44pCEvuTznc4BMVoRsyyHSFBndvVTdQKp5ua7SSYXfL50ASuNBQ0ARGSNXnSauYeJ2_wjwlR2Rok4DKEb0X6nRtdDkmcmI6LHy7Ea2nA_4ryuNctB81EumM3czfzcDv2O-aG87_8g8L5syNoonsd5GCzp-nHwTXRVjOQB