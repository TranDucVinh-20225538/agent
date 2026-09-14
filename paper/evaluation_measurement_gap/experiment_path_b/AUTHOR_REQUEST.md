# Screenshot request (B2 blocker)

Released WebJudge JSON has `{Response, Score}` only. B2 needs v2
`trajectory/*.png` aligned to `image_judge_record` order.

Public contact from the Online-Mind2Web leaderboard: `xue.681@osu.edu`
(Xue et al. / OSU NLP). Operator traces were collected via the Operator
web UI, not an API (HF space discussion #8).

Do not send this agent as an annotator. Do not ask authors to label
DECISIVE. Ask only for the existing screenshot dump (or a research
share of the 30 sampled task folders).

## Email draft

Subject: Research request: Online-Mind2Web Operator (and control) screenshots for a collect-then-filter audit

Hi Xue / Online-Mind2Web authors,

We are auditing WebJudge's collect-then-filter step
(`score >= 3`, then `whole_content_img[:50]`) on the released
`webjudge_o4-mini` products. At T=3 the cap fires on 10/1790
episodes, all Operator.

The public JSON does not include screenshot bytes. Could you share,
for research use only, the original v2 task folders
(`result.json` + `trajectory/*.png`) for the task_ids below? We
need frame order to match `image_judge_record`. We will not
redistribute the images.

Priority (10 Operator cap-hits):

- 2e4e21cf1449c6894b17d571c47b77ea
- 33bd2cdcea4fcc42a09a8a1e4e5841c6
- 4639a54f3ab549864fd8d60b7398b1e1
- 6b2cfae0ef25c73d1224b6ab74cb8b63
- 753f372c189d3b306623cb0c65b50320
- 7e1047f4803237f319c004f7a7f6bccb
- a13e4231a3d6a7000c622c56448d97ba
- b2f4fde2fce122a93c7b578086cb0585
- b3f8bd9198d9d157e0848109563c4b23
- fe33894188d20d7469f37a9fd855e7ff

If a bulk share of all Operator (300) plus the 10 other-agent
controls in `experiment_path_b/out/b2_episode_sample.csv` is easier,
that is better.

We are not asking you to re-run WebJudge or to label frames.

Thanks,
[name]

## If authors cannot share

B2 stays blocked. Do not substitute:

- LLM-as-annotator on `Response` text
- `Score` as DECISIVE
- task-level `human_label` as frame gold
- replaying live sites (pages have changed; not the judged τ)

A new self-collected Operator/Browser-Use corpus would be a
**different instrument**, not an audit of the released WebJudge
product. Only open that if the paper explicitly drops “on the
released Online-Mind2Web judge product.”
