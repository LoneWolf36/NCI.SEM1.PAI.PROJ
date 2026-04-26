# Presentation Script — Predicting 30-Day Readmission Risk in Dialysis Patients

> **How to use this script:** Read it naturally — don't rush. Pause where indicated. Make eye contact with the audience between sentences. The timings are approximate; focus on clarity over speed.

---

## SLIDE 1 — TITLE & INTRODUCTION
**Speaker:** Faizan · **Time:** ~60 seconds

Good morning, everyone.

My name is Faizan, and joining me today are Sakshi, Shashank, and Chetan. 

Our project tackles a critical challenge in nephrology care — **predicting which End-Stage Renal Disease (ESRD) dialysis patients are most likely to be readmitted to hospital within 30 days of discharge**. 

This is a high-stakes clinical problem. Nearly **one in five** kidney patients is readmitted to hospital within just 30 days of being discharged. These readmissions are costly for health systems, disruptive for patients, and — critically — often **preventable** if the right patients are flagged early enough.

To tackle this, we built a **full machine learning pipeline** using publicly available data from the U.S. Centers for Medicare & Medicaid Services, covering over **3 million discharge events**. Everything — from data ingestion to model explanation — runs in a single, reproducible workflow.

Let's start with **where the field stands today** and **why there's still a gap**.

---

## SLIDE 2 — STATE OF THE ART & PROBLEM STATEMENT
**Speaker:** Sakshi · **Time:** ~60 seconds

Machine learning has made meaningful progress in predicting hospital readmission across a range of conditions — heart failure, pneumonia, COPD. And more recently, it's been applied to kidney failure populations as well.

But the **ESRD dialysis population** is fundamentally different. These patients manage complex, recurring treatment regimens. They cycle between outpatient dialysis facilities, emergency departments, and acute-care hospitals. The data is fragmented, and the clinical trajectory is inherently non-linear.

*(Pause briefly.)*

Now, what does the existing dialysis ML literature actually focus on? Mostly **adequacy metrics** — how well a session clears toxins — or **complication forecasting**. Not readmission. And critically, many of those studies also suffer from **data leakage** — where the same patient's records appear in both training and testing, inflating results and giving a false sense of accuracy.

So our research question was clear: **can we use all four linked CMS ESRD tables to build a reliable, leakage-free readmission risk model?**

That gap in the literature — the absence of a rigorous, end-to-end, ESRD-specific readmission pipeline — is exactly what we set out to fill.

---

## SLIDE 3 — DATA & APPROACH
**Speaker:** Faizan · **Time:** ~60 seconds

Our project had **four clear objectives**, and I want to walk you through each one because they shaped every design decision we made.

**First** — build a **database-first pipeline** that integrates four public CMS ESRD tables: Patient Summary, Admit Treatment, Hospitalization, and Hemodialysis Adequacy. This gives us roughly **3.2 million patient-level records**, **7.7 million treatment episode records**, and over **32 million hemodialysis adequacy records**. No prior study had linked all of these in a single workflow. 

**Second** — focus on **temporal feature engineering**. Rather than relying on static demographics alone, we engineered features that capture a patient's *trajectory*: 30-day and 180-day hospitalisation counts, discharge gap days, and rolling dialysis adequacy trends. These time-aware signals are where the predictive power lives.

**Third** — run a **head-to-head model comparison** under **strict patient-level splitting**. Every hospital event for a given patient stays entirely in either the training set or the test set — never both. This prevents leakage and gives us honest, real-world performance estimates.

And **fourth** — go beyond accuracy. We used **SHAP** to explain what actually drives each individual prediction — not just *what* the model predicts, but *why*. 

*(Pause briefly.)*

That last step is critical. Because in a clinical setting, a risk score without an explanation is a risk score that doesn't get used.

---

## SLIDE 4 — MODELS & RESULTS
**Speaker:** Chetan & Faizan · **Time:** ~75 seconds

Let's look at how the models performed. 

We evaluated all three models on a substantial stratified test set: **100,000 unique patients**, covering exactly **388,375 hospitalisation events**. 

Now, when evaluating these models, we have to look beyond just raw accuracy. Our baseline model, **Logistic Regression**, achieved a moderate AUC of **0.6309** and an F1 score of **0.3469**. After threshold tuning, it successfully identified around 58% of actual readmissions — but it did so with poor precision, meaning it generated a high number of false positives. 

