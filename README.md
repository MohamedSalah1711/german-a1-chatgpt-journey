# German A1 ChatGPT Journey

ريبو منظم لمذاكرة الالماني A1 مع ChatGPT، وتسجيل التقدم اليومي على GitHub.

الفكرة بسيطة:

- كل يوم له ملف مستقل داخل `days/`.
- كل يوم يبدأ بمراجعة شاملة مبنية على الايام السابقة.
- كل يوم يحتوي على 10 افعال للحفظ مع امثلة.
- كل يوم يحتوي على نقطة قواعد A1 وتدريبات قصيرة.
- كل جلسة تنتهي بتحديث `progress.json` و `CURRENT_STATE.md` و `MISTAKE_PATTERNS.md`.
- كل تقدم يتسجل بـ Git commit، وبالتالي يظهر كتاريخ واضح على GitHub.

## Where we actually are (13 October 2026)

**Startbereit A1** study was already underway before this repo was created.

| Checkpoint | Page |
| --- | --- |
| Last studied page (printed in the book) | **80** |
| Same page in PDF viewer | **81** |
| Next printed page | **81** |
| Next PDF viewer page | **82** |
| Current lesson | **Lektion 3** |
| First GitHub tracking day | Day 001: ten clothing verbs practiced; **page 81 and the full day remain incomplete** |

Lessons 1–2 and the opening of Lesson 3 have been studied. This does **not** mean every word, grammar point or exercise is mastered or finished. Day 001 began as a placement/revision session, not a beginner reset. The guided review ended at **question 80/80 on 2026-10-13**; details and actual mistakes are under [reviews/](reviews/2026-10-13-a1-review-through-page-80.md). No overall A1 grade or new textbook-page completion is claimed.

A full course PDF is **currently committed to this public repository**. Check redistribution rights. Removing the file in a later commit does not remove it from Git history. Use `references/startbereit-a1-source-map.md` for the outline and `progress.json.course_progress` for the page bookmark.

## Start

اقرأ اولا:

1. `START_HERE.md`
2. `CURRENT_STATE.md`
3. `PROMPTS.md`
4. `references/startbereit-a1-source-map.md`

لإنشاء يوم جديد:

```powershell
python scripts/new_day.py
```

او بتاريخ محدد:

```powershell
python scripts/new_day.py --date 2026-10-14
```

بعد المذاكرة:

```powershell
git add .
git commit -m "Study German A1 day 001"
```

## GitHub

اسم الريبو المقترح:

```text
german-a1-chatgpt-journey
```

بعد إنشاء الريبو على GitHub تحت حساب:

```text
MohamedSalah1711
```

اربطه محليا:

```powershell
git remote add origin https://github.com/MohamedSalah1711/german-a1-chatgpt-journey.git
git branch -M main
git push -u origin main
```

## Repo Map

```text
.
├── days/                         # ملفات المذاكرة اليومية
├── reviews/                      # تقييمات المراجعة ونتائج الأقسام
├── data/                         # بيانات الافعال وخطة القواعد
├── references/                   # مراجع مختصرة مبنية على كورس A1
├── scripts/                      # ادوات إنشاء اليوم الجديد
├── templates/                    # قوالب اليوم والمراجعة
├── CURRENT_STATE.md              # الحالة الحالية
├── LEARNING_PROFILE.md           # هدفك وطريقة المذاكرة
├── MISTAKE_PATTERNS.md           # اخطاء متكررة
├── PROMPTS.md                    # برومبتات ChatGPT اليومية
└── progress.json                 # سجل تقدم منظم
```

## Daily Rule

لا تعتبر اليوم مكتمل غير لما تعمل الثلاث حاجات دي:

1. مراجعة بداية اليوم.
2. حفظ 10 افعال وكتابة جملة من عندك لكل فعل.
3. حل تدريبات القواعد وتسجيل الاخطاء.


## Safe lesson generation

- **Resume Day 001 first.** The generator blocks new days while an earlier day is incomplete.
- Preview: `python scripts/new_day.py --dry-run`.
- After a previous day is genuinely completed: `python scripts/new_day.py`.
- Run tests: `python -m unittest discover -s tests -v`.
- The generator does **not** rewrite `CURRENT_STATE.md`, invent results, mark practice as mastered, or advance the textbook bookmark.
- Page-linked verbs live in `data/course_verbs.json`; otherwise verbs are labelled **general A1 practice** (not claimed to be from the page).
- The book PDF and local machine details should not be republished without checking permissions/privacy.
