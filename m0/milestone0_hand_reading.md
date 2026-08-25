# Milestone 0 - hand reading, 10 tasks

Seed 13. Stratified by category and rubric class.

## retrieval-f009  (retrieval / personal_lookup / hard)

- rubric_class: **mixed** (pinned 3, seed-relative 2, procedural 0)
- apps: Cheskepdia, Dinoco Airlines
- seeded values quoted: NYC_HOTEL_NAME

**Instruction.** For my recent NYC trip, pull up the hotel confirmation, the flight confirmation, and the check-in date — I need to send them to someone. I stayed at the Greenwich and flew Dinoco.

**Rubrics.**

1. Agent finds The Greenwich Hotel NYC booking in Cheskepdia and reports the live confirmation number as shown on the booking
2. Agent finds the NYC Dinoco flight in Dinoco Airlines and reports the seeded flight confirmation code from the live booking
3. Agent reports the NYC check-in date as seeded on the Greenwich Hotel booking
4. Agent reports the Greenwich hotel confirmation, the Dinoco flight confirmation, and the NYC check-in date together in one response for the recent NYC trip

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## retrieval-f035  (retrieval / personal_lookup / hard)

- rubric_class: **seed_relative** (pinned 0, seed-relative 1, procedural 1)
- apps: Files
- seeded values quoted: -

**Instruction.** I made Holly a music playlist a while back and saved the track list as a text file somewhere on my computer. Where did I put it, and what songs are on it? I want to add a couple new ones tonight.

**Rubrics.**

1. Agent locates the Holly playlist text file anywhere on Michael's filesystem and reports the absolute path where it was found
2. Agent opens / reads the file (does not summarize from memory)
3. Agent lists the actual tracks that appear in the playlist file (not generic love songs)
4. Agent's response is grounded in the file content, not in fan-fiction guesses about what Michael would put on a Holly playlist

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## retrieval-f030  (retrieval / personal_lookup / hard)

- rubric_class: **mixed** (pinned 3, seed-relative 3, procedural 0)
- apps: SpeedTax, Files
- seeded values quoted: SPEEDTAX_1099_PAYER;SPEEDTAX_TAX_YEAR

**Instruction.** What was my 1099 income on the most-recent return, who paid it, and how much did I claim for charitable contributions? Cross-check the 1099 payer and amount against ~/Documents/Tax_2025/1099s.txt. This is for my accountant.

**Rubrics.**

1. Agent opens SpeedTax and finds the most-recent 1099 entry showing the income amount and payer for the accountant summary
2. Agent reports the most-recent SpeedTax 1099 income amount from Scranton Improv Academy and the charitable-contribution total from the deductions section
3. Agent opens ~/Documents/Tax_2025/1099s.txt and cross-checks the 1099 income payer (Scranton Improv Academy) and amount against the SpeedTax value
4. Agent navigates to the most-recent SpeedTax return's deductions section and surfaces the charitable contributions line for the accountant summary

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## preference_inference-f025  (preference_inference / pattern_inference / medium)

- rubric_class: **seed_relative** (pinned 0, seed-relative 5, procedural 0)
- apps: HangryDash, LibreOffice Calc
- seeded values quoted: -

**Instruction.** What do I usually tip on food delivery, in dollars and as a percent? I want to set a smart default so I'm not thinking about it every order. Give me a report of all my orders and their tips in a LibreOffice spreadsheet.

**Rubrics.**

1. Agent queries tip_amount and subtotal at the order-level for the HangryDash food-delivery tip analysis, covering Michael's full order history
2. Agent computes mean tip in both $ and % terms
3. Agent identifies the modal tip percent (15%, 18%, 20%, or custom) from the HangryDash order history
4. Agent recommends a defensible pre-fill default tip value grounded in the observed HangryDash tip pattern
5. Agent creates a LibreOffice Calc spreadsheet (.ods or .xlsx) containing a per-order row report with at minimum the order identifier, tip amount, and subtotal columns for Michael's HangryDash order history
6. Agent cites the HangryDash order-history tip rows as the data source for the recommended smart-default tip value, not inventing numbers
7. Agent delivers the full food-delivery tip answer in dollars and percent plus the smart-default recommendation and the LibreOffice spreadsheet

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## preference_inference-f005  (preference_inference / pattern_inference / medium)

