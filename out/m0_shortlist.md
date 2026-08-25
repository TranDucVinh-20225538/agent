# Milestone 0 - hand-read shortlist

Screening pass proposes the class of each rubric criterion; these ten are read by hand to check whether the machine label holds and whether a counterfactual keeps the task well defined.

| task | category | rubrics | apps | attributable weight | rubric edit needed | variables quoted |
| --- | --- | --- | --- | --- | --- | --- |
| `retrieval-f029` | retrieval | 3 | 2 | 1.00 | yes | LOCKEDIN_COMPANY |
| `retrieval-f010` | retrieval | 4 | 1 | 1.00 | yes | JAMAICA_HOTEL_NAME |
| `retrieval-f030` | retrieval | 4 | 2 | 1.00 | yes | SPEEDTAX_1099_PAYER |
| `preference_inference-f012` | preference_inference | 4 | 1 | 1.00 | yes | TABLEFIND_NEXT_RESERVATION_RESTAURANT |
| `preference_inference-f025` | preference_inference | 7 | 2 | 0.93 | no | - |
| `preference_inference-f009` | preference_inference | 6 | 1 | 0.93 | no | - |
| `situated_action-f009` | situated_action | 4 | 1 | 1.00 | yes | DUNDIES_DOC_VENUE |
| `situated_action-f011` | situated_action | 4 | 1 | 1.00 | yes | - |
| `situated_action-f028` | situated_action | 4 | 1 | 0.00 | no | - |
| `situated_action-f026` | situated_action | 4 | 1 | 0.00 | no | - |

## Per task

### `retrieval-f029`  (retrieval - point lookup: gold should be one seeded field)

**Instruction.** What was my gross income on my most-recent W-2, who was the employer, and how much federal tax got withheld? Double-check the numbers against ~/Documents/Tax_2025/w2_summary.txt and SpeedTax. I need the numbers for a thing.

Apps: SpeedTax, Files

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | record | 0.33 | Agent opens SpeedTax and locates the most-recent W-2 showing gross income and federal withholding fields |
| 2 | value | 0.33 | Agent reports the gross wages shown on the most-recent SpeedTax W-2 and Dunder Mifflin as the employer |
| 3 | record | 0.33 | Agent reports the federal withholding shown on the most-recent SpeedTax W-2 and cross-checks the value against w2_summary.txt |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `retrieval-f010`  (retrieval - point lookup: gold should be one seeded field)

**Instruction.** What was the total cost of my Jamaica trip — pull the trip total from the booking. Also tell me the host name on file and what amenities the property comes with so I know what I'm getting.

Apps: Cheskepdia

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | value | 0.25 | Agent opens Cheskepdia and loads the upcoming Sandals Montego Bay (Jamaica) booking |
| 2 | value | 0.25 | Agent reports the trip total cost as it is shown on the live Cheskepdia Sandals Montego Bay booking |
| 3 | value | 0.25 | Agent reports the host name as listed on the live Cheskepdia Sandals Montego Bay booking (Sandals Resorts Concierge) |
| 4 | value | 0.25 | Agent reports the amenities list shown on the live Cheskepdia Sandals Montego Bay booking (or notes that no amenities are listed if the booking shows none) |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `retrieval-f030`  (retrieval - point lookup: gold should be one seeded field)

**Instruction.** What was my 1099 income on the most-recent return, who paid it, and how much did I claim for charitable contributions? Cross-check the 1099 payer and amount against ~/Documents/Tax_2025/1099s.txt. This is for my accountant.

Apps: SpeedTax, Files

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | record | 0.27 | Agent opens SpeedTax and finds the most-recent 1099 entry showing the income amount and payer for the accountant summary |
| 2 | value | 0.27 | Agent reports the most-recent SpeedTax 1099 income amount from Scranton Improv Academy and the charitable-contribution total from the deductions section |
| 3 | value | 0.27 | Agent opens ~/Documents/Tax_2025/1099s.txt and cross-checks the 1099 income payer (Scranton Improv Academy) and amount against the SpeedTax value |
| 4 | record | 0.20 | Agent navigates to the most-recent SpeedTax return's deductions section and surfaces the charitable contributions line for the accountant summary |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `preference_inference-f012`  (preference_inference - latent: gold should be a statistic over records)

**Instruction.** Look at my HangryDash order history over the last few months. Am I really sticking to Sweetgreen healthy lunches like I tell people, or am I quietly defaulting to places like Chili's? Pull the data and tell me what my food preferences actually look like.

Apps: HangryDash

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | record | 0.25 | Agent opens HangryDash and enumerates Michael's order history (multiple orders, not a single order) |
| 2 | record | 0.25 | Agent computes order frequency per restaurant or per cuisine from the history (not just lists raw orders) |
| 3 | record | 0.25 | Agent identifies Michael's actually-most-ordered HangryDash restaurants (top 2-3 by live order count), citing specific order counts per restaurant from the live data |
| 4 | value | 0.25 | Agent gives a clear preference verdict on whether Michael is actually sticking to his stated 'healthy lunch' (Sweetgreen) narrative, backed by the live order-count distribution — calling out any gap between the stated preference and actual behavior |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `preference_inference-f025`  (preference_inference - latent: gold should be a statistic over records)

**Instruction.** What do I usually tip on food delivery, in dollars and as a percent? I want to set a smart default so I'm not thinking about it every order. Give me a report of all my orders and their tips in a LibreOffice spreadsheet.

