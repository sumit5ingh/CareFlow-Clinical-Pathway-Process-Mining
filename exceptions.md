# Exceptions and Edge Cases

| Situation | Type | Note |
|---|---|---|
| Emergency patient Triage skip kare (Registration -> Consultation) | Clinical | Valid, direct doctor ke paas jaata hai |
| Repeat tests | Clinical | Valid, result unclear ho ya follow-up test ho |
| Multiple consultations | Clinical | Valid, specialist referral ya follow-up |
| X-Ray ke baad dobara Triage, phir X-Ray (rework loop) | Clinical rework | Clinically possible (re-assessment ya repeat imaging) par ideal path nahi, conformance mein deviation ginte hain |
| Discharge ke baad koi activity | Data error | Visit close ho chuka hai, timestamp ya logging galti |
| Registration pehla step nahi | Data error | Missing ya galat sorted event |
| Same timestamp ya reversed order | Data error | Sorting ya logging issue |

## Team review feedback

- (Yahan apne teammates ke actual suggestions likho)
