# Upgrade the five observatory instruments

Work in `/home/rayin/Projects/Testing/Rayin Observatory`.

Upgrade all five 3D instruments to match the detail, material quality, and mechanical credibility of the recently rebuilt observatory. The instruments currently look too simple beside it. Implement the upgrades, rather than only proposing concepts.

## Read and inspect first

Follow applicable project instructions. Inspect the running site at desktop and mobile sizes, including each instrument's homepage chapter and case-file inspection view. Read:

- `web/components/observatory-model.ts` — visual and construction benchmark.
- `web/components/observatory-scene.tsx` — framing, camera, model loading, disposal, and projected hotspot anchors.
- `web/components/instrument-motion.ts` — existing moving parts, material names, signal states, and animation rigs.
- `web/lib/cases.ts` — component names, node/part anchors, and what each instrument represents.
- `web/lib/instruments.ts` — instrument identities and approved copy.
- Relevant existing Blender source/export scripts under `assets/blender/`, if modifying GLBs.

Capture a before image for each instrument. Trace actual geometry, named nodes, materials, and animation consumers before changing them. Treat source files as authoritative if documentation differs.

## Visual direction

Build sophisticated scientific instruments with believable construction. Match the observatory's silver metal, dark navy structure, restrained brass, warm amber lights, and optical glass. Give each instrument a strong silhouette, readable major assemblies, secondary mechanisms, and selective fine detail.

Use bevelled edges, layered housings, inset panels, bearing collars, brackets, fasteners, cable routing, calibrated scales, connectors, and ventilation where they serve a physical purpose. Vary roughness and reflectivity so surfaces remain readable in the actual scene lighting. Avoid flat plastic surfaces, featureless cylinders, excessive glow, decorative clutter, and details too small to survive the website's framing.

Preserve each instrument's identity:

1. **CrossCheck — three-channel telescope:** detailed optical barrels, recessed lenses, aperture rings, focusing assemblies, alignment hardware, braced mount, and service cabling. Keep the three channels distinct and their existing inspection anchors meaningful.
2. **SurgeLine — radio dish array:** shaped dishes, rear support ribs, feed horns on support arms, azimuth/elevation bearings, motors, cable paths, and a functional central base. Preserve independent dish movement and the queue/worker/proof signal story.
3. **DriftWatch — recording instrument:** a precision chassis, articulated needle, real paper path, rollers, bearings, tension guides, calibration marks, and an inspection window. Keep the live trace legible and the collection/change/alarm parts easy to identify.
4. **DueWatch — mechanical orrery:** layered orbital tracks, gears, shafts, balanced support arms, engraved timing marks, and distinct planetary finishes. Preserve the three relevant moving planets, deadline states, and their tracking hotspots.
5. **BrandWall — optical bench:** a machined rail, adjustable light source and collimator, a prism in a credible mount, spectrum receiver, alignment screws, and connected detector housing. Preserve the wave/particle interaction and readable optical path.

These details are design directions; adapt them to the inspected models and their existing behavior. Do not turn every instrument into the same assembly with different colors.

## Motion and integration

Make mechanisms move around believable pivots: focus collars turn, dish drives track, rollers feed, orbital gears rotate, optical mounts adjust. Use restrained idle motion and preserve the existing signal animations. Scroll forward and backward must remain smooth and reversible.

Preserve the rebuilt observatory, planetary scroll choreography, navigation, approved text, project readings, routes, audio controls, and case-file interactions. Keep the singularity/black-hole effect removed.

Use the existing single R3F Canvas, Three.js, GSAP, and Lenis architecture. Choose between improving Blender/GLB assets and adding procedural geometry based on the actual source. Keep editable source and reproducible exports. Save a new Blender checkpoint before destructive model operations.

Preserve named node and material contracts used by rigs and `cases.ts`. Add detail around stable functional anchors. If an anchor must change, update its consumers and verify the projected endpoint follows the correct moving part.

Share geometry/materials, merge static meshes by material, and instance repeated details where appropriate. Retain independent moving assemblies. Dispose owned resources and keep loading/failure handling intact. Honor reduced motion. Measure model size, triangle count, draw calls, loading, and frame timing against the current baseline; identify any regression instead of claiming smoothness from screenshots.

## Completion criteria

- All five instruments show a clear improvement at normal viewing size in both chapters and case files.
- Main forms and motion remain clear on desktop and mobile; models do not obscure text or controls.
- All hotspot targets, leader lines, case transitions, history navigation, signal states, and fallback views still work.
- Run `npm run typecheck`, `npm run lint`, and `npm run build` from `web/`, plus relevant existing browser verification scripts against the rebuilt preview.
- Capture before/after screenshots and a short browser walkthrough showing idle motion, scroll, and case inspection. Include reduced-motion verification.
- Update the project progress log briefly. Report changes, verification results, evidence paths, and any remaining limitations.

Work instrument by instrument and complete all five. Do not commit, push, deploy, or publish unless separately requested.
