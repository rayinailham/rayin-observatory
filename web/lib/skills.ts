import type { InstrumentId } from './instruments';

type Skill = { name: string; projects: InstrumentId[] };
type SkillGroup = { name: string; items: Skill[] };
const all: InstrumentId[] = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall'];
export const skillGroups: SkillGroup[] = [
  { name: 'Languages & runtime', items: [{ name: 'Python', projects: all }] },
  { name: 'Test automation & QA', items: [
    { name: 'Playwright', projects: ['crosscheck', 'surgeline', 'brandwall'] },
    { name: 'Cross-browser testing · Chromium / Firefox / WebKit', projects: ['crosscheck'] },
    { name: 'Visual regression / design QA · Pillow, NumPy', projects: ['brandwall'] },
    { name: 'pytest', projects: ['duewatch'] },
    { name: 'unittest', projects: ['crosscheck', 'surgeline', 'driftwatch', 'brandwall'] },
  ] },
  { name: 'Web scraping & data', items: [
    { name: 'httpx', projects: ['driftwatch', 'crosscheck'] },
    { name: 'selectolax', projects: ['driftwatch'] },
    { name: 'tenacity', projects: ['driftwatch', 'crosscheck'] },
    { name: 'pydantic', projects: ['driftwatch'] },
  ] },
  { name: 'Backend & web', items: [
    { name: 'FastAPI', projects: ['brandwall', 'surgeline'] },
    { name: 'HTMX', projects: ['surgeline'] },
    { name: 'WordPress / PHP · test target', projects: ['crosscheck'] },
  ] },
  { name: 'Data & storage', items: [{ name: 'SQLite', projects: ['surgeline', 'driftwatch', 'duewatch', 'crosscheck'] }] },
  { name: 'Workflow automation', items: [{ name: 'n8n', projects: ['duewatch'] }] },
  { name: 'Scheduling & ops', items: [
    { name: 'systemd timers', projects: ['driftwatch', 'duewatch'] },
    { name: 'cron', projects: ['duewatch'] },
    { name: 'Linux', projects: ['driftwatch', 'duewatch'] },
  ] },
  { name: 'DevOps', items: [
    { name: 'Docker / Docker Compose', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
    { name: 'GNU Make', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
    { name: 'uv', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
  ] },
  { name: 'Reporting', items: [
    { name: 'Excel reporting · openpyxl', projects: ['brandwall', 'surgeline', 'driftwatch', 'crosscheck'] },
    { name: 'matplotlib', projects: ['brandwall', 'crosscheck'] },
  ] },
  { name: 'Media', items: [{ name: 'ffmpeg', projects: all }] },
  { name: 'AI-assisted engineering', items: [
    { name: 'Anthropic Claude API', projects: ['driftwatch'] },
    { name: 'Claude Code / MCP', projects: all },
  ] },
  // Owner-confirmed daily-work tools (2026-09-15); not part of the five case files, so no project link.
  { name: 'Daily work', items: [
    { name: 'Go', projects: [] },
    { name: 'MySQL / TiDB', projects: [] },
    { name: 'Redis', projects: [] },
  ] },
];
