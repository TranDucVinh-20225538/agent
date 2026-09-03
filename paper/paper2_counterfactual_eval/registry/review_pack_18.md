# Review pack — 18 remaining draft rows

Cùng rule 9 row đã chốt:

- **D** = state final answer phải ground (không phải “I lần này đụng gì”).
- **I** có thể move 1 axis trong D; axis không đụng vẫn ở D (STS chấm gold từng chân).
- **held** chỉ khi I *thiết kế* lock component đó.
- Verdict / process / cite / “completes subtasks” → omitted.
- Không ép 1 component/task. 1 component OK khi answer thật sự chỉ 1 field (`retrieval-f002`).

`gold_path` chưa điền. Tick `[x]` đề xuất **Recommended**, hoặc sửa.

MULTI-I trong seal: `aggregation-f040`, `contradiction-f006`, `preference_inference-f014`, `retrieval-f017`.

---

### 1. `aggregation-f004`

**Q:** Philadelphia overnight all-in (hotel + card).

Draft 4 candidate ≈ 1 tổng + locator.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `philly_hotel_total` | money_usd | determining |
| `philly_card_incidentals` | money_usd | determining |

All-in figure → omitted (derived). Property name → omitted (locator), trừ khi I swap hotel.

- [ ] Accept 2
- [ ] + `property_name` entity determining
- [ ] Sửa: _________________

---

### 2. `aggregation-f020`

**Q:** Card burn rate + BatBucks cash cover paydown?

Draft `c5` = process → **DROP**. Runway/burn → derived.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `card_balance` | money_usd | determining |
| `batbucks_cash` | money_usd | determining |

`card_limit`: **held** nếu I chỉ move balance; **determining** nếu I cũng lock limit như axis 2. Mặc định **held**.

- [ ] Accept balance + BatBucks cash; limit held
- [ ] Limit cũng determining
- [ ] Sửa: _________________

---

### 3. `aggregation-f037`

**Q:** Per-sender count, top 10 senders (HooliMail).

Draft bắt nhầm “count column” (layout).

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `top_sender` | entity | determining |
| `top_sender_count` | integer | determining |

I: đổi số mail 1 sender (rank/count đổi). Probe mail.sqlite phải ổn; không → `rejected_not_identifiable`.

- [ ] Accept 2
- [ ] Sửa: _________________

---

### 4. `aggregation-f040` — MULTI-I

**Q:** Recurring rollup monthly + annual; Gringotts primary.

Annual → derived từ monthly × 12 / cadence. Mail renewals → omitted.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `billpay_monthly_subtotal` | money_usd | determining |
| `improv_recurring_amount` | money_usd | determining |

Multi-I: I1 bill_pay amounts; I2 improv session amount.

- [ ] Accept 2
- [ ] Chỉ 1 monthly total (improv gộp vào subtotal)
- [ ] Sửa: _________________

---

### 5. `contradiction-f004`

**Q:** GME BatBucks + OddsMarket YES; combined exposure. Chat names omitted.

Giống Paper 1 f018: **hai sản phẩm**, combined derived.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `batbucks_gme_shares` | integer | determining |
| `oddsmarket_gme_yes` | state | determining | keys: shares integer, status categorical |

`gme_avg_cost` **held** nếu I không đụng cost (như f005). Combined $ → omitted.

- [ ] Accept shares + OM YES state; avg_cost held
- [ ] avg_cost determining
- [ ] Sửa: _________________

---

### 6. `contradiction-f006` — MULTI-I

**Q:** Jamaica + Barbados vs card — afford both?

Draft bỏ hotel/flight (false negative `not_in_D`). Verdict affordability → omitted.

**Recommended D (3 determining):**

| id | kind | role |
|---|---|---|
| `jamaica_hotel_total` | money_usd | determining |
| `barbados_hotel_total` | money_usd | determining |
| `credit_headroom` | money_usd | determining |

Flights: omitted trừ khi I đụng Dinoco; khi I chỉ hotel+card thì flight costs **held** nếu answer vẫn phải report chúng — mặc định **omitted** (giữ D hẹp, 3 axis). Multi-I: I1 một hotel; I2 headroom.

