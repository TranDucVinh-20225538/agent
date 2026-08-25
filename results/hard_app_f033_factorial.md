# hard_app-f033 factorial

| Condition | Time channel | Description channel | Agent decision | Judge score |
|-----------|--------------|---------------------|----------------|-------------|
| Baseline | overlap | overlap assertion present | reschedule-and-notify | 0.90 |
| A | no overlap | overlap assertion present | reschedule-and-notify | 1.00 |
| B | overlap | cleaned | reschedule-and-notify | 0.20 |
| A+B | no overlap | cleaned | all-clear | 0.51 |
