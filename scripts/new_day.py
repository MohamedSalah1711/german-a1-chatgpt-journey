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


def select_verbs(verbs: list[dict], day_number: int, count: int) -> list[dict]:
    start = ((day_number - 1) * count) % len(verbs)
    selected = []
    for offset in range(count):
        selected.append(verbs[(start + offset) % len(verbs)])
    return selected


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
    due = [item for item in generated if day_number - int(item["day"]) in intervals]

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


def render_day(day_number: int, study_date: str, progress: dict, verbs: list[dict], grammar_plan: list[dict]) -> str:
    selected = select_verbs(verbs, day_number, progress["daily_rules"]["verbs_per_day"])
    grammar = pick_grammar(grammar_plan, progress)
    review_due = review_due_text(day_number, progress)
    checkpoint = progress.get('course_progress', {})
    next_printed = checkpoint.get('next_printed_page', 'unknown')
    next_pdf = checkpoint.get('next_pdf_page', 'unknown')

    return f"""# {study_date} - Day {day_label(day_number)}

Status: not completed

First tracking day does not mean the learner is new to German.
Textbook bookmark: next **printed page {next_printed} / PDF viewer page {next_pdf}**. This is not a mastery score.

## 1. Morning Review

Review due:

{review_due}

Checklist:

- [ ] Old verbs reviewed
- [ ] Old grammar reviewed
- [ ] Mistake patterns reviewed
- [ ] One short spoken answer completed

## 2. Today's 10 Verbs

{verbs_table(selected)}

Task: write one personal sentence for every verb.

## 3. Grammar Focus

Source unit: {grammar['unit']} - starts around PDF page {grammar['source_page']}

Focus: {grammar['focus']}

Goal: {grammar['goal_ar']}

Practice ideas:

{chr(10).join(f"- {item}" for item in grammar["practice"])}

## 4. Exercises

{exercise_block(selected, grammar)}

## 5. Speaking

Answer in German:

1. Wie heißt du?
2. Wo wohnst du?
3. Was lernst du heute?
4. Was machst du morgen?
5. Welche Verben sind heute schwierig?

## 6. End Of Day Log

Score: __ / 10

What I learned:

-

Mistakes:

-

Review tomorrow:

-
"""


def update_current_state(day_number: int, study_date: str, day_file: Path, grammar: dict) -> None:
    CURRENT_STATE_PATH.write_text(
        f"""# Current State

Date: {study_date}

Current level: A1 beginner

Current day: {day_label(day_number)}

Status: Day {day_label(day_number)} generated, not completed yet.

## Today

- File: {day_file.as_posix()}
- Grammar focus: {grammar['focus']}
- Source unit: {grammar['unit']} around PDF page {grammar['source_page']}
- Daily target: 10 verbs, one grammar point, exercises, and end-of-day log.

## Next Session Should Start With

1. Review this generated day.
2. Review old mistake patterns.
3. Ask the learner short questions before explaining new material.
""",
        encoding="utf-8",
    )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Generate a new daily German A1 study file.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Study date in YYYY-MM-DD format.")
    parser.add_argument("--day", type=int, help="Specific day number to generate.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing generated day file.")
    parser.add_argument("--dry-run", action="store_true", help="Print the generated lesson without writing files.")
    args = parser.parse_args()

    progress = load_json(PROGRESS_PATH)
    verbs = load_json(VERBS_PATH)
    grammar_plan = load_json(GRAMMAR_PATH)

    last_day = int(progress.get("current_day", 0))
    if args.day is None and any(
        int(item["day"]) == last_day and not item.get("completed", False)
        for item in progress.get("generated_days", [])
    ):
        raise SystemExit(
            f"Day {day_label(last_day)} is still not completed. "
            "Finish/review it before generating the next day."
        )
    day_number = args.day or last_day + 1
    day_file = DAYS_DIR / f"{args.date}-day-{day_label(day_number)}.md"

    if any(item.get("file") == day_file.relative_to(ROOT).as_posix() and item.get("completed") for item in progress.get("generated_days", [])):
        raise SystemExit(f"Refusing to overwrite a completed day: {day_file}")
    if day_file.exists() and not args.force:
        raise SystemExit(f"Day file already exists: {day_file}")

    rendered = render_day(day_number, args.date, progress, verbs, grammar_plan)

    if args.dry_run:
        print(rendered)
        return 0

    day_file.write_text(rendered, encoding="utf-8")

    rel_file = day_file.relative_to(ROOT).as_posix()
    generated_days = progress.setdefault("generated_days", [])
    generated_days = [item for item in generated_days if int(item["day"]) != day_number]
    generated_days.append(
        {
            "day": day_number,
            "date": args.date,
            "file": rel_file,
            "completed": False,
            "score": None,
        }
    )
    progress["generated_days"] = sorted(generated_days, key=lambda item: int(item["day"]))
    progress["current_day"] = day_number
    progress["last_generated_date"] = args.date
    progress["skills"]["verbs"]["introduced"] = max(
        int(progress["skills"]["verbs"].get("introduced", 0)),
        day_number * int(progress["daily_rules"]["verbs_per_day"]),
    )

    grammar = pick_grammar(grammar_plan, progress)
    topics = progress["skills"]["grammar"].setdefault("introduced_topics", [])
    if grammar["focus"] not in topics:
        topics.append(grammar["focus"])

    save_json(PROGRESS_PATH, progress)
    update_current_state(day_number, args.date, day_file.relative_to(ROOT), grammar)
    # Preserve the learner's actual textbook progress in CURRENT_STATE.
    with CURRENT_STATE_PATH.open("a", encoding="utf-8") as state_file:
        course = progress.get("course_progress", {})
        state_file.write(
            f"\n## Textbook Bookmark (learner-reported)\n\n"
            f"- Last studied printed page: {course.get('last_studied_printed_page', 'unknown')}\n"
            f"- Next printed page: {course.get('next_printed_page', 'unknown')}\n"
            f"- Next PDF viewer page: {course.get('next_pdf_page', 'unknown')}\n"
            f"- Studied does not mean mastered. Never auto-advance the page.\n"
        )

    print(f"Generated {rel_file}")
    print("Next: study the file, update the end-of-day log, then commit your progress.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

