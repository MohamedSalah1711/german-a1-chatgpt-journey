# German A1 ChatGPT Journey

ريبو منظم لمذاكرة الالماني A1 مع ChatGPT، وتسجيل التقدم اليومي على GitHub.

الفكرة بسيطة:

- كل يوم له ملف مستقل داخل `days/`.
- كل يوم يبدأ بمراجعة شاملة مبنية على الايام السابقة.
- كل يوم يحتوي على 10 افعال للحفظ مع امثلة.
- كل يوم يحتوي على نقطة قواعد A1 وتدريبات قصيرة.
- كل جلسة تنتهي بتحديث `progress.json` و `CURRENT_STATE.md` و `MISTAKE_PATTERNS.md`.
- كل تقدم يتسجل بـ Git commit، وبالتالي يظهر كتاريخ واضح على GitHub.

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

