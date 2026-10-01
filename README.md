# GemCTF: LLM Security Capture the Flag

A Gandalf-style CTF where each level has an AI guardian protecting a secret passphrase. Your goal: make the AI reveal it through creative prompting.

**Built by:** [CyberGemChick](https://github.com/cybergemchick) | AI Red Team

---

## What This Teaches

Each level demonstrates a real prompt injection or extraction technique. In the OWASP Top 10 for LLM Applications (2025 edition) these map to LLM01 Prompt Injection and LLM07 System Prompt Leakage. See the [OWASP project page](https://genai.owasp.org/llm-top-10/).

| Level | Name | Defense | Technique to learn |
|-------|------|---------|-------------------|
| 1 | Open Door | None | Baseline: ask directly |
| 2 | The First Lock | Basic secrecy instruction | Indirect extraction |
| 3 | Roleplay Bypass | Explicit refusal | Fictional framing, encoding |
| 4 | The Warden | Multi-rule prohibition | Gap analysis, training data |
| 5 | The Fortress | Paranoid + meta-injection resistance | Context manipulation, edge cases |

## Quick Start

```bash
pip install openai rich
export OPENAI_API_KEY=your-key-here
python ctf_challenge.py
```

```bash
# Start at a specific level
python ctf_challenge.py --level 3

# Use a different model
python ctf_challenge.py --model gpt-4o

# Trainer mode: see all solutions
python ctf_challenge.py --solve-mode
```

## How to Play

Each level loads a new AI guardian with a system prompt defending a secret passphrase.
Type messages in the terminal. If the guardian says the passphrase, you advance.

Type `hint` for a nudge. Type `quit` to exit.

## Learning Path

After completing GemCTF, explore:
- [Lakera Gandalf](https://gandalf.lakera.ai): the original LLM CTF
- [HackAPrompt](https://www.hackaprompt.com): competitive prompt injection
- [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/)
- [MITRE ATLAS AML.T0051](https://atlas.mitre.org/techniques/AML.T0051): LLM prompt injection

## For Trainers / Red Teams

Use `--solve-mode` to see every secret passphrase, defense and hint.
Swap the `secret` and `system_prompt` fields in `LEVELS` to build your own custom challenges for team training exercises.

## Tests

```bash
pip install pytest
pytest
```

The tests use a stub client, so they need no network or API key.

## Ethics

This tool is for education, security training, and red team skill development. All secrets are fictional words; no real credentials or sensitive data are involved.
