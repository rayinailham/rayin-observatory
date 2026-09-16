import type { InstrumentId } from './instruments';

/** `note` is one line on what the tool does here; it awaits the owner's copy approval. */
type Skill = { name: string; note: string; projects: InstrumentId[] };
/** `blurb` says what the group is for; `swaps` names tools that do the same job — they are
    equivalents in the field, not work I am claiming. Both await the owner's copy approval. */
type SkillGroup = { name: string; blurb: string; items: Skill[]; swaps: string[] };
const all: InstrumentId[] = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall'];
export const skillGroups: SkillGroup[] = [
  { name: 'Languages & runtime', blurb: 'The language every instrument in this observatory is written in.', swaps: ['Node.js', 'Go', 'Ruby'], items: [{ name: 'Python', note: 'One language for the scrapers, the tests and the reports.', projects: all }] },
  { name: 'Test automation & QA', blurb: 'Driving real browsers until an app admits what breaks, then writing it down.', swaps: ['Selenium', 'Cypress', 'Puppeteer'], items: [
    { name: 'Playwright', note: 'One script drives Chromium, Firefox and WebKit.', projects: ['crosscheck', 'surgeline', 'brandwall'] },
    { name: 'Cross-browser testing · Chromium / Firefox / WebKit', note: 'The same suite run on all three engines.', projects: ['crosscheck'] },
    { name: 'Visual regression / design QA · Pillow, NumPy', note: 'Pixel diffs that catch what eyes skip.', projects: ['brandwall'] },
    { name: 'pytest', note: 'Fixtures and parametrised cases for wide suites.', projects: ['duewatch'] },
    { name: 'unittest', note: 'Standard-library tests, no extra dependency.', projects: ['crosscheck', 'surgeline', 'driftwatch', 'brandwall'] },
  ] },
  { name: 'Web scraping & data', blurb: 'Collecting pages on a schedule and parsing them into typed records.', swaps: ['requests', 'BeautifulSoup', 'Scrapy'], items: [
    { name: 'httpx', note: 'HTTP client with strict timeouts, sync or async.', projects: ['driftwatch', 'crosscheck'] },
    { name: 'selectolax', note: 'Fast HTML parsing when the pages are large.', projects: ['driftwatch'] },
    { name: 'tenacity', note: 'Retry and backoff around flaky network calls.', projects: ['driftwatch', 'crosscheck'] },
    { name: 'pydantic', note: 'Validates scraped rows before anything stores them.', projects: ['driftwatch'] },
  ] },
  { name: 'Backend & web', blurb: 'Small services and thin interfaces to drive the work and show it.', swaps: ['Flask', 'Django', 'Express'], items: [
    { name: 'FastAPI', note: 'Small APIs and dashboards around a run.', projects: ['brandwall', 'surgeline'] },
    { name: 'HTMX', note: 'Server-rendered interaction without a front-end build.', projects: ['surgeline'] },
    { name: 'WordPress / PHP · test target', note: 'An owned site to test against, safely.', projects: ['crosscheck'] },
  ] },
  { name: 'Data & storage', blurb: 'Local, file-backed state that survives a crash halfway through a run.', swaps: ['PostgreSQL', 'DuckDB'], items: [{ name: 'SQLite', note: 'File-backed state that survives a crash mid-run.', projects: ['surgeline', 'driftwatch', 'duewatch', 'crosscheck'] }] },
  { name: 'Workflow automation', blurb: 'Wiring steps, retries and alerts together without a service for each one.', swaps: ['Zapier', 'Make', 'Airflow'], items: [{ name: 'n8n', note: 'Visual workflows for alerts and follow-ups.', projects: ['duewatch'] }] },
  { name: 'Scheduling & ops', blurb: 'Making a job run unattended, on time, and prove that it ran.', swaps: ['Airflow', 'Celery beat', 'Kubernetes CronJob'], items: [
    { name: 'systemd timers', note: 'Unattended runs with logs and restart rules.', projects: ['driftwatch', 'duewatch'] },
    { name: 'cron', note: 'The plain schedule when a timer is overkill.', projects: ['duewatch'] },
    { name: 'Linux', note: 'Where the jobs actually live and run.', projects: ['driftwatch', 'duewatch'] },
  ] },
  { name: 'DevOps', blurb: 'Reproducible environments and one command that runs the whole thing.', swaps: ['Podman', 'Task', 'pip-tools'], items: [
    { name: 'Docker / Docker Compose', note: 'The same environment on my machine and yours.', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
    { name: 'GNU Make', note: 'One command per task, written down in the file.', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
    { name: 'uv', note: 'Fast, locked Python environments.', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
  ] },
  { name: 'Reporting', blurb: 'Turning a run into a file a client can open and act on.', swaps: ['pandas', 'XlsxWriter', 'Plotly'], items: [
    { name: 'Excel reporting · openpyxl', note: 'Results as a workbook a client can open.', projects: ['brandwall', 'surgeline', 'driftwatch', 'crosscheck'] },
    { name: 'matplotlib', note: 'Charts that carry the numbers, not decoration.', projects: ['brandwall', 'crosscheck'] },
  ] },
  { name: 'Media', blurb: 'Turning a run into short, silent, captioned video proof.', swaps: ['MoviePy', 'ImageMagick', 'OBS'], items: [{ name: 'ffmpeg', note: 'Silent, captioned video proof of a run.', projects: all }] },
  { name: 'AI-assisted engineering', blurb: 'Using models where they shorten the loop, with every output checked.', swaps: ['OpenAI API', 'Ollama', 'LangChain'], items: [
    { name: 'Anthropic Claude API', note: 'Model calls inside a pipeline, output checked.', projects: ['driftwatch'] },
    { name: 'Claude Code / MCP', note: 'Agent tooling for building and reviewing the work.', projects: all },
  ] },
  // Owner-confirmed daily-work tools (2026-09-15); not part of the five case files, so no project link.
  { name: 'Daily work', blurb: 'Tools I work with day to day, outside the five case files.', swaps: ['PostgreSQL', 'Memcached', 'Java'], items: [
    { name: 'Go', note: 'Services and CLIs in day-to-day work.', projects: [] },
    { name: 'MySQL / TiDB', note: 'Relational and distributed SQL at work.', projects: [] },
    { name: 'Redis', note: 'Cache and queue for the hot paths.', projects: [] },
  ] },
];
