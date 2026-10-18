# How reports are counted

[繁體中文](EVIDENCE.zh-TW.md) · [Back to the overview](README.md)

These rules are written **before** results come in, so that the summary cannot be tuned to a wanted answer. If they change, the change and its reason are recorded at the bottom of this file.

## A report counts when

1. It has A, B and C prints of the same model on the same printer, with the protocol in [TESTING.md](TESTING.md) followed (or deviations described).
2. The G-code (or sliced 3MF) of all three is attached, and the checker confirms:
   - A and C come from the test build (or A/B from the official v2.5.0-alpha), with the same settings except the wall options;
   - C has switched layers on the overhang.
3. Photos show all three parts together.

Reports that do not meet this are still read, kept, and listed separately as *incomplete*, never dropped silently.

## What is summarised

For every counted report: printer type and firmware family, nozzle, material, layer height, wall generator, model, the feature settings, and the five scores from TESTING.md (underside C vs A, underside C vs B, switch line visibility, vertical walls, kept print), plus whether the ranking was blind.

The summary shows **every** result, better, same and worse, and counts by tester, not by part, so one person printing ten sets cannot outweigh ten people.

Software checks reported by testers ("feature off = official", crashes, wrong switching) are listed separately.

## When the feature goes to OrcaSlicer (proposal)

The feature is proposed upstream when **all** of these hold:

- **≥ 8 independent testers** with counted reports;
- **≥ 3 printer families** (for example bed slinger, CoreXY, Bambu Lab, Klipper, Marlin) and **≥ 2 materials**;
- for the chamfer underside, **C better than A in a clear majority of testers** and C rarely worse;
- the switch line on C judged *none* or *faint* by most testers, or the reports show which settings avoid it;
- **no open crash or wrong-output report** caused by the feature;
- "feature off = official v2.5.0-alpha" confirmed by **≥ 3 testers on at least 2 operating systems**.

If the evidence shows that the feature does not help, or only in narrow cases, that result is published as well, and the proposal is changed or dropped accordingly.

The upstream pull request would contain only the feature commit (with the local migration code for the author's own early prototypes removed) and link to this summary.

## Changes to these rules

*(none yet)*
