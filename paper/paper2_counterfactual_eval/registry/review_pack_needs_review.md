# Review pack — 9 `needs_review` rows

Tick `[x]` trên đề xuất. Đừng freeze JSON cho đến khi 9 row này xong.  
`gold_path` / SQL = bước inject-probe, **chưa** điền ở đây. `w_i=1`.  
`held`/`distractor` chỉ thêm nếu đúng f030 / f016.

Quy ước: **KEEP** = component STS; **DROP** = bỏ khỏi D (omitted).

---

## A. Zero candidates (heuristic miss hoặc không có D)

### 1. `contradiction-f011` — MULTI-I

**Instruction:** Cross-check SpeedTax charitable deduction (last year) vs Gringotts donations (+ optional HooliMail receipts).

**Đề xuất D (2 determining):**

| id | kind | role | Field I sẽ move |
|---|---|---|---|
| `claimed_charitable_2025` | money_usd | determining | SpeedTax TY2025 charitable claimed |
| `gringotts_donation_sum_2025` | money_usd | determining | Sum Gringotts 2025 charity debits |

- Verdict (supported/overstated/…) → **omitted** (`not_in_D`) — derived.
- HooliMail receipts → **distractor** chỉ nếu không chấm STS; mặc định omitted.
- Held: không (không có field “phải đúng cả 2 chân” tách khỏi I).

**I (ghi chú probe, chưa SQL):** đổi claimed **hoặc** đổi 1–2 donation amounts (gold-moving). Multi-I: chân kia là hướng còn lại.

- [ ] Accept 2 determining
- [ ] Sửa: _________________

---

### 2. `contradiction-f024`

**Instruction:** Jan rejected expense report; Chili's in `~/Downloads/`; any double-dip onto SpeedTax?

**Đề xuất D (2 determining):**

| id | kind | role | Field |
|---|---|---|---|
| `chilis_receipt_amount` | money_usd | determining | Chili's line on receipt / rejected item |
| `speedtax_overlap` | categorical | determining | overlap vs none (live SpeedTax vs rejected set) |

Draft auto **không** bắt được (zero). `amounts` không match `\bamount\b`.

Không nhét “extracts rejected line items” thành determining — process.

**I:** đổi Chili's amount **hoặc** thêm/bớt deduction SpeedTax khớp Chili's. Receipt là file — probe phải đọc file + sqlite; nếu guest gold không stable → `not_identifiable`.

- [ ] Accept 2 determining
- [ ] Chỉ 1 field: _________________
- [ ] Sửa: _________________

---

### 3. `situated_action-f029`

**Instruction:** Mở sequel notes, thêm 5 plot points, gửi ≥3 coworker (casting).

**Đề xuất: không invent D.** Rubric = action/style. `mail.sqlite` không phải gold của “5 plot points”.

- [ ] Giữ trong seal; sau probe ghi `rejected_not_identifiable` (không vào confirmatory \(\mathcal{A}\))
- [ ] Tự nghĩ D khác: _________________
- [ ] (Không khuyến nghị) D giả trên số recipient — không phải determining state của plot

Family tag `categorical` trên seal là sai hướng; không cần sửa seal vì family chỉ stratify.

---

## B. Cap >4 (gộp restatement, bỏ cite)

### 4. `aggregation-f036`

**Instruction:** Sum Scranton Improv class spend, last full calendar year (payee filter).

Draft 5 candidate ≈ cùng một tổng.

| Quyết định | id | kind | role |
|---|---|---|---|
| KEEP | `improv_spend_last_full_year` | money_usd | determining |
| optional held | `improv_txn_count_last_full_year` | integer | held nếu I chỉ đổi **số tiền** từng dòng, không thêm/xóa txn |

DROP: c2 line items, c4 duplicate total, c5 “single answer”, filter criterion (action).

**I:** UPDATE amount vài debit Improv cùng năm → tổng đổi, count giữ.

- [ ] 1 determining (total only)
- [ ] + count as held
- [ ] Sửa: _________________

---

### 5. `contradiction-f003`

**Instruction:** Loyalty / miles vs booked flights vs “Gold Voyager” claim.

