# Tier 1 schema extract

Source: `out/db_schema.json` (host copy of guest sqlite, not a new QEMU boot).
No SQL patches written. `_sql_status` stays `PENDING_GUEST_SCHEMA` until
someone maps D → columns and fills `cf/paper2_interventions.json`.

Order: single-I, then multi-I.

## `aggregation-f004` — single-I

- D: philly_hotel_total, philly_card_incidentals
- held: —

### `cheskepdia.sqlite` (`/data/cheskepdia.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `booking_messages` | 14 | id:INTEGER, canonical_message_key:TEXT, booking_id:INTEGER, user_email:TEXT, sender_type:TEXT, sender_name:TEXT, mess... |
| `bookings` | 8 | id:INTEGER, canonical_booking_id:TEXT, user_email:TEXT, source_listing_id:TEXT, catalog_source:TEXT, property_name:TE... |
| `loyalty_programs` | 3 | id:INTEGER, user_email:TEXT, program_name:TEXT, tier:TEXT, member_id:TEXT, points:INTEGER, world_id:TEXT, actor_id:TE... |
| `saved_properties` | 5 | id:INTEGER, user_email:TEXT, property_name:TEXT, property_type:TEXT, location:TEXT, price_per_night:REAL, rating:REAL... |
| `search_results` | 13 | id:INTEGER, source_listing_id:TEXT, catalog_source:TEXT, source_snapshot_date:TEXT, source_url:TEXT, property_name:TE... |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

## `aggregation-f020` — single-I