- rubric_class: **seed_relative** (pinned 0, seed-relative 4, procedural 0)
- apps: BatBucks
- seeded values quoted: -

**Instruction.** Take a look at my brokerage portfolio. How bad is my meme-stock problem, and what would a sensible rebalance look like that doesn't totally abandon the names I actually like? Use cost basis, not market prices. While you're at it, peek at my old WUPHF investment agreement in ~/Downloads/ — that one was the OG mistake, and it sets the pattern for how I get into these things. Return the review of my portfolio in LibreOffice Writer.

**Rubrics.**

1. Agent pulls Michael's BatBucks RIVN holding (shares and avg_cost from the holdings view / /api/holdings) and reports it as the source of his RIVN exposure
2. Agent reports Michael's RIVN cost-basis dollar exposure (shares × avg_cost from live BatBucks holdings) and expresses RIVN's share as a percent of the total cost-basis portfolio
3. Agent frames the analysis using cost basis (avg_cost) per the user's request, not market value
4. Agent proposes a RIVN trim plan consistent with Michael's historical consumer-brand bias (preserves DIS/SBUX-style narrative names rather than suggesting a pure-index dump)
5. Agent reports the BatBucks holdings rows as the data source for the trim recommendation instead of inventing numbers
6. Agent delivers the full RIVN trim answer including cost-basis concentration percent and recommendation without abandoning the task midway
7. Agent opens ~/Downloads/WUPHF_Investment_Agreement.txt and references it as the founding 'bad bet' pattern that explains the current RIVN over-exposure
8. Agent produces the portfolio review in a LibreOffice Writer document, as requested in the instruction

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## preference_inference-f009  (preference_inference / pattern_inference / easy)

- rubric_class: **seed_relative** (pinned 0, seed-relative 3, procedural 0)
- apps: Kwik-E-Mart
- seeded values quoted: -

**Instruction.** What's my favorite grocery store, and what do I actually buy there? Rank my stores and give me a quick profile of my shopping habits in LibreOffice Writer. 

**Rubrics.**

1. Agent identifies Michael's favorite Kwik-E-Mart grocery store as the top-by-order-count store from live order history (/api/orders), naming whichever store has the plurality of orders
2. Agent reports the live order counts per store from Michael's Kwik-E-Mart order history (/api/orders), confirming the top-by-order-count store is ranked first ahead of the other stores Michael has used
3. Agent characterizes the typical line items Michael buys there
4. Agent writes a one-paragraph profile of Michael's Kwik-E-Mart grocery shopping habits at his favorite store
5. Agent reads Kwik-E-Mart order-history line items and states them as the data source backing the favorite grocery store ranking and buying profile
6. Agent delivers the favorite Kwik-E-Mart grocery store ranking and the buying-habits profile before ending the task

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## situated_action-f026  (situated_action / bounded_action / medium)

- rubric_class: **pinned** (pinned 4, seed-relative 0, procedural 0)
- apps: HooliChat
- seeded values quoted: BUZZCHAT_GROUPS;ZELLE_RECIPIENTS_CONTACT_ONLY

**Instruction.** DM Jim and propose a near-future evening for the next Finer Things Club meetup. Pick something this week or next. He'd be a great addition; he has taste.

**Rubrics.**

1. Agent opens or starts a HooliChat DM thread with Jim Halpert before composing the Finer Things Club invite
2. Agent picks a reasonable near-future evening (this week or next) as the proposed Finer Things Club meetup time
3. Agent sends the DM to Jim Halpert as a one-on-one HooliChat message rather than posting it in a group channel
4. Agent writes a HooliChat DM body that proposes the chosen near-future evening to Jim and references the Finer Things Club meetup

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## hard_app-f003  (situated_action / bounded_action / hard)

