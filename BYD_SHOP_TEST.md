# BYD Atto 3: shop install and test guide

Install link (one link for everyone):

```
https://installer.comma.ai/bring-nirachornkul/byd-atto3-comma4-v2
```

Default after install: **nudge mode** (driver nudges the wheel to confirm a lane change), same as the original `byd-atto3-comma4` link.
Nudgeless is an on-device toggle: **Settings > Toggles > nudgeless lane change**.

Fallback links (unchanged, known working):

| Situation | Link |
|---|---|
| Anything on this branch misbehaves | `https://installer.comma.ai/bring-nirachornkul/byd-atto3-comma4` |

Rule: if a test below fails, **do not troubleshoot on the road**. Use the fallback in step 5.

---

## 1. Install (parked, car in P)

1. Install the link above. Let it finish and reboot.
2. While it boots, the loading screen shows the brand logo (or the stock comma logo if no logo file was added).

**Pass:** device reaches the home screen with no red alert.

## 2. Parked checks (car on, in P)

| # | Check | Pass |
|---|---|---|
| 2.1 | Home screen | No "Dashcam Mode", no "Process Not Running", no "openpilot Unavailable" |
| 2.2 | Settings > Toggles | "nudgeless lane change" is listed and **OFF** |
| 2.3 | Turn the steering wheel by hand | Device does not show an error |
| 2.4 | Press brake, then gas | Device does not show an error |

Any fail: go to step 5.

## 3. Blind-spot check (nudge mode, toggle OFF)

Why: nudgeless trusts the car's blind-spot sensor. This test proves openpilot sees it. In nudge mode the car never changes lanes on its own, so this test is safe.

Road: multi-lane road, above 20 mph (32 km/h), openpilot engaged, helper car or normal traffic.

| # | Do | Pass |
|---|---|---|
| 3.1 | Car in your left blind spot (car's own left mirror light ON). Signal left. Do NOT touch the wheel. | Screen shows **"Car Detected in Blindspot"** |
| 3.2 | Same on the right side | Same alert |
| 3.3 | Car **pacing you at the same speed** in the blind spot (mirror light ON). Signal. | Same alert. **This is the most important check.** |
| 3.4 | Lane empty. Signal. Do NOT touch the wheel. | Screen shows "Steer Left/Right to Start Lane Change Once Safe" and the car does **not** move over |
| 3.5 | Lane empty. Signal, then nudge the wheel toward the lane. | Car changes lanes |

Rule: every time the car's mirror light is ON, the screen must show "Car Detected in Blindspot".
If it ever does not (especially 3.3): **leave nudgeless OFF for that car.** Nudge mode stays safe. Report it to Bring.

## 4. Nudgeless check (toggle ON)

Only if all of step 3 passed. Settings > Toggles > nudgeless lane change: **ON** (change it while parked).
Road: empty lanes, above 20 mph, driver hands on wheel and ready.

| # | Do | Pass |
|---|---|---|
| 4.1 | Lane empty. Tap signal once. Hands resting, no nudge. | Car changes lanes by itself within about 1 s |
| 4.2 | Lane empty. Hold the stalk on and keep holding. | **Exactly one** lane change, then the car stays in lane and shows "Steer ... Once Safe" |
| 4.3 | Signal. Grab the wheel to stop the change. Let go, signal still on. | Car does **not** start the lane change again |
| 4.4 | Car in blind spot (mirror light ON). Signal. | Car does **not** move. After the car passes, it changes about 1 s later |
| 4.5 | Car in blind spot. Signal. Press the brake. Car passes. | Car does **not** change lanes (brake cancelled it) |

Any fail: turn the toggle **OFF** (nudge mode). If the problem is anything other than lane change, go to step 5.

## 5. Fallback to the original software

1. Park, car in P.
2. Device: Settings > Software > **uninstall openpilot**. Confirm. Device reboots to setup.
3. Choose custom software and enter:
   `https://installer.comma.ai/bring-nirachornkul/byd-atto3-comma4`
4. Let it install and reboot. This is the original, known-working nudge version.

## 6. Report back to Bring

Send: car VIN last 6 digits, date, which link is installed, toggle ON/OFF, and the # of any failed check.
If possible, note the time of the failure so the drive log can be found in comma connect.

---

## Adding the BYD logo (Bring, one time)

The loading screen shows `openpilot/selfdrive/assets/images/spinner_brand.png` if the file exists.

- Square PNG, transparent background, at least 400x400 px. It is scaled to fit inside the spinning ring.
- The file is excluded from Git LFS in `.gitattributes`, so a normal `git add` / `git push` works.
- No file = stock comma logo. Nothing breaks.

```
cp /path/to/your-byd-logo.png openpilot/selfdrive/assets/images/spinner_brand.png
git add openpilot/selfdrive/assets/images/spinner_brand.png
git commit -m "Add brand logo"
git push origin byd-atto3-comma4-v2
```

Check before pushing: `git check-attr filter openpilot/selfdrive/assets/images/spinner_brand.png` must print `filter: unset`.