*(Pause — let that land.)*-------Let us go through the codebase 

**Pipeline** -- Explanation by Faiazn 

Hand over to Chetan 

**CatBoost** emerged as the strongest overall performer, delivering a better balance. It achieved an **AUC of 0.6453** and an F1 score of **0.3499**. While **LightGBM** followed closely with an AUC of **0.6242**, CatBoost consistently provided the best overall risk ranking. It gives us a better trade-off between sensitivity and precision, which is exactly what you need in a clinical triage scenario. 

Now, we want to be fully transparent. **AUC 0.6453 is moderate.** We're not claiming clinical-grade precision. What this model *is* useful for is **risk ranking and triage** — helping clinicians identify which patients deserve the closest follow-up — **not** making autonomous clinical decisions on its own.

Chetan - Let me go th next slide

---

## SLIDE 5 — FEATURE IMPORTANCE & SHAP
**Speaker:** Chetan & Faizan &  · **Time:** ~75 seconds

So the model works — but *what is it actually learning?* This is where **SHAP** comes in.

SHAP — **SHapley Additive exPlanations** — lets us look inside the CatBoost model and understand exactly **which features push each prediction toward or away from readmission**.

*(Direct the audience's attention to the slide.)*

-----Faizan
Four features dominate the global importance:
1. **Prior hospitalisation count** — the single strongest signal. Cumulative burden over a patient's history matters deeply.
2. **Recent hospitalisations in the last 180 days** — a patient who's been in and out of hospital recently is a patient in clinical distress.
3. **Length of stay** — longer hospitalisations signal greater illness complexity.
4. Discharge GAPS - SHORTER GAP = HIGHER RISK
Now, looking at the **SHAP beeswarm plot**, patients with high prior hospitalisation counts — shown as red dots pushed to the right — see a **strong increase** in their predicted readmission risk. Patients with low counts — the blue dots on the left — see their risk pushed *down*.

*(Pause briefly.)*

Here's an important nuance: **dialysis adequacy measures like Kt/V do contribute**, but they're **secondary** to utilisation history. This actually makes clinical sense. Within a 30-day readmission window, it's not how well the last dialysis session went — it's how *frequently* the patient has been hospitalised recently that carries the signal.

---

## SLIDE 6 — RECOMMENDATIONS & CONTRIBUTIONS
**Speaker:** Shashank · **Time:** ~75 seconds

Based on our findings, we want to close by clearly stating how this work could translate into practice, and what distinguishes it from prior work.

**First** — deploy this model as a **triage aid alongside clinicians**, not as an autonomous system. An AUC of 0.6453 is good enough to **rank patients by risk** — to separate the top quintile from the bottom — but it should act as a prioritisation layer, not a decision-maker. Care coordination teams should **intensify follow-up for patients with recent, repeated hospitalisations**, as that is where SHAP shows the largest concentration of risk.

**Second** — we built the **first end-to-end pipeline integrating all four CMS ESRD tables**. This isn't an incremental extension — it's a pipeline design no prior paper had attempted in a single, unified workflow.

**Third** — **patient-level splitting**. By ensuring that no patient's data appears in both training and testing, we prevent the leakage problem that **inflates results in much of the published literature**. Our performance numbers are honest.

**Fourth** — our readmission label is derived from **actual hospitalisation timing** — real admission and discharge dates in sequence — reflecting true clinical reality.

And **finally** — everything we've built sits on top of **publicly available CMS data**. Any researcher, any health system can download the same files and **reproduce and extend this pipeline** without requiring proprietary access.

*(Pause. Make eye contact with the audience.)*

Faizan will conclude with vote of Thanks 
---

> [!TIP]
> **Delivery reminders:**
> - Speak at roughly **130 words per minute** for clarity — slower is always better than faster at a podium.
> - When stating a number (1 in 5, AUC 0.6453, 388,000), **slow down slightly** and let the number land before continuing.
> - On Slide 4, emphasise the trade-off. Logistic Regression has okay recall but poor precision; CatBoost provides a better overall ranking (AUC) and balance. 
> - On Slide 5, **physically point** at the SHAP charts as you describe them — guide the audience's eyes.
> - If a question catches you off guard, it's perfectly fine to say: *"That's a great question — let me think about that for a moment."*
