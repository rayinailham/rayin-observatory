# Phase 0 style review

Status: **Phase 0 gate passed (owner, 2026-09-14)**. Palette, type, portrait and models are
final and recorded in PLAN §8. Chapter copy on this page stays DRAFT until its own approval
(Phase 2). This static mobile composition is not the Phase 1 application.

## Preview

From the project root:

```sh
python -m http.server 8766 --bind 0.0.0.0 --directory assets
```

- Local: <http://127.0.0.1:8766/style-lock/>
- Phone on the same Wi-Fi, current session: <http://192.168.1.21:8766/style-lock/>
- The IP can change. This server serves only `assets/`; stop with Ctrl+C when review ends.
- First screen: CrossCheck composition. The review link opens the dome, instrument,
  portrait, six palette swatches and three font samples below it.
- Desktop layout is intentionally not designed yet. The preview stays at phone width.

## Decisions approved at the Phase 0 gate

1. Dome form, night lighting and amber rails.
2. CrossCheck's three separate optics and metal finish.
3. Portrait likeness and navy scan treatment. AI edited the crop and background to remove
   the Amazon signage while retaining both shoulders; it is not an unretouched photograph.
4. PLAN §8 palette and Fraunces / Inter / JetBrains Mono.
5. The mobile composition. Chapter wording still remains DRAFT until its Phase 2 approval.

The owner passed this gate on 2026-09-14. The approved identity is recorded in PLAN §8.
Later phases require their own explicit owner gate.

## Sources and design choices

- Model forms: PLAN §5. Palette and fonts: PLAN §8.
- CrossCheck copy: `../portfolio/CAPABILITY_CROSSCHECK.md` relative to the project root,
  §1 (pitch) and §3.1 (browser / viewport / role matrix).
- “Three lenses. One target.” is a DRAFT visual metaphor for those three browser engines.
  No demo performance numbers or affiliation claims appear in this review.
- Typography sample “Evidence you can read.” is DRAFT, adapted from the dossier's
  evidence and reproducible issue reporting description.
- Design read: astronomy-inspired developer portfolio; native CSS, dark theme, sharp
  rectangular controls, no automatic motion. Dials: variance 6 / motion 1 / density 3.
- Fraunces and Inter explicitly follow the owner's plan. Both override the design skill's
  generic font defaults. Desktop, live instrument motion, routing and audio remain later phases.
- `fonts/` contains self-hosted regular weight 400 TTFs downloaded from Google Fonts.
  Each font's SIL OFL license is included, obtained from its `@fontsource` 5.3.0 package.
- `provenance.json` records photo prompts and font download sources.

## Blender

Both models were created through Blender MCP in the running GUI, rendered with Cycles,
OptiX GPU, 48 samples and denoising at 1000×1000 RGBA. Transparent backgrounds let the
page's ink background remain consistent.

- `dome.blend`: active `Dome / night review`, plus the untouched startup scene.
- `crosscheck.blend`: active `CrossCheck / three optics`, plus the dome and startup scenes.
- `crosscheck.blend1`: automatic backup before the camera / lens material refinement.
- `build_style.py`: editable procedural source. Refuses to overwrite the final `.blend`
  files; use a versioned destination for a rebuild. Execute through Blender MCP, not a
  headless replacement for the required GUI workflow.
- Render the selected review scene with `bpy.ops.render.render(write_still=True)`.
- This Phase 0 review uses PNGs. The Phase 1 dome export is documented in `web/README.md`
  from the project root; CrossCheck GLB still belongs to Phase 2.

## Verification

With the server running:

```sh
timeout 60 /home/rayin/Projects/Testing/crosscheck/.venv/bin/python assets/style-lock/verify_mobile.py
```

This borrows the existing Playwright environment without changing the CrossCheck project.
It writes `verification.json` and two screenshots in `assets/renders/`. The check covers
390×844 layout overflow, first-screen CTA, image/font loading, English/DRAFT markers,
browser errors, the review anchor and the disclosure. The screenshot was visually reviewed
at phone size before the full review page was inspected.

Final result: no horizontal overflow; CTA bottom at y=789 within the 844px screen;
all four image elements and three fonts loaded; review controls passed; no browser errors.
Font metadata confirms weight 400 for all three TTFs. PNG decoding passed. LAN URL returned
HTTP 200 from this machine; opening on a physical phone remains the owner's gate.

Blender inspection: 80 dome-scene objects, 100 CrossCheck-scene objects, exactly three named
optical lens objects, no linked libraries or missing image files. Full browser compatibility,
real-device performance and accessibility audits are not Phase 0 acceptance claims.