- D: card_balance, batbucks_cash
- held: card_limit

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `batbucks.sqlite` (`/data/batbucks.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `analyst_ratings` | 14 | ticker:TEXT, buy_count:INTEGER, hold_count:INTEGER, sell_count:INTEGER, consensus:TEXT, target_low:REAL, target_avera... |
| `batbucks_meta` | 2 | key:TEXT, value:TEXT |
| `dividends` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, amount:REAL, pay_date:TEXT, status:TEXT |
| `historical_prices` | 840 | id:INTEGER, ticker:TEXT, interval:TEXT, sampled_at:TEXT, open:REAL, high:REAL, low:REAL, close:REAL, volume:INTEGER |
| `holdings` | 5 | id:INTEGER, user_email:TEXT, ticker:TEXT, shares:REAL, avg_cost:REAL |
| `orders` | 10 | id:INTEGER, user_email:TEXT, ticker:TEXT, side:TEXT, shares:REAL, order_type:TEXT, time_in_force:TEXT, status:TEXT, s... |
| `portfolio` | 1 | id:INTEGER, user_email:TEXT, cash:REAL, created_at:TEXT |
| `portfolio_history` | 30 | id:INTEGER, user_email:TEXT, interval:TEXT, sampled_at:TEXT, total_value:REAL, cash_value:REAL, invested_value:REAL |
| `price_alerts` | 4 | id:INTEGER, user_email:TEXT, ticker:TEXT, direction:TEXT, target_price:REAL, status:TEXT, created_at:TEXT, triggered_... |
| `stock_news` | 52 | id:INTEGER, ticker:TEXT, headline:TEXT, source:TEXT, published_at:TEXT, url:TEXT, summary:TEXT |
| `stock_profiles` | 14 | ticker:TEXT, name:TEXT, sector:TEXT, description:TEXT, market_cap:REAL, pe:REAL, eps:REAL, dividend_yield:REAL, fifty... |
| `transfers` | 9 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, status:TEXT, reference:TEXT, created_at:TEXT, completed_at:TEXT |
| `watchlist_groups` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, sort_order:INTEGER |
| `watchlist_items` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, group_id:INTEGER, added_at:TEXT |

## `aggregation-f036` — single-I

- D: improv_spend_last_full_year
- held: improv_txn_count_last_full_year

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

## `contradiction-f003` — single-I

- D: loyalty_tier, loyalty_miles
- held: —

### `dinoco-airlines.sqlite` (`/data/dinoco-airlines.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `boarding_passes` | 0 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, passenger_name:TEXT, barcode:TEXT, qr_payload:TEXT, boarding_group:TE... |
| `flight_alternatives` | 11 | id:INTEGER, flight_id:INTEGER, alternative_key:TEXT, flight_number:TEXT, departure_date:TEXT, departure_time:TEXT, ar... |
| `flight_baggage` | 7 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, checked_bag_count:INTEGER, first_bag_free:INTEGER, total_price:INTEGE... |
| `flight_passengers` | 7 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, full_name:TEXT, date_of_birth:TEXT, gender:TEXT, tsa_precheck:INTEGER... |
| `flight_seats` | 1024 | id:INTEGER, flight_id:INTEGER, seat_number:TEXT, cabin:TEXT, row_number:INTEGER, seat_letter:TEXT, status:TEXT, world... |
| `flight_upgrades` | 12 | id:INTEGER, flight_id:INTEGER, upgrade_key:TEXT, cabin_class:TEXT, price_difference:INTEGER, seat_hint:TEXT, perks:TE... |
| `flights` | 7 | id:INTEGER, user_email:TEXT, flight_number:TEXT, origin:TEXT, origin_city:TEXT, destination:TEXT, destination_city:TE... |
| `loyalty` | 1 | id:INTEGER, user_email:TEXT, status:TEXT, miles:INTEGER, miles_ytd:INTEGER, medallion_qualifying_miles:INTEGER, membe... |
| `passenger_profiles` | 1 | id:INTEGER, user_email:TEXT, full_name:TEXT, date_of_birth:TEXT, gender:TEXT, tsa_precheck:INTEGER, passport_number:T... |
| `payment_methods` | 1 | id:INTEGER, user_email:TEXT, cardholder_name:TEXT, card_brand:TEXT, last4:TEXT, exp_month:TEXT, exp_year:TEXT, billin... |
| `travel_credits` | 1 | id:INTEGER, user_email:TEXT, amount:INTEGER, balance_remaining:INTEGER, created_at:TEXT, expires_at:TEXT, source_book... |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

## `contradiction-f004` — single-I

- D: batbucks_gme_shares, oddsmarket_gme_yes
- held: gme_avg_cost

### `batbucks.sqlite` (`/data/batbucks.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `analyst_ratings` | 14 | ticker:TEXT, buy_count:INTEGER, hold_count:INTEGER, sell_count:INTEGER, consensus:TEXT, target_low:REAL, target_avera... |
| `batbucks_meta` | 2 | key:TEXT, value:TEXT |
| `dividends` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, amount:REAL, pay_date:TEXT, status:TEXT |
| `historical_prices` | 840 | id:INTEGER, ticker:TEXT, interval:TEXT, sampled_at:TEXT, open:REAL, high:REAL, low:REAL, close:REAL, volume:INTEGER |
| `holdings` | 5 | id:INTEGER, user_email:TEXT, ticker:TEXT, shares:REAL, avg_cost:REAL |
| `orders` | 10 | id:INTEGER, user_email:TEXT, ticker:TEXT, side:TEXT, shares:REAL, order_type:TEXT, time_in_force:TEXT, status:TEXT, s... |
| `portfolio` | 1 | id:INTEGER, user_email:TEXT, cash:REAL, created_at:TEXT |
| `portfolio_history` | 30 | id:INTEGER, user_email:TEXT, interval:TEXT, sampled_at:TEXT, total_value:REAL, cash_value:REAL, invested_value:REAL |
| `price_alerts` | 4 | id:INTEGER, user_email:TEXT, ticker:TEXT, direction:TEXT, target_price:REAL, status:TEXT, created_at:TEXT, triggered_... |
| `stock_news` | 52 | id:INTEGER, ticker:TEXT, headline:TEXT, source:TEXT, published_at:TEXT, url:TEXT, summary:TEXT |
| `stock_profiles` | 14 | ticker:TEXT, name:TEXT, sector:TEXT, description:TEXT, market_cap:REAL, pe:REAL, eps:REAL, dividend_yield:REAL, fifty... |
| `transfers` | 9 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, status:TEXT, reference:TEXT, created_at:TEXT, completed_at:TEXT |
| `watchlist_groups` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, sort_order:INTEGER |
| `watchlist_items` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, group_id:INTEGER, added_at:TEXT |

### `oddsmarket.sqlite` (`/data/oddsmarket.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `account` | 1 | id:INTEGER, user_email:TEXT, balance:REAL, total_invested:REAL, net_pnl:REAL, win_rate:REAL, seed_version:INTEGER |
| `account_activity` | 10 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, created_at:TEXT |
| `open_orders` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, action:TEXT, shares:INTEGER, lim... |
| `positions` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, shares:INTEGER, avg_price:REAL, ... |
| `trade_history` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, action:TEXT, side:TEXT, shares:INTEGER, price:REAL, date... |
| `watchlist` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT |

## `contradiction-f017` — single-I

- D: largest_gringotts_spend, largest_batbucks_buy
- held: —

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `batbucks.sqlite` (`/data/batbucks.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `analyst_ratings` | 14 | ticker:TEXT, buy_count:INTEGER, hold_count:INTEGER, sell_count:INTEGER, consensus:TEXT, target_low:REAL, target_avera... |
| `batbucks_meta` | 2 | key:TEXT, value:TEXT |
| `dividends` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, amount:REAL, pay_date:TEXT, status:TEXT |
| `historical_prices` | 840 | id:INTEGER, ticker:TEXT, interval:TEXT, sampled_at:TEXT, open:REAL, high:REAL, low:REAL, close:REAL, volume:INTEGER |
| `holdings` | 5 | id:INTEGER, user_email:TEXT, ticker:TEXT, shares:REAL, avg_cost:REAL |
| `orders` | 10 | id:INTEGER, user_email:TEXT, ticker:TEXT, side:TEXT, shares:REAL, order_type:TEXT, time_in_force:TEXT, status:TEXT, s... |
| `portfolio` | 1 | id:INTEGER, user_email:TEXT, cash:REAL, created_at:TEXT |
| `portfolio_history` | 30 | id:INTEGER, user_email:TEXT, interval:TEXT, sampled_at:TEXT, total_value:REAL, cash_value:REAL, invested_value:REAL |
| `price_alerts` | 4 | id:INTEGER, user_email:TEXT, ticker:TEXT, direction:TEXT, target_price:REAL, status:TEXT, created_at:TEXT, triggered_... |
| `stock_news` | 52 | id:INTEGER, ticker:TEXT, headline:TEXT, source:TEXT, published_at:TEXT, url:TEXT, summary:TEXT |
| `stock_profiles` | 14 | ticker:TEXT, name:TEXT, sector:TEXT, description:TEXT, market_cap:REAL, pe:REAL, eps:REAL, dividend_yield:REAL, fifty... |
| `transfers` | 9 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, status:TEXT, reference:TEXT, created_at:TEXT, completed_at:TEXT |
| `watchlist_groups` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, sort_order:INTEGER |
| `watchlist_items` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, group_id:INTEGER, added_at:TEXT |

## `contradiction-f022` — single-I

- D: zelle_sent_ytd, speedtax_charitable
- held: —

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

### `speedtax.sqlite` (`/data/speedtax.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `tax_data` | 59 | id:INTEGER, return_id:INTEGER, step:INTEGER, field_name:TEXT, field_value:TEXT |
| `tax_documents` | 6 | id:INTEGER, return_id:INTEGER, step:INTEGER, doc_type:TEXT, data_json:TEXT, created_at:TEXT, updated_at:TEXT |
| `tax_filing_events` | 14 | id:INTEGER, return_id:INTEGER, event_order:INTEGER, event_key:TEXT, title:TEXT, detail:TEXT, state:TEXT, occurred_at:... |
| `tax_returns` | 3 | id:INTEGER, user_email:TEXT, tax_year:INTEGER, status:TEXT, current_step:INTEGER, created_at:TEXT, filed_at:TEXT, las... |

## `counterfactual-f005` — single-I

- D: gme_shares, liquid_bank
- held: gme_avg_cost

### `batbucks.sqlite` (`/data/batbucks.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `analyst_ratings` | 14 | ticker:TEXT, buy_count:INTEGER, hold_count:INTEGER, sell_count:INTEGER, consensus:TEXT, target_low:REAL, target_avera... |
| `batbucks_meta` | 2 | key:TEXT, value:TEXT |
| `dividends` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, amount:REAL, pay_date:TEXT, status:TEXT |
| `historical_prices` | 840 | id:INTEGER, ticker:TEXT, interval:TEXT, sampled_at:TEXT, open:REAL, high:REAL, low:REAL, close:REAL, volume:INTEGER |
| `holdings` | 5 | id:INTEGER, user_email:TEXT, ticker:TEXT, shares:REAL, avg_cost:REAL |
| `orders` | 10 | id:INTEGER, user_email:TEXT, ticker:TEXT, side:TEXT, shares:REAL, order_type:TEXT, time_in_force:TEXT, status:TEXT, s... |
| `portfolio` | 1 | id:INTEGER, user_email:TEXT, cash:REAL, created_at:TEXT |
| `portfolio_history` | 30 | id:INTEGER, user_email:TEXT, interval:TEXT, sampled_at:TEXT, total_value:REAL, cash_value:REAL, invested_value:REAL |
| `price_alerts` | 4 | id:INTEGER, user_email:TEXT, ticker:TEXT, direction:TEXT, target_price:REAL, status:TEXT, created_at:TEXT, triggered_... |
| `stock_news` | 52 | id:INTEGER, ticker:TEXT, headline:TEXT, source:TEXT, published_at:TEXT, url:TEXT, summary:TEXT |
| `stock_profiles` | 14 | ticker:TEXT, name:TEXT, sector:TEXT, description:TEXT, market_cap:REAL, pe:REAL, eps:REAL, dividend_yield:REAL, fifty... |
| `transfers` | 9 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, status:TEXT, reference:TEXT, created_at:TEXT, completed_at:TEXT |
| `watchlist_groups` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, sort_order:INTEGER |
| `watchlist_items` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, group_id:INTEGER, added_at:TEXT |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

## `counterfactual-f010` — single-I

- D: liquid_cash, n_upcoming_flights
- held: —

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `dinoco-airlines.sqlite` (`/data/dinoco-airlines.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `boarding_passes` | 0 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, passenger_name:TEXT, barcode:TEXT, qr_payload:TEXT, boarding_group:TE... |
| `flight_alternatives` | 11 | id:INTEGER, flight_id:INTEGER, alternative_key:TEXT, flight_number:TEXT, departure_date:TEXT, departure_time:TEXT, ar... |
| `flight_baggage` | 7 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, checked_bag_count:INTEGER, first_bag_free:INTEGER, total_price:INTEGE... |
| `flight_passengers` | 7 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, full_name:TEXT, date_of_birth:TEXT, gender:TEXT, tsa_precheck:INTEGER... |
| `flight_seats` | 1024 | id:INTEGER, flight_id:INTEGER, seat_number:TEXT, cabin:TEXT, row_number:INTEGER, seat_letter:TEXT, status:TEXT, world... |
| `flight_upgrades` | 12 | id:INTEGER, flight_id:INTEGER, upgrade_key:TEXT, cabin_class:TEXT, price_difference:INTEGER, seat_hint:TEXT, perks:TE... |
| `flights` | 7 | id:INTEGER, user_email:TEXT, flight_number:TEXT, origin:TEXT, origin_city:TEXT, destination:TEXT, destination_city:TE... |
| `loyalty` | 1 | id:INTEGER, user_email:TEXT, status:TEXT, miles:INTEGER, miles_ytd:INTEGER, medallion_qualifying_miles:INTEGER, membe... |
| `passenger_profiles` | 1 | id:INTEGER, user_email:TEXT, full_name:TEXT, date_of_birth:TEXT, gender:TEXT, tsa_precheck:INTEGER, passport_number:T... |
| `payment_methods` | 1 | id:INTEGER, user_email:TEXT, cardholder_name:TEXT, card_brand:TEXT, last4:TEXT, exp_month:TEXT, exp_year:TEXT, billin... |
| `travel_credits` | 1 | id:INTEGER, user_email:TEXT, amount:INTEGER, balance_remaining:INTEGER, created_at:TEXT, expires_at:TEXT, source_book... |

## `counterfactual-f013` — single-I

- D: batbucks_dividends, oddsmarket_balance, gringotts_savings
- held: —

### `batbucks.sqlite` (`/data/batbucks.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `analyst_ratings` | 14 | ticker:TEXT, buy_count:INTEGER, hold_count:INTEGER, sell_count:INTEGER, consensus:TEXT, target_low:REAL, target_avera... |
| `batbucks_meta` | 2 | key:TEXT, value:TEXT |
| `dividends` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, amount:REAL, pay_date:TEXT, status:TEXT |
| `historical_prices` | 840 | id:INTEGER, ticker:TEXT, interval:TEXT, sampled_at:TEXT, open:REAL, high:REAL, low:REAL, close:REAL, volume:INTEGER |
| `holdings` | 5 | id:INTEGER, user_email:TEXT, ticker:TEXT, shares:REAL, avg_cost:REAL |
| `orders` | 10 | id:INTEGER, user_email:TEXT, ticker:TEXT, side:TEXT, shares:REAL, order_type:TEXT, time_in_force:TEXT, status:TEXT, s... |
| `portfolio` | 1 | id:INTEGER, user_email:TEXT, cash:REAL, created_at:TEXT |
| `portfolio_history` | 30 | id:INTEGER, user_email:TEXT, interval:TEXT, sampled_at:TEXT, total_value:REAL, cash_value:REAL, invested_value:REAL |
| `price_alerts` | 4 | id:INTEGER, user_email:TEXT, ticker:TEXT, direction:TEXT, target_price:REAL, status:TEXT, created_at:TEXT, triggered_... |
| `stock_news` | 52 | id:INTEGER, ticker:TEXT, headline:TEXT, source:TEXT, published_at:TEXT, url:TEXT, summary:TEXT |
| `stock_profiles` | 14 | ticker:TEXT, name:TEXT, sector:TEXT, description:TEXT, market_cap:REAL, pe:REAL, eps:REAL, dividend_yield:REAL, fifty... |
| `transfers` | 9 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, status:TEXT, reference:TEXT, created_at:TEXT, completed_at:TEXT |
| `watchlist_groups` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, sort_order:INTEGER |
| `watchlist_items` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, group_id:INTEGER, added_at:TEXT |

### `oddsmarket.sqlite` (`/data/oddsmarket.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `account` | 1 | id:INTEGER, user_email:TEXT, balance:REAL, total_invested:REAL, net_pnl:REAL, win_rate:REAL, seed_version:INTEGER |
| `account_activity` | 10 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, created_at:TEXT |
| `open_orders` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, action:TEXT, shares:INTEGER, lim... |
| `positions` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, shares:INTEGER, avg_price:REAL, ... |
| `trade_history` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, action:TEXT, side:TEXT, shares:INTEGER, price:REAL, date... |
| `watchlist` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

## `retrieval-f002` — single-I

- D: sandals_jamaica_confirmation
- held: —

### `cheskepdia.sqlite` (`/data/cheskepdia.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `booking_messages` | 14 | id:INTEGER, canonical_message_key:TEXT, booking_id:INTEGER, user_email:TEXT, sender_type:TEXT, sender_name:TEXT, mess... |
| `bookings` | 8 | id:INTEGER, canonical_booking_id:TEXT, user_email:TEXT, source_listing_id:TEXT, catalog_source:TEXT, property_name:TE... |
| `loyalty_programs` | 3 | id:INTEGER, user_email:TEXT, program_name:TEXT, tier:TEXT, member_id:TEXT, points:INTEGER, world_id:TEXT, actor_id:TE... |
| `saved_properties` | 5 | id:INTEGER, user_email:TEXT, property_name:TEXT, property_type:TEXT, location:TEXT, price_per_night:REAL, rating:REAL... |
| `search_results` | 13 | id:INTEGER, source_listing_id:TEXT, catalog_source:TEXT, source_snapshot_date:TEXT, source_url:TEXT, property_name:TE... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

## `retrieval-f005` — single-I

- D: monthly_recurring_total, designated_payee_amount
- held: monthly_payee_membership

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

## `aggregation-f040` — MULTI-I

- D: billpay_monthly_subtotal, improv_recurring_amount
- held: —

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

## `contradiction-f006` — MULTI-I

- D: jamaica_hotel_total, barbados_hotel_total, credit_headroom
- held: —

### `cheskepdia.sqlite` (`/data/cheskepdia.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `booking_messages` | 14 | id:INTEGER, canonical_message_key:TEXT, booking_id:INTEGER, user_email:TEXT, sender_type:TEXT, sender_name:TEXT, mess... |
| `bookings` | 8 | id:INTEGER, canonical_booking_id:TEXT, user_email:TEXT, source_listing_id:TEXT, catalog_source:TEXT, property_name:TE... |
| `loyalty_programs` | 3 | id:INTEGER, user_email:TEXT, program_name:TEXT, tier:TEXT, member_id:TEXT, points:INTEGER, world_id:TEXT, actor_id:TE... |
| `saved_properties` | 5 | id:INTEGER, user_email:TEXT, property_name:TEXT, property_type:TEXT, location:TEXT, price_per_night:REAL, rating:REAL... |
| `search_results` | 13 | id:INTEGER, source_listing_id:TEXT, catalog_source:TEXT, source_snapshot_date:TEXT, source_url:TEXT, property_name:TE... |

### `dinoco-airlines.sqlite` (`/data/dinoco-airlines.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `boarding_passes` | 0 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, passenger_name:TEXT, barcode:TEXT, qr_payload:TEXT, boarding_group:TE... |
| `flight_alternatives` | 11 | id:INTEGER, flight_id:INTEGER, alternative_key:TEXT, flight_number:TEXT, departure_date:TEXT, departure_time:TEXT, ar... |
| `flight_baggage` | 7 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, checked_bag_count:INTEGER, first_bag_free:INTEGER, total_price:INTEGE... |
| `flight_passengers` | 7 | id:INTEGER, flight_id:INTEGER, user_email:TEXT, full_name:TEXT, date_of_birth:TEXT, gender:TEXT, tsa_precheck:INTEGER... |
| `flight_seats` | 1024 | id:INTEGER, flight_id:INTEGER, seat_number:TEXT, cabin:TEXT, row_number:INTEGER, seat_letter:TEXT, status:TEXT, world... |
| `flight_upgrades` | 12 | id:INTEGER, flight_id:INTEGER, upgrade_key:TEXT, cabin_class:TEXT, price_difference:INTEGER, seat_hint:TEXT, perks:TE... |
| `flights` | 7 | id:INTEGER, user_email:TEXT, flight_number:TEXT, origin:TEXT, origin_city:TEXT, destination:TEXT, destination_city:TE... |
| `loyalty` | 1 | id:INTEGER, user_email:TEXT, status:TEXT, miles:INTEGER, miles_ytd:INTEGER, medallion_qualifying_miles:INTEGER, membe... |
| `passenger_profiles` | 1 | id:INTEGER, user_email:TEXT, full_name:TEXT, date_of_birth:TEXT, gender:TEXT, tsa_precheck:INTEGER, passport_number:T... |
| `payment_methods` | 1 | id:INTEGER, user_email:TEXT, cardholder_name:TEXT, card_brand:TEXT, last4:TEXT, exp_month:TEXT, exp_year:TEXT, billin... |
| `travel_credits` | 1 | id:INTEGER, user_email:TEXT, amount:INTEGER, balance_remaining:INTEGER, created_at:TEXT, expires_at:TEXT, source_book... |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

## `contradiction-f011` — MULTI-I

- D: claimed_charitable_2025, gringotts_donation_sum_2025
- held: —

### `speedtax.sqlite` (`/data/speedtax.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `tax_data` | 59 | id:INTEGER, return_id:INTEGER, step:INTEGER, field_name:TEXT, field_value:TEXT |
| `tax_documents` | 6 | id:INTEGER, return_id:INTEGER, step:INTEGER, doc_type:TEXT, data_json:TEXT, created_at:TEXT, updated_at:TEXT |
| `tax_filing_events` | 14 | id:INTEGER, return_id:INTEGER, event_order:INTEGER, event_key:TEXT, title:TEXT, detail:TEXT, state:TEXT, occurred_at:... |
| `tax_returns` | 3 | id:INTEGER, user_email:TEXT, tax_year:INTEGER, status:TEXT, current_step:INTEGER, created_at:TEXT, filed_at:TEXT, las... |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

## `counterfactual-f002` — MULTI-I

- D: liquid_cash, hotel_settle
- held: —

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

### `batbucks.sqlite` (`/data/batbucks.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `analyst_ratings` | 14 | ticker:TEXT, buy_count:INTEGER, hold_count:INTEGER, sell_count:INTEGER, consensus:TEXT, target_low:REAL, target_avera... |
| `batbucks_meta` | 2 | key:TEXT, value:TEXT |
| `dividends` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, amount:REAL, pay_date:TEXT, status:TEXT |
| `historical_prices` | 840 | id:INTEGER, ticker:TEXT, interval:TEXT, sampled_at:TEXT, open:REAL, high:REAL, low:REAL, close:REAL, volume:INTEGER |
| `holdings` | 5 | id:INTEGER, user_email:TEXT, ticker:TEXT, shares:REAL, avg_cost:REAL |
| `orders` | 10 | id:INTEGER, user_email:TEXT, ticker:TEXT, side:TEXT, shares:REAL, order_type:TEXT, time_in_force:TEXT, status:TEXT, s... |
| `portfolio` | 1 | id:INTEGER, user_email:TEXT, cash:REAL, created_at:TEXT |
| `portfolio_history` | 30 | id:INTEGER, user_email:TEXT, interval:TEXT, sampled_at:TEXT, total_value:REAL, cash_value:REAL, invested_value:REAL |
| `price_alerts` | 4 | id:INTEGER, user_email:TEXT, ticker:TEXT, direction:TEXT, target_price:REAL, status:TEXT, created_at:TEXT, triggered_... |
| `stock_news` | 52 | id:INTEGER, ticker:TEXT, headline:TEXT, source:TEXT, published_at:TEXT, url:TEXT, summary:TEXT |
| `stock_profiles` | 14 | ticker:TEXT, name:TEXT, sector:TEXT, description:TEXT, market_cap:REAL, pe:REAL, eps:REAL, dividend_yield:REAL, fifty... |
| `transfers` | 9 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, status:TEXT, reference:TEXT, created_at:TEXT, completed_at:TEXT |
| `watchlist_groups` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, sort_order:INTEGER |
| `watchlist_items` | 12 | id:INTEGER, user_email:TEXT, ticker:TEXT, group_id:INTEGER, added_at:TEXT |

### `oddsmarket.sqlite` (`/data/oddsmarket.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `account` | 1 | id:INTEGER, user_email:TEXT, balance:REAL, total_invested:REAL, net_pnl:REAL, win_rate:REAL, seed_version:INTEGER |
| `account_activity` | 10 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, created_at:TEXT |
| `open_orders` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, action:TEXT, shares:INTEGER, lim... |
| `positions` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, shares:INTEGER, avg_price:REAL, ... |
| `trade_history` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, action:TEXT, side:TEXT, shares:INTEGER, price:REAL, date... |
| `watchlist` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT |

### `cheskepdia.sqlite` (`/data/cheskepdia.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `booking_messages` | 14 | id:INTEGER, canonical_message_key:TEXT, booking_id:INTEGER, user_email:TEXT, sender_type:TEXT, sender_name:TEXT, mess... |
| `bookings` | 8 | id:INTEGER, canonical_booking_id:TEXT, user_email:TEXT, source_listing_id:TEXT, catalog_source:TEXT, property_name:TE... |
| `loyalty_programs` | 3 | id:INTEGER, user_email:TEXT, program_name:TEXT, tier:TEXT, member_id:TEXT, points:INTEGER, world_id:TEXT, actor_id:TE... |
| `saved_properties` | 5 | id:INTEGER, user_email:TEXT, property_name:TEXT, property_type:TEXT, location:TEXT, price_per_night:REAL, rating:REAL... |
| `search_results` | 13 | id:INTEGER, source_listing_id:TEXT, catalog_source:TEXT, source_snapshot_date:TEXT, source_url:TEXT, property_name:TE... |

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

## `counterfactual-f003` — MULTI-I

- D: venue_planned, credit_headroom
- held: —

### `mail.sqlite` (`/data/mail.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `_mail_meta` | 1 | key:TEXT, value:TEXT |
| `attachments` | 6 | id:INTEGER, user_email:TEXT, scope_type:TEXT, scope_id:TEXT, file_name:TEXT, file_size:INTEGER, mime_type:TEXT, stora... |
| `contacts` | 21 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, frequency:INTEGER |
| `drafts` | 0 | id:INTEGER, user_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, created_at:TEXT, updated_at:TEXT, attachment_sco... |
| `emails` | 2426 | id:INTEGER, user_email:TEXT, from_name:TEXT, from_email:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, body_html:TEXT,... |
| `emails_send_idempotency_cache` | 0 | user_email:TEXT, idempotency_key:TEXT, response_json:TEXT, created_at:TEXT |
| `filters` | 6 | id:INTEGER, user_email:TEXT, from_pattern:TEXT, to_pattern:TEXT, subject_pattern:TEXT, has_words:TEXT, action_label:T... |
| `labels` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, color:TEXT, world_id:TEXT, vm_id:TEXT, actor_id:TEXT |
| `mail_entry_state` | 2422 | user_email:TEXT, email_id:INTEGER, folder:TEXT, read:INTEGER, starred:INTEGER, important:INTEGER, labels:TEXT, snooze... |
| `mail_threads` | 1719 | user_email:TEXT, thread_id:TEXT, subject:TEXT, subject_normalized:TEXT, participant_emails:TEXT, participant_actor_id... |
| `message_metadata` | 0 | user_email:TEXT, source:TEXT, message_id:INTEGER, to_recipients:TEXT, cc_email:TEXT, bcc_email:TEXT, body_html:TEXT, ... |
| `sent` | 0 | id:INTEGER, user_email:TEXT, to_name:TEXT, to_email:TEXT, subject:TEXT, body:TEXT, date:TEXT, thread_id:TEXT, subject... |
| `user_preferences` | 1 | user_email:TEXT, signature:TEXT, vacation_enabled:INTEGER, vacation_subject:TEXT, vacation_body:TEXT, vacation_start_... |

### `hoolishop.sqlite` (`/data/hoolishop.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `cart_items` | 2 | id:INTEGER, user_email:TEXT, world_id:TEXT, actor_id:TEXT, vm_id:TEXT, product_id:INTEGER, quantity:INTEGER, added_at... |
| `hoolishop_meta` | 1 | key:TEXT, value:TEXT |
| `order_timeline_events` | 263 | id:INTEGER, order_id:INTEGER, status:TEXT, label:TEXT, created_at:TEXT |
| `orders` | 66 | id:INTEGER, user_email:TEXT, world_id:TEXT, actor_id:TEXT, vm_id:TEXT, status:TEXT, total:REAL, subtotal:REAL, shippi... |
| `products` | 85 | id:INTEGER, title:TEXT, description:TEXT, price:REAL, original_price:REAL, category:TEXT, department:TEXT, image_url:... |
| `saved_addresses` | 2 | id:INTEGER, user_email:TEXT, world_id:TEXT, actor_id:TEXT, vm_id:TEXT, label:TEXT, full_name:TEXT, street:TEXT, city:... |
| `subscribe_save` | 3 | id:INTEGER, user_email:TEXT, world_id:TEXT, actor_id:TEXT, vm_id:TEXT, product_id:INTEGER, frequency:TEXT, discount_p... |
| `subscriptions` | 1 | id:INTEGER, user_email:TEXT, world_id:TEXT, actor_id:TEXT, vm_id:TEXT, product_id:INTEGER, frequency:TEXT, discount_p... |
| `tax_rates` | 10 | id:INTEGER, state:TEXT, rate:REAL |
| `wishlist_shares` | 1 | id:INTEGER, wishlist_id:INTEGER, share_token:TEXT, created_at:TEXT |
| `wishlists` | 4 | id:INTEGER, user_email:TEXT, world_id:TEXT, actor_id:TEXT, vm_id:TEXT, name:TEXT, product_ids:TEXT, created_at:TEXT |

### `hangrydash.sqlite` (`/data/hangrydash.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `cart_items` | 2 | id:INTEGER, user_email:TEXT, restaurant_id:INTEGER, menu_item_id:INTEGER, quantity:INTEGER, customizations:TEXT |
| `cart_settings` | 0 | user_email:TEXT, restaurant_id:INTEGER, fulfillment_type:TEXT, updated_at:TEXT |
| `credit_ledger` | 13 | id:INTEGER, user_email:TEXT, amount:REAL, entry_type:TEXT, description:TEXT, order_id:INTEGER, created_at:TEXT |
| `menu_items` | 132 | id:INTEGER, restaurant_id:INTEGER, name:TEXT, description:TEXT, price:REAL, category:TEXT, image_url:TEXT |
| `order_issue_reports` | 19 | id:INTEGER, order_id:INTEGER, user_email:TEXT, category:TEXT, details:TEXT, status:TEXT, resolution_note:TEXT, create... |
| `order_reviews` | 112 | id:INTEGER, order_id:INTEGER, user_email:TEXT, restaurant_id:INTEGER, rating:INTEGER, review_text:TEXT, created_at:TEXT |
| `order_timeline_events` | 1974 | id:INTEGER, order_id:INTEGER, step_key:TEXT, step_label:TEXT, event_time:TEXT, sort_order:INTEGER |
| `orders` | 399 | id:INTEGER, user_email:TEXT, restaurant_id:INTEGER, date:TEXT, status:TEXT, subtotal:REAL, tax:REAL, service_fee:REAL... |
| `promo_codes` | 11 | id:INTEGER, code:TEXT, description:TEXT, discount_type:TEXT, discount_value:REAL, min_subtotal:REAL, is_active:INTEGER |
| `restaurants` | 28 | id:INTEGER, name:TEXT, cuisine:TEXT, rating:REAL, rating_count:INTEGER, delivery_time:TEXT, delivery_fee:REAL, image_... |
| `saved_addresses` | 2 | id:INTEGER, user_email:TEXT, label:TEXT, address:TEXT, is_default:INTEGER, latitude:REAL, longitude:REAL |
| `user_memberships` | 1 | user_email:TEXT, dashpass_enabled:INTEGER, updated_at:TEXT |

### `vaultbank.sqlite` (`/data/vaultbank.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `accounts` | 3 | id:INTEGER, user_email:TEXT, type:TEXT, name:TEXT, balance:REAL, credit_limit:REAL, account_number:TEXT, routing_numb... |
| `bill_pay` | 23 | id:INTEGER, user_email:TEXT, payee:TEXT, amount:REAL, due_date:TEXT, autopay:INTEGER, frequency:TEXT, last_paid:TEXT |
| `bill_payments` | 9 | id:INTEGER, user_email:TEXT, bill_id:INTEGER, payee:TEXT, source_account_id:INTEGER, amount:REAL, scheduled_date:TEXT... |
| `credit_score_factors` | 5 | id:INTEGER, user_email:TEXT, label:TEXT, status:TEXT, impact:TEXT, description:TEXT, sort_order:INTEGER |
| `credit_score_reports` | 8 | id:INTEGER, user_email:TEXT, bureau:TEXT, score:INTEGER, reported_at:TEXT |
| `investment_accounts` | 1 | id:INTEGER, user_email:TEXT, name:TEXT, cash_balance:REAL, last_updated:TEXT |
| `investment_holdings` | 5 | id:INTEGER, investment_account_id:INTEGER, symbol:TEXT, name:TEXT, quantity:REAL, price:REAL, price_change:REAL, cost... |
| `investment_performance` | 9 | id:INTEGER, investment_account_id:INTEGER, date:TEXT, total_value:REAL |
| `notifications` | 6 | id:INTEGER, user_email:TEXT, title:TEXT, body:TEXT, date:TEXT, read:INTEGER |
| `transactions` | 1634 | id:INTEGER, account_id:INTEGER, date:TEXT, description:TEXT, amount:REAL, category:TEXT, status:TEXT, running_balance... |
| `user_preferences` | 1 | user_email:TEXT, email_alerts:INTEGER, sms_alerts:INTEGER, push_alerts:INTEGER, bill_due_alerts:INTEGER, security_ale... |
| `user_profiles` | 1 | user_email:TEXT, full_name:TEXT, phone:TEXT, street:TEXT, city:TEXT, state:TEXT, zip_code:TEXT |
| `user_security_settings` | 1 | user_email:TEXT, two_factor_enabled:INTEGER, biometric_enabled:INTEGER, login_alerts:INTEGER, trusted_devices:INTEGER... |
| `vaultbank_billers` | 8 | id:INTEGER, user_email:TEXT, name:TEXT, address:TEXT, account_number:TEXT, category:TEXT, created_at:TEXT |
| `zelle_contacts` | 14 | id:INTEGER, user_email:TEXT, name:TEXT, email:TEXT, phone:TEXT |
| `zelle_transfers` | 29 | id:INTEGER, user_email:TEXT, direction:TEXT, contact_name:TEXT, contact_email:TEXT, contact_phone:TEXT, amount:REAL, ... |

## `retrieval-f017` — MULTI-I

- D: total_invested, n_open_positions
- held: —

### `oddsmarket.sqlite` (`/data/oddsmarket.sqlite`)

| table | n_rows | columns |
| --- | ---: | --- |
| `account` | 1 | id:INTEGER, user_email:TEXT, balance:REAL, total_invested:REAL, net_pnl:REAL, win_rate:REAL, seed_version:INTEGER |
| `account_activity` | 10 | id:INTEGER, user_email:TEXT, type:TEXT, amount:REAL, created_at:TEXT |
| `open_orders` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, action:TEXT, shares:INTEGER, lim... |
| `positions` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT, side:TEXT, shares:INTEGER, avg_price:REAL, ... |
| `trade_history` | 5 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, action:TEXT, side:TEXT, shares:INTEGER, price:REAL, date... |
| `watchlist` | 4 | id:INTEGER, user_email:TEXT, market_ticker:TEXT, title:TEXT, source:TEXT |