Apps: HangryDash, LibreOffice Calc

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | record | 0.21 | Agent queries tip_amount and subtotal at the order-level for the HangryDash food-delivery tip analysis, covering Michael's full order history |
| 2 | record | 0.21 | Agent computes mean tip in both $ and % terms |
| 3 | record | 0.12 | Agent identifies the modal tip percent (15%, 18%, 20%, or custom) from the HangryDash order history |
| 4 | record | 0.12 | Agent recommends a defensible pre-fill default tip value grounded in the observed HangryDash tip pattern |
| 5 | record | 0.20 | Agent creates a LibreOffice Calc spreadsheet (.ods or .xlsx) containing a per-order row report with at minimum the order identifier, tip amount, and subtotal columns for Michael's HangryDash order history |
| 6 | record | 0.07 | Agent cites the HangryDash order-history tip rows as the data source for the recommended smart-default tip value, not inventing numbers |
| 7 | unclear | 0.07 | Agent delivers the full food-delivery tip answer in dollars and percent plus the smart-default recommendation and the LibreOffice spreadsheet |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `preference_inference-f009`  (preference_inference - latent: gold should be a statistic over records)

**Instruction.** What's my favorite grocery store, and what do I actually buy there? Rank my stores and give me a quick profile of my shopping habits in LibreOffice Writer. 

Apps: Kwik-E-Mart

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | record | 0.26 | Agent identifies Michael's favorite Kwik-E-Mart grocery store as the top-by-order-count store from live order history (/api/orders), naming whichever store has the plurality of orders |
| 2 | record | 0.21 | Agent reports the live order counts per store from Michael's Kwik-E-Mart order history (/api/orders), confirming the top-by-order-count store is ranked first ahead of the other stores Michael has used |
| 3 | record | 0.21 | Agent characterizes the typical line items Michael buys there |
| 4 | record | 0.16 | Agent writes a one-paragraph profile of Michael's Kwik-E-Mart grocery shopping habits at his favorite store |
| 5 | record | 0.08 | Agent reads Kwik-E-Mart order-history line items and states them as the data source backing the favorite grocery store ranking and buying profile |
| 6 | unclear | 0.07 | Agent delivers the favorite Kwik-E-Mart grocery store ranking and the buying-habits profile before ending the task |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `situated_action-f009`  (situated_action - latent gold consumed by an action)

**Instruction.** Order me my usual from Chili's — pick whichever item I've ordered most often from there, or just match my most recent Chili's order if multiple items are tied. Deliver to my place.

Apps: HangryDash

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | value | 0.21 | Agent identifies Chili's as the target restaurant and opens HangryDash order history to find Michael's prior Chili's orders |
| 2 | value | 0.33 | Agent places a Chili's order whose item(s) match Michael's most-frequent/modal item in his HangryDash Chili's order history (if two items tie for modal, either tied item is acceptable; matching the most-recent Chili's order is also acceptable as a tiebreaker) |
| 3 | record | 0.21 | Agent selects a delivery address on the order that matches Michael's saved home/primary HangryDash address |
| 4 | value | 0.25 | Agent adds the usual Chili's item(s) to the HangryDash cart and submits the order through the checkout flow so the order is placed |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `situated_action-f011`  (situated_action - latent gold consumed by an action)

**Instruction.** Can you knock $500 off my credit card from my checking? I'm trying to be responsible here.

Apps: Gringotts

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | value | 0.58 | Agent completes the $500 payment from checking to the credit card in Gringotts and confirms the payment posted |
| 2 | value | 0.17 | Agent cites the Gringotts checking account as the funding source and the credit card as the destination for the $500 payment |
| 3 | record | 0.08 | Agent transfers exactly $500 (not a different amount) from checking to the credit card, matching Michael's stated request to knock $500 off |
| 4 | value | 0.17 | Agent opens Gringotts, navigates into the credit card account view, and captures the displayed credit card balance before initiating the $500 payment |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `situated_action-f028`  (CONTROL - no rubric weight attributable to personal records)

**Instruction.** I'm feeling nostalgic. Book me an upcoming Scranton weekend, Friday through Sunday. Pick a well-rated property in town and book it.

Apps: Cheskepdia

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | action | 0.30 | Agent books a Scranton property on Cheskepdia with a future check-in date for the nostalgic weekend trip |
| 2 | unclear | 0.24 | Agent's booked Scranton stay spans Friday check-in through Sunday check-out as requested for the upcoming weekend |
| 3 | unclear | 0.24 | Agent browses the Cheskepdia Scranton search results and picks a well-rated property before booking |
| 4 | action | 0.23 | Agent confirms the new Cheskepdia Scranton booking details (property, Friday-to-Sunday dates, total) after submitting the reservation for the nostalgic weekend |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?

### `situated_action-f026`  (CONTROL - no rubric weight attributable to personal records)

**Instruction.** DM Jim and propose a near-future evening for the next Finer Things Club meetup. Pick something this week or next. He'd be a great addition; he has taste.

Apps: HooliChat

| # | class | w | criterion |
| --- | --- | --- | --- |
| 1 | action | 0.26 | Agent opens or starts a HooliChat DM thread with Jim Halpert before composing the Finer Things Club invite |
| 2 | unclear | 0.26 | Agent picks a reasonable near-future evening (this week or next) as the proposed Finer Things Club meetup time |
| 3 | action | 0.24 | Agent sends the DM to Jim Halpert as a one-on-one HooliChat message rather than posting it in a group channel |
| 4 | action | 0.24 | Agent writes a HooliChat DM body that proposes the chosen near-future evening to Jim and references the Finer Things Club meetup |

Questions to answer by hand:

1. What is the gold value?
2. Which records generate it?
3. Does any other record also generate it?
4. If those records change, does the gold change?
5. If those records change, must the rubric text change?
