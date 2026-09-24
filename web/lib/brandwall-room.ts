// Phase 7E (copy approved at gate 7E, 2026-09-24). Recorded pairs: brandwall/data/video/en_evidence, copied byte-for-byte.
// Counts and boundaries: portfolio/CAPABILITY_BRANDWALL.md §3, §6 K3/K5/K7/K15, §9.
export const specimens = [
  { id: 'portrait', capture: 'b08-tall-1x4__S1__light', title: 'A logo outside its frame', short: 'Crop',
    asset: 'Portrait logo', surface: 'S1 / Listing card', code: 'BW-C1 · BW-C6',
    view: '130 98 340 314', width: 1440, afterWidth: 1440, height: 900,
    before: 'The portrait extends below its slot and into the card.', after: 'A bounded slot contains the logo and gives the title its space.',
    measure: 'Crop: overflow > 2 px. Overlap: any whole pixel of intersection.',
    rule: 'Bound both dimensions. Fit the image inside its slot; keep the original proportions.' },
  { id: 'contrast', capture: 'b12-white-only__S4__light', title: 'White ink, pale surface', short: 'Contrast',
    asset: 'White-only logo', surface: 'S4 / Article footer', code: 'BW-C3',
    view: '137 451 393 164', width: 1440, afterWidth: 1440, height: 900,
    before: 'The white mark nearly disappears against the light footer.', after: 'The recorded fix uses a dark monochrome variant on the light footer.',
    measure: 'Logo contrast: below 3:1 is flagged by the recorded test policy.',
    rule: 'Use a monochrome variant for each theme. The demo applies a CSS brightness filter; real brand rules still need approval.' },
  { id: 'name', capture: 'b29-longname__S1__light', title: 'A name takes over the row', short: 'Overflow',
    asset: 'Long publication name', surface: 'S1 / Listing card', code: 'BW-C7',
    view: '134 92 747 310', phoneView: '134 92 706 599', width: 1550, afterWidth: 1440, height: 900,
    before: 'One long name stretches the card and crowds its neighbors.', after: 'The card keeps its allotted width; the name wraps within it.',
    measure: 'Text overflow: more than 1 px beyond the available row width.',
    rule: 'Allow the text column to shrink and wrap. Measure the row, not only the text element.' },
] as const;

export const boundaries = [
  { id: 'ratio', label: 'Portrait ratio', safe: '1.00', broken: '1.25', step: '0.25', unit: 'height / width',
    context: 'S1 listing card · BW-C1 crop', note: 'The first failing probe is 1.25. The exact transition lies between the tested values.' },
  { id: 'light', label: 'Logo brightness', safe: '0.30', broken: '0.35', step: '0.05', unit: 'relative luminance',
    context: 'S1 light theme · BW-C3 contrast', note: 'A light-theme boundary only. The dark-theme sweep changes in the opposite direction.' },
  { id: 'length', label: 'Latin name length', safe: '28', broken: '32', step: '4', unit: 'characters',
    context: 'S1 listing card · BW-C7 overflow', note: 'A range for the probe font and glyphs, not a universal name limit. Glyph widths can change the result.' },
] as const;

export const studioRules = [
  ['BW-C1', 'Crop', 'Contain the logo in a bounded slot.'],
  ['BW-C2', 'Text contrast', 'Use readable text colors for each theme.'],
  ['BW-C3', 'Logo contrast', 'Use a per-theme monochrome variant; the demo applies a brightness filter.'],
  ['BW-C4', 'Aspect ratio', 'Preserve proportions. No failures of this class were recorded.'],
  ['BW-C5', 'Missing or empty', 'Show a fallback, but reject the source asset. CSS does not repair it.'],
  ['BW-C6', 'Overlap', 'Reserve space between the logo and neighboring text.'],
  ['BW-C7', 'Text overflow', 'Let the text column shrink and wrap inside its row.'],
] as const;
