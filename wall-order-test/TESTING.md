# Test protocol

[繁體中文](TESTING.zh-TW.md) · [Back to the overview](README.md)

The aim is a fair A/B/C comparison: three prints that differ **only** in the wall settings. One careful set is worth more than many quick ones.

## 1. Choose a model

**Coupons** in [`models/`](models). All are 15 mm blocks with downward chamfers on all four sides, a slot through Y (bridge at the top of the slot) and a 5 mm hole through X.

| File | Chamfer | Width | Notes |
| --- | --- | --- | --- |
| `453MF.3mf` | 45° | 25 mm | Chamfer starts at the bed, like a chamfered bottom edge on a normal part. |
| `603MF.3mf` | 60° | 25 mm | Same, steeper. |
| `753MF.3mf` | 75° | 35 mm | Same, very steep. |
| `*_底座3mm.3mf` | same | same | Same block on a 3 mm vertical base, so the chamfer is clear of the first layer and the elephant foot compensation. **Start with one of these**. `603MF_底座3mm.3mf` is a good first test. |

**Your own model** is welcome too, especially one that shows the problem this feature is meant to fix. Attach it, or describe it if you cannot share it.

## 2. Slice three versions

Use your usual printer, filament and process profile. Change **only** the following, in the global process settings (not per object):

| Print | Walls printing order | Change walls printing order on overhangs | Other options of the feature |
| --- | --- | --- | --- |
| **A** | your usual (Inner/Outer/Inner or Outer/Inner) | off | – |
| **B** | Inner/Outer | off | – |
| **C** | same as A | **on** | Inner/Outer on overhangs = **40°**; everything else at its default |

You are welcome to try other values in additional prints (D, E…). Record exactly what you changed.

Do not change anything else between A, B and C: speeds, cooling, flow, temperatures, seam, plate position, orientation. Keep **one object per plate**, in the same place each time. Layer time and fan exposure change with the number of objects, so several coupons on one plate are not a fair comparison.

Save each sliced plate (**Export G-code**, or **Export plate sliced file** for a 3MF with the G-code inside). Name them `A.gcode`, `B.gcode`, `C.gcode`.

Before printing, drop `C.gcode` into [`tools/wallorder-check.html`](tools/wallorder-check.html) and confirm that it says *test build* and lists switched layers on the chamfer. If no layer switched, the settings did not reach the slicer, and printing C would not test anything.

## 3. Print

- Print A, B and C one after another, from the same spool, with the printer in the same state (same enclosure door position, same room).
- Write down anything unusual: a clog, a layer shift, a draft, a cold start.
- Optional but valuable: print the set twice, in the order A B C and then C B A.

## 4. Photograph

Label the parts on the bed side with a marker (A/B/C), or keep them on labelled paper.

Take these photos, with **all three parts in the same picture** and the same light:

1. **Underside of the chamfer**, looking up at it at a low angle, with a raking light from the side. This shows sagging and curling.
2. **Side view across the switch**, the vertical wall just above and below where the chamfer starts and ends. This shows any line or colour change where the order switches.
3. A close-up of anything that looks different.

Phone photos are fine. Do not edit them apart from cropping.

## 5. Score

Compare **C with A**, and **C with B**:

| Question | Answer |
| --- | --- |
| Chamfer underside: C compared with A | much better / better / same / worse / much worse |
| Chamfer underside: C compared with B | much better / better / same / worse / much worse |
| Visible line where the order switches, on C | none / faint (only in raking light) / visible / strong |
| Vertical walls away from the chamfer: C compared with A | same / different (describe) |
| Which print would you keep? | A / B / C / no difference |

If someone else can rank the three parts **without knowing which is which**, say so in the report. Blind rankings are the strongest evidence.

Optional measurements: caliper width across the chamfer zone and across the vertical part, for A, B and C.

## 6. Report

Open a **Print report** issue (Issues → New issue → Print report) and attach:

- the photos
- `A.gcode`, `B.gcode`, `C.gcode` (or the sliced 3MF files) **in one zip**; GitHub does not accept `.gcode` or `.3mf` directly
- your own model, if you used one and can share it

G-code files contain your printer and filament settings, including your start/end G-code. Look through them if those contain anything you do not want to share.
