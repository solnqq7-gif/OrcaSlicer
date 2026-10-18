# Conditional wall order – public test build (unofficial)

[繁體中文](README.zh-TW.md)

> **This is not an official OrcaSlicer release.** It is a test build of OrcaSlicer **v2.5.0-alpha** with one added feature, made by an OrcaSlicer user to collect real prints before proposing the feature upstream. Please do not report problems with this build to the OrcaSlicer project. Report them here.

## What it does

With **Inner/Outer/Inner** or **Outer/Inner** wall order, the external wall of an overhang (a downward chamfer, a rounded bottom edge) is laid out before an internal wall exists next to it, so it can sag. **Inner/Outer** fixes that, but changes the surface of the whole object.

This build switches **only the layers that need it** to Inner/Outer and keeps your wall order everywhere else:

- layers where an island overhangs the layer below by more than a set angle
- layers up to a set height from the object bottom
- layers shrunk by the elephant foot compensation

The decision is made per island, per layer. The first object layer never switches. With the main checkbox off, the output is the same as the official v2.5.0-alpha. That was checked line by line, and you can check it yourself (see [Check your G-code](#check-your-g-code)). The software tests done before this release are listed in [SOFTWARE_TESTS.md](SOFTWARE_TESTS.md).

**What we want to find out:** does this actually print better overhangs on your printer, and how visible is the place where the wall order changes? Results that turn out worse are just as useful as better ones.

## Download and install (kept separate from your normal OrcaSlicer)

Downloads: the **Releases** page of this repository. Each release lists the exact source commit and SHA-256 checksums.

| System | File | How to keep it separate |
| --- | --- | --- |
| Windows | `OrcaWallOrderTest-..._portable.zip` | Unzip it and start `OrcaWallOrderTest\orca-slicer.exe`. The empty `data_dir` folder next to it keeps all settings there, so your installed OrcaSlicer is not touched. If Windows says a path is too long, unzip to a short folder such as `C:\OrcaWallOrderTest`. |
| macOS | `.dmg` | Copy `OrcaSlicer.app` into a **new folder** and create an empty folder named `data_dir` next to the app. The build is not signed: the first time, right-click the app → Open (or run `xattr -cr OrcaSlicer.app`). |
| Linux | `.AppImage` | Start it with a separate settings folder: `./OrcaSlicer*.AppImage --datadir ~/orca-wallorder-test` |

To use your own printer and filament profiles, export them from your normal OrcaSlicer (**File → Export → Export Preset Bundle**) and import the bundle into the test build. We suggest staying logged out of cloud accounts in the test build, or at least turning off preset sync, so the extra settings do not travel into your normal setup. (The official build simply ignores them, but it avoids confusion.)

On a fresh settings folder, Windows may ask to install the **Bambu Network Plug-in**. You only need it for Bambu printers' network features; "Skip for now" is fine for testing.

## The settings

**Process → Quality → Walls and surfaces**, directly under **Walls printing order**. They are advanced settings, so turn on the **Advanced** switch in the process panel. They can also be set per object or per height range modifier, like other quality settings.

| Setting | Default | What it does |
| --- | --- | --- |
| **Change walls printing order on overhangs** | off | Main switch. Shows the options below. Hidden when the wall order is already Inner/Outer, in spiral vase mode, or without walls. |
| **Inner/Outer on overhangs** | 0° | Switch an island when it overhangs the layer below by more than this angle, measured from vertical (0° = vertical, 45° = typical chamfer). Set it a little below the chamfers you want to catch, e.g. **40°** for 45° chamfers. 0 = off. |
| **Maximum overhang angle for Inner/Outer** | 0° | Islands whose steepest overhang is above this angle keep the original order, for prints where very steep overhangs do better that way. Only used when larger than the angle above (greyed out while that angle is 0). 0 = no limit. |
| **Inner/Outer up to height** | 0 mm | Switch every layer from the object bottom up to this height (first layer excluded). For rounded or chamfered bottom edges. 0 = off. |
| **Inner/Outer on elephant foot compensation layers** | off | Switch the layers shrunk by elephant foot compensation (first layer excluded). Only available when the compensation is above 0, covers more than one layer, and no raft is used. |
| **Precise wall on switched layers** | off | Apply the precise wall to switched islands only (removes the overlap between the internal and external wall so the external wall is not pushed outwards). Independent of the official **Precise wall** option. |
| **Size compensation on switched layers** | 0 mm | Shrink switched islands to make up for the external wall being pushed out by the internal wall printed first. **The value is the total of both sides**: 0.2 mm moves each side 0.1 mm (unlike elephant foot compensation, which is per side). Holes grow by the same amount. |

## How to test (about 1–2 hours of printing)

Full instructions and the scoring sheet: **[TESTING.md](TESTING.md)**. In short:

1. Pick a model: one of the six coupons in [`models/`](models) (45°, 60°, 75° chamfers, each with and without a 3 mm base), or one of your own models that shows the sagging problem.
2. Print it **three times**, changing nothing but the wall settings:
   - **A** – your usual wall order (Inner/Outer/Inner or Outer/Inner), feature off
   - **B** – Walls printing order = **Inner/Outer** for the whole object, feature off
   - **C** – your usual wall order, feature **on** (for example Inner/Outer on overhangs = 40°)
3. Same printer, filament, speeds, plate position and orientation for all three. One object per plate.
4. Photograph all three together, in the same light: the overhang from below, and the side where the order switches.
5. Open a **Print report** issue and attach the photos and a zip of the three G-code files (or the project 3MF).

## Check your G-code

[`tools/wallorder-check.html`](tools/wallorder-check.html) runs offline in your browser; download the file and open it. Nothing is uploaded.

- Drop a G-code to see which build and settings produced it, and which layers were printed in Inner/Outer order.
- Drop **two** G-codes to compare them. With the main checkbox off, the test build and the official v2.5.0-alpha should produce identical moves. If you find a difference, please report it.

## Known behaviour (not bugs)

These were found in software testing; most also happen in the official build whenever the wall order is changed.

- **The seam start can move** on switched layers and the layers next to them. Seams set to *Nearest* or *Back* follow the nozzle, and *Aligned* seams are aligned across layers. The loops and extrusion amounts are the same; only the start point moves.
- **Fuzzy skin is random.** Official OrcaSlicer also gives a different result every time you slice. With Inner/Outer order, the official build makes the fuzzy external wall longer and the internal walls shorter; switched layers show the same.
- **The whole island switches**, not individual wall segments.
- **Twisted polyholes** can be detected as overhangs.
- **Height range modifiers** whose settings differ from the object split it into regions. The official build then changes that object's walls by output rounding (0.001 mm), with or without this feature.
- **No effect** with one wall, in spiral vase mode, or when the wall order is already Inner/Outer.
- The change of order can leave a **visible line** where switching starts or stops. That is one of the things this test is meant to measure.

## Problems

Crashes, slicing errors, or settings that do not behave as described: open a **Problem report** issue. Please check whether the problem also happens in the official v2.5.0-alpha with the main checkbox off. If it does, it is not caused by this feature.

## How results will be used

All reports, including bad results, are summarised publicly in this repository. If the evidence supports it, the feature will be proposed to OrcaSlicer as a pull request that links to these reports. See [EVIDENCE.md](EVIDENCE.md) for what counts as enough evidence. Nothing here implies that the OrcaSlicer team endorses or will accept the feature.

## Source and licence

OrcaSlicer is licensed under the GNU AGPL v3. The source of every test build is the commit named in its release, in this repository. The feature is a single commit on top of the official `v2.5.0-alpha` tag, and the test-programme files are a separate commit.