| Quyết định | id | kind | role |
|---|---|---|---|
| KEEP | `loyalty_tier` | categorical | determining |
| KEEP | `loyalty_miles` | integer | determining |

**DROP** `c5` `c6` `c7` (discrepancy / cites sources / walk-through) — `c6` là FP “balance”.  
`c4` miles-from-flights: **omitted** trừ khi I không đụng itinerary — khi đó có thể **held** (f030-style). Mặc định omitted.

**I:** cùng Paper 1 Dinoco `loyalty` (Silver + miles thấp). Không redesign trap.

- [ ] Accept tier + miles
- [ ] + held miles-from-flights
- [ ] Sửa: _________________

---

### 6. `counterfactual-f002` — MULTI-I

**Instruction:** Liquid cash vs Barbados hotel settle; card headroom; BatBucks fallback.

| Quyết định | id | kind | role |
|---|---|---|---|
| KEEP | `liquid_cash` | money_usd | determining | checking+savings (+ BatBucks cash nếu I đụng) |
| KEEP | `hotel_settle` | money_usd | determining | Cheskepdia Barbados settle |

DROP: `c3` brokerage cite, `c5` policy emails (`$200` keyword), rank-options.  
Card headroom: omitted trừ khi I lock “không đụng card” — khi đó **held**.

**I:** đổi checking **hoặc** hotel total. Multi-I: hướng kia.

- [ ] Accept liquid_cash + hotel_settle
- [ ] + held card_headroom
- [ ] Sửa: _________________

---

### 7. `counterfactual-f003` — MULTI-I

**Instruction:** Venue doubles; cut trophies/catering; credit limit.

| Quyết định | id | kind | role |
|---|---|---|---|
| KEEP | `venue_planned` | money_usd | determining | planned venue (doc/email) — gold của “double” |
| KEEP | `credit_headroom` | money_usd | determining | limit − owed |

DROP: trophy unit × qty (derived), dollar-cuts proposal, “coherent budget”.  
Trophy qty: omitted (count in doc, không phải I trừ khi extra leg).

**I:** đổi venue planned trong file/email **hoặc** đổi card limit.

- [ ] Accept venue + headroom
- [ ] Chỉ venue_planned
- [ ] Sửa: _________________

---

### 8. `counterfactual-f005`

**Instruction:** Double GME at avg_cost; afford from checking/savings/card.

| Quyết định | id | kind | role |
|---|---|---|---|
| KEEP | `gme_shares` | integer | determining |
| KEEP | `gme_avg_cost` | money_usd | determining |
| KEEP | `gringotts_checking` | money_usd | determining | hoặc checking+savings một component `liquid_bank` |

DROP: c1 shortfall, c2 card-alone, c3 impact prose, c5 residual — derived. Go/no-go omitted.

Ba component = dưới cap 4. Nếu muốn hẹp hơn: `gme_shares` + `liquid_bank` (avg_cost held nếu I không đụng holdings cost).

- [ ] 3 determining (shares, avg_cost, checking)
- [ ] 2: shares + liquid_bank; avg_cost held
- [ ] Sửa: _________________

---

### 9. `counterfactual-f010`

**Instruction:** Upgrade all upcoming flights ~$600 each from checking+savings; which most/least worth it.

| Quyết định | id | kind | role |
|---|---|---|---|
| KEEP | `liquid_cash` | money_usd | determining | checking+savings |
| KEEP | `n_upcoming_flights` | integer | determining | count upcoming (upgrade bill = 600×n) |

DROP: `c2` residual, `c3` confirmation list (entity FP), `c4` priority ranking (`integer` nhầm “duration”), `c5` yes/no.

**I:** đổi balances **hoặc** số / cost upcoming flights.

- [ ] Accept liquid_cash + n_upcoming
- [ ] Chỉ liquid_cash (n held nếu I không đụng Dinoco)
- [ ] Sửa: _________________

---

## Sau khi tick

1. Sửa `registry_rows_draft.json` (hoặc file `registry_rows_reviewed.json`) theo tick.  
2. 18 row sạch: gộp tương tự (bắt đầu `aggregation-f004` → 1 trip total).  
3. Rồi mới inject-probe / `gold_path`.