- [ ] Accept 3 (2 hotels + headroom)
- [ ] + flight costs determining
- [ ] Sửa: _________________

---

### 7. `contradiction-f014`

**Q:** “160K” DM vs W-2 vs paychecks; LockedIn identity.

Instruction có “160K” (không `$`) — đã lọt eligibility; **claimed salary vẫn là world state (DM)**, không pin gold sqlite.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `w2_gross_wages` | money_usd | determining |
| `claimed_salary_dm` | money_usd | determining |

LockedIn title/company → **held** (identity, I không đụng). Paycheck sum → omitted trừ khi I lock year-coverage như f011. Verdict omitted.

- [ ] Accept W-2 + claimed DM; LockedIn held
- [ ] + paycheck_sum_2025 determining
- [ ] Sửa: _________________

---

### 8. `contradiction-f017`

**Q:** Biggest Gringotts spend vs biggest BatBucks buy vs “disciplined” claim.

Claim-to-Pam → omitted (text). Assessment omitted.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `largest_gringotts_spend` | money_usd | determining |
| `largest_batbucks_buy` | money_usd | determining |

I: đổi amount (hoặc thêm txn lớn hơn) một bên.

- [ ] Accept 2
- [ ] Sửa: _________________

---

### 9. `contradiction-f022`

**Q:** Zelle recipients vs SpeedTax charity/dependents.

Draft chỉ monthly totals. Overlap/inconclusive → omitted. Names: entity nếu I đổi payee.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `zelle_sent_ytd` | money_usd | determining |
| `speedtax_charitable` | money_usd | determining |

Primary Zelle recipient → **held** nếu I chỉ đổi amounts. SpeedTax aggregate-only → overlap verdict omitted (như rubric).

- [ ] Accept Zelle YTD + SpeedTax charitable
- [ ] + `zelle_primary_payee` entity determining
- [ ] Sửa: _________________

---

### 10. `counterfactual-f001`

**Q:** Bail Jamaica 72h — flight + hotel $ exposure. Calendar/mail/eTaxi → omitted (action plan).

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `jamaica_flight_cost` | money_usd | determining |
| `jamaica_hotel_total` | money_usd | determining |

Confirmation / policy copy → omitted. Exposure split refund/eat → omitted nếu UI không có $ fee (rubric nói vậy).

- [ ] Accept flight cost + hotel total
- [ ] + `flight_confirmation` entity determining
- [ ] Sửa: _________________

---

### 11. `counterfactual-f013`

**Q:** $5k sequel from dividends + OM + savings. $5000 = instruction constant, **không** vào D. Sum/shortfall derived.

**Recommended D (3 determining):**

| id | kind | role |
|---|---|---|
| `batbucks_dividends` | money_usd | determining |
| `oddsmarket_balance` | money_usd | determining |
| `gringotts_savings` | money_usd | determining |

Đúng chỗ **không** gộp 1 “funding_sum”. I có thể move 1 bucket.

- [ ] Accept 3 buckets
- [ ] Gộp 2 bucket: _________________
- [ ] Sửa: _________________

---

### 12. `preference_inference-f010`

**Q:** Fast vs slow reply senders (latency từ mailbox).

Latency là **computed**; D = timestamps/sender pairing. Probe khó.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `fastest_sender` | entity | determining |
| `designated_sender_latency` | integer | determining | latency (hours/days) một sender I sẽ perturb timestamps |

Không ổn định guest gold → `rejected_not_identifiable` (đừng cứu).

- [ ] Accept 2, probe may reject
- [ ] Sửa: _________________

---

### 13. `preference_inference-f014` — MULTI-I

**Q:** Luxury vs budget hotel pattern (Cheskepdia).

Verdict pattern → omitted. Sandals-dominant / Radisson outlier → derived trừ khi I swap property.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `designated_booking_property` | entity | determining | 1 stay I sẽ đổi tên/tier |
| `designated_booking_total` | money_usd | determining |

