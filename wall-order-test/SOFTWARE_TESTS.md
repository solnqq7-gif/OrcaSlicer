# Software tests done before the first test build

[Back to the overview](README.md)

These checks were run on Windows with the feature commit on top of the official `v2.5.0-alpha` tag (Windows Release build), and an unmodified `v2.5.0-alpha` built from the same dependencies as the reference. They show that the slicer does what the settings say. **They do not show that prints get better.** That is what the public test is for.

The models are the six coupons in [`models/`](models). The settings are a Creality K1 Max with a 0.4 mm nozzle, 0.16 mm layers, PETG and 4 walls, unless a test changes them.

| Check | Result |
| --- | --- |
| Unit tests of the whole project (Catch2) | 2319 of 2320 passed. The one skipped is an upstream plugin test that needs symlink rights on Windows. All 13 cases of this feature passed. |
| Feature off = official v2.5.0-alpha, every G-code command | identical on 6 models × 2 wall generators, and in every combination below |
| 29 combinations with common settings × 3 models × 2 wall generators: Outer/Inner, global Inner/Outer, overhang reversal, alternate extra wall, scarf seams, fuzzy skin, official precise wall, one wall on first/top layers, extra perimeters on overhangs, infill first, unsupported wall last, brim, 1/2/6 walls, 0.08/0.28 mm layers, tree support, raft, arc fitting, wall direction, thin walls, no elephant foot compensation, spiral vase, two objects, print by object | 174 of 174 cases, 906 slices. Feature on: same layers, first layer unchanged, every wall segment the same, only the order changes. Where the feature cannot act (one wall, spiral vase, global Inner/Outer), the output is identical to feature off. |
| Random combinations: nozzle 0.2–0.8 mm, layer height, 2–6 walls, wall order, generator, seam position, elephant foot compensation, all seven options, all six models | 230 of 230 cases, no crash. Each wall loop is the same path with the same extrusion; only the start point moves with *Nearest*/*Back* seams. |
| Fuzzy skin (random in the official build too) | Over 8 slices each, the extrusion totals with the feature off overlap the official range. With the feature on, switched layers match what the official build does with global Inner/Outer. |
| Project files | All seven values survive save and reload. One object on and one off on the same plate each slice as expected. A height range modifier switches only inside its range. The official v2.5.0-alpha opens projects saved by the test build without error, ignores the extra settings and slices in the original order. |
| Settings panel (English UI) | The options appear, hide and grey out as described in the README, in the global process and per object. A plate sliced in the GUI gives the same G-code as the command line with the same settings. |
| Windows portable package | Started without arguments, it keeps all settings in `data_dir`; the installed OrcaSlicer's settings file is unchanged. |
| G-code checker | Its per-layer estimate matched the real wall order on all 913 layers of 9 test files (Inner/Outer/Inner and Outer/Inner, Arachne and Classic, arcs, two objects, two walls). |

Not covered yet: macOS and Linux builds (the release workflow builds them; they have not been run by the author), printers other than the K1 Max profile in software tests, and physical prints.
