#!/usr/bin/env python3
"""Generate a new German A1 study day from the repo data."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_PATH = ROOT / "progress.json"
VERBS_PATH = ROOT / "data" / "verbs_a1.json"
GRAMMAR_PATH = ROOT / "data" / "grammar_plan.json"
DAYS_DIR = ROOT / "days"
CURRENT_STATE_PATH = ROOT / "CURRENT_STATE.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def day_label(day_number: int) -> str:
    return f"{day_number:03d}"


def pick_grammar(grammar_plan: list[dict], progress: dict) -> dict:
    """Keep lessons aligned to textbook progress, not GitHub tracking-day number."""
    next_page = int(progress.get("course_progress", {}).get("next_pdf_page", 1))
    eligible = [item for item in grammar_plan if int(item["source_page"]) <= next_page]
    return eligible[-1] if eligible else grammar_plan[0]


def select_verbs(verbs: list[dict], mapped: list[dict], progress: dict, day_number: int, count: int):
    """Prefer verified page mappings; disclose when verbs are generic A1 practice."""
    page = int(progress.get("course_progress", {}).get("next_printed_page", 1))
    used = {v for session in progress.get("lesson_sessions", []) for v in session.get("verbs", [])}
    entry = next((e for e in mapped if int(e["printed_page"]) == page), None)
    page_verbs = [v for v in entry.get("verbs", []) if v["verb"] not in used] if entry else []
    chosen = page_verbs[:count]
    selected_names = {v["verb"] for v in chosen}
    general = [v for v in verbs if v["verb"] not in used and v["verb"] not in selected_names]
    general += [v for v in verbs if v["verb"] in used and v["verb"] not in selected_names]
    needed = count - len(chosen)
    if len(general) < needed:
        raise ValueError("Insufficient distinct verbs in the general vocabulary data")
    offset = ((day_number - 1) * count) % len(general) if general else 0
    chosen += [general[(offset + i) % len(general)] for i in range(needed)]
    source = (
        f"Book page {page}: {len(page_verbs[:count])} mapped verbs; "
        f"remaining {needed} are general A1 practice, NOT verified on the page."
        if page_verbs else f"General A1 practice only; no unused verb mapping for printed page {page}."
    )
    return chosen, source


def verbs_table(selected: list[dict]) -> str:
    rows = ["| # | Verb | Arabic | Example | Translation | Note |", "| ---: | --- | --- | --- | --- | --- |"]
    for i, item in enumerate(selected, start=1):
        rows.append(
            f"| {i} | {item['verb']} | {item['meaning_ar']} | {item['example_de']} | {item['example_ar']} | {item.get('note', '')} |"
        )
    return "\n".join(rows)


def review_due_text(day_number: int, progress: dict) -> str:
    if day_number <= 1:
        return "- Baseline day: review alphabet, articles, pronouns, and self-introduction."

    intervals = set(progress.get("review_schedule", {}).get("intervals_after_day", [1, 3, 7, 14, 30]))
    generated = progress.get("generated_days", [])
    due = [item for item in generated if item.get("completed") and day_number - int(item["day"]) in intervals]

    if not due:
        return "- No spaced-review day is due. Review yesterday plus mistake patterns."

    lines = []
    for item in due:
        lines.append(f"- Day {day_label(int(item['day']))}: {item['file']}")
    return "\n".join(lines)


def exercise_block(selected: list[dict], grammar: dict) -> str:
    first_five = selected[:5]
    lines = [
        "### A. Verb Practice",
        "",
        "Fill the blank with the correct verb or write a new sentence:",
        "",
    ]
    for i, item in enumerate(first_five, start=1):
        lines.append(f"{i}. {item['example_de']} -> اكتب جملة جديدة باستخدام `{item['verb']}`.")

    lines.extend(
        [
            "",
            "### B. Grammar Practice",
            "",
            f"Topic: {grammar['focus']}",
            "",
            "1. اكتب 3 جمل قصيرة تطبق قاعدة اليوم.",
            "2. حول جملة واحدة الى سؤال.",
            "3. حول جملة واحدة الى نفي.",
            "4. اشرح القاعدة لنفسك في سطر عربي واحد.",
            "",
            "### C. Mini Writing",
            "",
            "اكتب 5 جمل عن نفسك مستخدما 3 افعال من افعال اليوم.",
        ]
    )
    return "\n".join(lines)


def render_day(day_number: int, study_date: str, progress: dict, verbs: list[dict], grammar_plan: list[dict], mapped: list[dict]) -> str:
    count = int(progress["daily_rules"]["verbs_per_day"])
    selected, source = select_verbs(verbs, mapped, progress, day_number, count)
    grammar = pick_grammar(grammar_plan, progress)
    bookmark = progress.get("course_progress", {})
    template = (ROOT / "templates/day-template.md").read_text(encoding="utf-8")
    fields = {
        "{{date}}": study_date,
        "{{day_number}}": day_label(day_number),
        "{{book_checkpoint}}": f"Printed page {bookmark.get('next_printed_page', '?')} / PDF viewer page {bookmark.get('next_pdf_page', '?')}",
        "{{verb_source}}": source,
        "{{review_due}}": review_due_text(day_number, progress),
        "{{verbs_table}}": verbs_table(selected),
        "{{grammar_focus}}": grammar["focus"],
        "{{grammar_goal}}": grammar["goal_ar"],
        "{{exercises}}": exercise_block(selected, grammar),
    }
    for key, value in fields.items():
        template = template.replace(key, value)
    if "{{" in template or "}}" in template:
        raise ValueError("Unresolved template placeholders")
    return template


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Safely generate one new German A1 worksheet.")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    parser.add_argument("--day", type=int, help="Must equal the next sequential day")
    parser.add_argument("--dry-run", action="store_true", help="Preview without saving")
    args = parser.parse_args()
    try:
        if date.fromisoformat(args.date).isoformat() != args.date:
            raise ValueError
    except ValueError:
        parser.error("Use YYYY-MM-DD for --date")
    progress = load_json(PROGRESS_PATH)
    previous = progress.get("generated_days", [])
    if any(not item.get("completed", False) for item in previous):
        parser.error("An incomplete day exists. Resume it instead of generating a new day.")
    next_day = max([int(progress.get("current_day", 0))] + [int(d["day"]) for d in previous]) + 1
    if args.day is not None and args.day != next_day:
        parser.error(f"Only day {next_day:03d} may be generated next.")
    name = f"{args.date}-day-{day_label(next_day)}.md"
    path = DAYS_DIR / name
    if path.exists():
        parser.error(f"Refusing to overwrite existing day: {path}")
    rendered = render_day(
        next_day, args.date, progress, load_json(VERBS_PATH),
        load_json(GRAMMAR_PATH), load_json(ROOT / "data/course_verbs.json"),
    )
    if args.dry_run:
        print(rendered)
        return 0
    DAYS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    progress.setdefault("generated_days", []).append({
        "day": next_day, "date": args.date, "file": f"days/{name}",
        "completed": False, "score": None,
    })
    progress["current_day"] = next_day
    progress["last_generated_date"] = args.date
    # Never rewrite CURRENT_STATE, advance a textbook page, or claim lessons mastered.
    save_json(PROGRESS_PATH, progress)
    print(f"Generated days/{name} (not studied or completed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