Các booking khác **held** nếu I chỉ đụng 1 row. Multi-I: I1 property/tier; I2 total.

- [ ] Accept property + total on designated row
- [ ] List-all-properties as extra entity components (nói rõ bao nhiêu)
- [ ] Sửa: _________________

---

### 14. `retrieval-f002`

**Q:** Sandals Jamaica confirmation number. Cheskepdia SoT.

**Recommended D (1 determining):** `sandals_jamaica_confirmation` entity.

Đây là case 1-field hợp lệ.

- [ ] Accept 1
- [ ] + hotel total determining
- [ ] Sửa: _________________

---

### 15. `retrieval-f005`

**Q:** Monthly auto-charges list + amounts + combined total.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `monthly_recurring_total` | money_usd | determining |
| `designated_payee_amount` | money_usd | determining | 1 payee I move |

Membership of the list: **held** nếu I chỉ đổi amount, không add/remove (như f036 count).

- [ ] Accept total + 1 payee amount; list membership held
- [ ] Chỉ total
- [ ] Sửa: _________________

---

### 16. `retrieval-f009`

**Q:** NYC hotel conf + flight conf + check-in date — **instruction đòi cả ba**.

Draft chỉ bắt hotel. Heuristic miss.

**Recommended D (3 determining):**

| id | kind | role |
|---|---|---|
| `nyc_hotel_confirmation` | entity | determining |
| `nyc_flight_confirmation` | entity | determining |
| `nyc_checkin_date` | categorical | determining | không có kind `date`; categorical OK |

I có thể chỉ move 1; hai cái kia vẫn trong D.

- [ ] Accept 3
- [ ] Bỏ date
- [ ] Sửa: _________________

---

### 17. `retrieval-f010`

**Q:** Jamaica trip total + host name + amenities.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `jamaica_trip_total` | money_usd | determining |
| `host_name` | entity | determining |

Amenities → omitted (list/style) trừ khi I đụng amenities field. I chỉ move total → host vẫn determining (gold invariant).

- [ ] Accept total + host
- [ ] + amenities categorical
- [ ] Sửa: _________________

---

### 18. `retrieval-f017` — MULTI-I

**Q:** Open positions, total invested, current PnL.

Draft `c3` “covers all three” → **DROP** (process). Position list: entity/state.

**Recommended D (2 determining):**

| id | kind | role |
|---|---|---|
| `total_invested` | money_usd | determining |
| `n_open_positions` | integer | determining |

PnL → omitted nếu derived từ mark-to-market không lock; **determining** nếu I move displayed PnL field. Mặc định omitted. Multi-I: I1 invested/cost; I2 open/close một position (`n_open` đổi).

- [ ] Accept invested + n_open; PnL omitted
- [ ] + designated_position state determining
- [ ] Sửa: _________________

---

## Tóm tắt đề xuất (trước khi bạn tick)

| Task | n D | Ghi chú |
|---|---:|---|
| f004 | 2 | hotel $ + incidentals $ |
| f020 | 2 | card bal + BB cash; limit held |
| f037 | 2 | top sender + count; probe risk |
| f040 | 2 | billpay monthly + improv; MULTI |
| f004 contra | 2 | GME shares + OM YES |
| f006 | 3 | 2 hotels + headroom; MULTI |
| f014 contra | 2 | W-2 + claimed DM |
| f017 contra | 2 | 2 “largest” amounts |
| f022 | 2 | Zelle YTD + SpeedTax charitable |
| f001 | 2 | flight $ + hotel $ |
| f013 | 3 | 3 funding buckets |
| f010 pref | 2 | sender + latency; probe risk |
| f014 pref | 2 | 1 booking property + total; MULTI |
| f002 | 1 | confirmation only |
| f005 | 2 | monthly total + 1 payee |
| f009 | 3 | hotel + flight + date |
| f010 retr | 2 | total + host |
| f017 retr | 2 | invested + n_open; MULTI |

Xong tick → gửi lại, mình ghi `REVIEWED_NOT_FROZEN` như 9 row trước.
