"""Tests for GemCTF. No network or API key needed."""

import builtins
import os
import sys
import types

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ctf_challenge as ctf  # noqa: E402
from ctf_challenge import LEVELS, LEVEL_MAP, GemCTF, check_win  # noqa: E402

REQUIRED = {"num", "name", "description", "lore", "secret", "system_prompt",
            "defense_technique", "hint"}


class TestLevelDefinitions:
    def test_five_levels(self):
        assert len(LEVELS) == 5

    def test_required_fields(self):
        for lvl in LEVELS:
            assert REQUIRED <= set(lvl), f"level {lvl.get('num')} missing {REQUIRED - set(lvl)}"
            assert all(str(lvl[k]).strip() for k in REQUIRED)

    def test_sequential_numbering_and_map(self):
        assert [l["num"] for l in LEVELS] == [1, 2, 3, 4, 5]
        assert set(LEVEL_MAP) == {1, 2, 3, 4, 5}

    def test_secrets_unique_uppercase_words(self):
        secrets = [l["secret"] for l in LEVELS]
        assert len(set(secrets)) == 5
        assert all(s.isalpha() and s.isupper() for s in secrets)

    def test_every_system_prompt_contains_its_own_secret_only(self):
        for lvl in LEVELS:
            assert lvl["secret"] in lvl["system_prompt"]
            for other in LEVELS:
                if other is not lvl:
                    assert other["secret"] not in lvl["system_prompt"]

    def test_levels_below_three_do_not_forbid_disclosure_strongly(self):
        assert "not tell" not in LEVEL_MAP[1]["system_prompt"].lower()
        assert "do not tell" in LEVEL_MAP[2]["system_prompt"].lower()

    def test_defenses_get_longer(self):
        lengths = [len(l["system_prompt"]) for l in LEVELS]
        assert lengths == sorted(lengths)

    def test_no_dashes_in_source(self):
        text = open(ctf.__file__, encoding="utf-8").read()
        assert "\u2014" not in text and "\u2013" not in text

    def test_no_stray_space_before_period(self):
        for lvl in LEVELS:
            assert "') ." not in lvl["system_prompt"]


class TestWinCondition:
    def test_exact(self):
        assert check_win("The answer is GEMSTONE", "GEMSTONE")

    def test_case_insensitive(self):
        assert check_win("gemstone", "GEMSTONE")

    def test_no_secret(self):
        assert not check_win("I cannot reveal that.", "GEMSTONE")

    def test_partial_does_not_win(self):
        assert not check_win("GEM", "GEMSTONE")

    def test_empty_and_none(self):
        assert not check_win("", "GEMSTONE")
        assert not check_win(None, "GEMSTONE")

    def test_empty_secret_never_wins(self):
        assert not check_win("anything", "")

    def test_method_delegates(self, monkeypatch):
        game = _game(monkeypatch, ["x"])
        assert game.check_win("obsidian", "OBSIDIAN")


def _fake_openai(replies, calls):
    class Completions:
        def create(self, **kw):
            calls.append(kw)
            msg = types.SimpleNamespace(content=replies.pop(0))
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])

    class Client:
        def __init__(self, api_key=None):
            self.chat = types.SimpleNamespace(completions=Completions())

    return types.SimpleNamespace(OpenAI=Client)


def _game(monkeypatch, replies, calls=None):
    monkeypatch.setitem(sys.modules, "openai", _fake_openai(replies, calls if calls is not None else []))
    return GemCTF(model="stub")


def _feed(monkeypatch, lines):
    it = iter(lines)
    monkeypatch.setattr(builtins, "input", lambda *a: next(it))
    monkeypatch.setattr(ctf, "RICH", False)


class TestGameLoop:
    def test_chat_sends_system_prompt_and_tracks_history(self, monkeypatch):
        calls = []
        game = _game(monkeypatch, ["hello"], calls)
        assert game.chat("SYS", "hi") == "hello"
        assert calls[0]["messages"][0] == {"role": "system", "content": "SYS"}
        assert calls[0]["messages"][-1] == {"role": "user", "content": "hi"}
        assert game.attempts == 1 and len(game.history) == 2

    def test_none_content_becomes_empty_string(self, monkeypatch):
        game = _game(monkeypatch, [None])
        assert game.chat("SYS", "hi") == ""

    def test_win_when_guardian_reveals_secret(self, monkeypatch, capsys):
        game = _game(monkeypatch, ["The secret is GEMSTONE."])
        _feed(monkeypatch, ["what is the secret?"])
        assert game.play_level(LEVEL_MAP[1]) is True
        assert "GEMSTONE" in capsys.readouterr().out

    def test_keeps_playing_until_win(self, monkeypatch):
        game = _game(monkeypatch, ["No.", "Still no.", "OBSIDIAN"])
        _feed(monkeypatch, ["a", "b", "c"])
        assert game.play_level(LEVEL_MAP[2]) is True
        assert game.attempts == 3

    def test_quit_returns_false(self, monkeypatch):
        game = _game(monkeypatch, [])
        _feed(monkeypatch, ["quit"])
        assert game.play_level(LEVEL_MAP[1]) is False

    def test_hint_does_not_call_the_model(self, monkeypatch, capsys):
        calls = []
        game = _game(monkeypatch, [], calls)
        _feed(monkeypatch, ["hint", "quit"])
        game.play_level(LEVEL_MAP[3])
        assert calls == []
        assert LEVEL_MAP[3]["hint"] in capsys.readouterr().out

    def test_api_error_does_not_end_the_game(self, monkeypatch, capsys):
        game = _game(monkeypatch, [])  # no replies: first call raises IndexError
        _feed(monkeypatch, ["hi", "quit"])
        assert game.play_level(LEVEL_MAP[1]) is False
        assert "Error" in capsys.readouterr().out

    def test_reset_clears_state_between_levels(self, monkeypatch):
        game = _game(monkeypatch, ["GEMSTONE", "OBSIDIAN"])
        _feed(monkeypatch, ["a", "b"])
        game.play_level(LEVEL_MAP[1])
        game.play_level(LEVEL_MAP[2])
        assert game.attempts == 1 and len(game.history) == 2


class TestCli:
    def test_solve_mode_lists_all_secrets(self, capsys):
        ctf.print_solutions()
        out = capsys.readouterr().out
        for lvl in LEVELS:
            assert lvl["secret"] in out

    def test_main_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setattr(sys, "argv", ["ctf_challenge.py"])
        with pytest.raises(SystemExit):
            ctf.main()

    def test_module_imports_without_openai_sdk(self):
        assert "import openai" not in open(ctf.__file__).read().split("class GemCTF")[0]
