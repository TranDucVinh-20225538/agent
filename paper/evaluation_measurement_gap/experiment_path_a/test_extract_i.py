"""Synthetic extractor tests. Fixtures have no cum_reward and no human labels."""

import unittest

from extract_i import classify_i, episode_status, extract_ans, extract_url, parse_send_msg


def traj(**kwargs):
    base = {"valid": True, "summary_info": {"err_msg": None}, "steps": []}
    base.update(kwargs)
    return base


class ParseSend(unittest.TestCase):
    def test_click_is_not_send(self):
        self.assertIsNone(parse_send_msg("click('57')"))

    def test_send_double_quotes(self):
        self.assertEqual(parse_send_msg('send_msg_to_user("hello")'), "hello")

    def test_send_wrapped(self):
        self.assertEqual(
            parse_send_msg('<action>\nsend_msg_to_user("x")\n</action>'),
            "x",
        )

    def test_empty_send(self):
        self.assertEqual(parse_send_msg('send_msg_to_user("")'), "")


class Episode(unittest.TestCase):
    def test_valid_false(self):
        self.assertEqual(episode_status(traj(valid=False, steps=[{}])), "EXEC_FAIL")

    def test_err_msg(self):
        t = traj(summary_info={"err_msg": "Frame.evaluate: TypeError"}, steps=[{"action": "goto('u')"}])
        self.assertEqual(episode_status(t), "EXEC_FAIL")

    def test_no_steps(self):
        self.assertEqual(episode_status(traj(steps=[])), "EXEC_FAIL")

    def test_intact_goto_only(self):
        t = traj(steps=[{"action": "goto('https://x')", "url": "https://x"}, {"action": None, "url": "https://x"}])
        self.assertEqual(episode_status(t), "ELIGIBLE")


class Extract(unittest.TestCase):
    def test_ans_from_action_not_click_chat(self):
        t = traj(
            steps=[
                {
                    "action": "click('1')",
                    "url": "https://a",
                    "chat_messages": [{"role": "assistant", "content": "<action>\nclick('1')\n</action>"}],
                },
                {
                    "action": 'send_msg_to_user("Acadia")',
                    "url": "https://a",
                    "chat_messages": [
                        {"role": "assistant", "content": '<action>\nsend_msg_to_user("Acadia")\n</action>'}
                    ],
                },
                {"action": None, "url": "https://a", "chat_messages": []},
            ]
        )
        self.assertEqual(extract_ans(t), "Acadia")
        self.assertEqual(extract_url(t), "https://a")
        self.assertEqual(classify_i("string", t), "DETERMINING")

    def test_ans_from_chat_if_action_null(self):
        t = traj(
            steps=[
                {
                    "action": None,
                    "url": "https://a",
                    "chat_messages": [
                        {"role": "assistant", "content": 'send_msg_to_user("only-in-chat")'}
                    ],
                }
            ]
        )
        self.assertEqual(extract_ans(t), "only-in-chat")

    def test_goto_only_string_abstain_not_exec_fail(self):
        t = traj(steps=[{"action": "goto('https://reddit.com/')", "url": "https://reddit.com/"}])
        self.assertEqual(episode_status(t), "ELIGIBLE")
        self.assertIsNone(extract_ans(t))
        self.assertEqual(classify_i("string", t), "ABSTAIN")
        self.assertEqual(classify_i("url", t), "DETERMINING")
        self.assertEqual(classify_i("string_url", t), "ABSTAIN")

    def test_whitespace_ans_abstain(self):
        t = traj(steps=[{"action": 'send_msg_to_user("   ")', "url": "https://a"}])
        self.assertEqual(classify_i("string", t), "ABSTAIN")


if __name__ == "__main__":
    unittest.main()