- rubric_class: **mixed** (pinned 1, seed-relative 1, procedural 1)
- apps: BatBucks
- seeded values quoted: SPEEDTAX_FILING_STATUS

**Instruction.** Time to rebalance my BatBucks portfolio into something a financial advisor wouldn't laugh at. I'm aiming for roughly 60% VTI / 20% SBUX / 20% DIS across the blue-chip bucket at cost basis (RIVN stays put — I'm not touching that one). Sell every share of GME I'm holding to free up cash, then use that plus my free cash to buy enough VTI to push the allocation toward 60%. Do this as a cost-basis rebalance, not live prices. Exact percentages aren't required — a reasonable approximation toward the 60/20/20 shape is the goal.

**Rubrics.**

1. Agent reads all current BatBucks holdings (live count from /api/holdings) and records each ticker's avg_cost value at cost basis before placing any orders
2. Agent sells every GME share Michael holds (full position liquidation) in a single or combined order
3. Agent computes a VTI buy quantity that pushes VTI toward approximately 60% of the rebalanced blue-chip (VTI+SBUX+DIS) cost-basis total, treating the 60/20/20 target as an approximation (RIVN held out of the target bucket)
4. Agent places a VTI buy order for the computed quantity
5. Agent confirms new holdings row shows GME=0 and VTI shares increased
6. Agent explicitly uses cost-basis framing (not market value)
7. Agent verifies the GME sell order and VTI buy order persist in the BatBucks order history and that the holdings table reflects the rebalance with cash updated

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## cua_only-f023  (long_horizon / bounded_action / hard)

- rubric_class: **procedural_only** (pinned 0, seed-relative 0, procedural 3)
- apps: LockedIn, Files
- seeded values quoted: -

**Instruction.** Draft me a new LockedIn post about 'Somehow I Manage' — two or three paragraphs about leadership. Get it fully typed into the Start a post composer so I can see what it looks like before I send it. Do NOT click Post. I want to look at it first.

**Rubrics.**

1. Screenshot shows the LockedIn post composer (Start a post box opened) with the agent's typed draft visible
2. Composer draft content references the 'Somehow I Manage' theme (the phrase appears in the typed body)
3. Post was NOT actually published (LOCKEDIN_POST_COUNT should be unchanged)
4. File saved at ~/Desktop/lockedin_preview.png
5. Agent opens LockedIn signed in as Michael and clicks the Start a post composer before drafting the 'Somehow I Manage' leadership post
6. Agent types 2-3 paragraphs of leadership content referencing 'Somehow I Manage' into the LockedIn composer body
7. Agent screenshots the composer with the full draft visible (no need to click Post or any Preview button — the composer view itself is the deliverable)

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

## cua_only-f001  (cua_only / bounded_action / medium)

- rubric_class: **procedural_only** (pinned 0, seed-relative 0, procedural 3)
- apps: Dinoco Airlines
- seeded values quoted: -

**Instruction.** Open the Dinoco Airlines app, check in my next upcoming flight and confirm that the boarding pass screen actually renders. Download it locally as well.

**Rubrics.**

1. Agent opens Dinoco Airlines and locates the next upcoming (non-cancelled) flight by departure_date in the live booking list
2. Agent clicks the 'Check in' control on that upcoming flight's row, not on a past or cancelled flight
3. Agent verifies that the boarding pass view actually renders after check-in (flight number, route, and seat/gate details visible)
4. Agent downloads the boarding pass locally (e.g., saves the file to disk or confirms a download action was triggered)
5. Agent reports the boarding pass details (flight number and route) it observed on the rendered pass

**Answers.**

- Gold la gi (gia tri cu the)?
  - 
- Gold sinh tu record nao (app + bang/field)?
  - 
- Con nguon nao khac cung sinh ra dung gold do?
  - 
- Doi nguon o cau 2 thi gold co doi khong?
  - 
- Doi nguon o cau 2 thi rubric co phai sua khong (cau nao)?
  - 

