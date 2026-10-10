# Ideal Pathway Rules

## 1. Stages

Registration -> Triage -> Tests -> Consultation -> Treatment -> Discharge

## 2. Required steps

- Registration: Bina registration ke patient ka record aur billing nahi ban sakta
- Triage: Priority aur severity pata karna safety ke liye zaroori hai (emergency mein skip ho sakta hai)
- Consultation: Diagnosis aur treatment ka decision doctor hi leta hai
- Discharge: Visit officially close hone ke liye discharge zaroori hai

## 3. Optional steps

- Tests: Sirf tab hote hain jab doctor ne manga ho
- Treatment: Kuch patients ko sirf advice milti hai, procedure ya medicine nahi

## 4. Order rules

- Registration sabse pehle, Discharge sabse last
- Triage ke baad Tests (X-Ray), phir Consultation (imaging-first pathway)
- Backward moves allowed nahi (X-Ray -> Triage rework loop deviation hai)
- Required step skip allowed nahi (sirf emergency mein Triage skip)

## 5. Exceptions

- Emergency patient Triage skip kare (Registration -> Consultation) (Clinical)
- Repeat tests (Clinical)
- Multiple consultations (Clinical)
- X-Ray ke baad dobara Triage, phir X-Ray (rework loop) (Clinical rework)
- Discharge ke baad koi activity (Data error)
- Registration pehla step nahi (Data error)
- Same timestamp ya reversed order (Data error)

Machine-readable version: ideal_pathway.json
