import type { InstrumentId } from './instruments';

/** `note` explains what the tool is and how it is used here, for a reader who has never met it.
    `projects` stays per tool, but the card shows the group's proving projects in one footer row. */
type Skill = { name: string; note: string; projects: InstrumentId[] };
/** `blurb` says what the group is for; `swaps` names tools that do the same job — they are
    equivalents in the field, not work I am claiming. */
type SkillGroup = { name: string; blurb: string; items: Skill[]; swaps: string[] };
const all: InstrumentId[] = ['crosscheck', 'surgeline', 'driftwatch', 'duewatch', 'brandwall'];
export const skillGroups: SkillGroup[] = [
  { name: 'Languages & runtime', blurb: 'The language every instrument in this observatory is written in.', swaps: ['Node.js', 'Go', 'Ruby'], items: [
    { name: 'Python', note: 'The language I write everything in: the scrapers, the tests, the schedulers and the report generators all run on it.', projects: all },
  ] },
  // Owner request (2026-09-16): the ordinary scripting tools that carry most automation work.
  { name: 'Scripting & glue', blurb: 'The small, ordinary tools that hold an automation together — and the ones an AI assistant writes well.', swaps: ['urllib', 'lxml', 'Click'], items: [
    { name: 'requests', note: 'The simplest way to call a website or an API from a script: fetch a page, post a form, read JSON back.', projects: [] },
    { name: 'BeautifulSoup', note: 'Reads messy HTML and pulls out a price, a table or a link by name, even when the markup is broken.', projects: [] },
    { name: 'pandas', note: 'Loads a CSV or a query result as a table, then filters, joins and counts it before the report.', projects: [] },
    { name: 'Typer / argparse', note: 'Turns a script into a real command with flags, so the job can be scheduled and handed over.', projects: [] },
    { name: 'python-dotenv', note: 'Keeps keys and URLs in a .env file next to the job, never inside the code.', projects: [] },
    { name: 'rich', note: 'Prints progress bars, tables and logs while a long run works, so its position is always clear.', projects: [] },
  ] },
  { name: 'Test automation & QA', blurb: 'Driving real browsers until an app admits what breaks, then writing it down.', swaps: ['Selenium', 'Cypress', 'Puppeteer'], items: [
    { name: 'Playwright', note: 'A browser-automation library: one script opens a real browser, clicks through the app like a user and checks what it finds.', projects: ['crosscheck', 'surgeline', 'brandwall'] },
    { name: 'Cross-browser testing · Chromium / Firefox / WebKit', note: 'The same suite run on the three engines behind Chrome, Firefox and Safari; a bug often shows on only one.', projects: ['crosscheck'] },
    { name: 'Visual regression / design QA · Pillow, NumPy', note: 'Screenshots compared pixel by pixel against an approved one, so a shifted button or wrong colour is caught automatically.', projects: ['brandwall'] },
    { name: 'pytest', note: 'The test runner I reach for first: plain test functions, shared setup, and one run per row of data from a single case.', projects: ['duewatch'] },
    { name: 'unittest', note: 'The test framework built into Python itself: tests written as classes that run anywhere, with nothing extra to install.', projects: ['crosscheck', 'surgeline', 'driftwatch', 'brandwall'] },
  ] },
  { name: 'Web scraping & data', blurb: 'Collecting pages on a schedule and parsing them into typed records.', swaps: ['requests', 'Scrapy', 'Selenium'], items: [
    { name: 'httpx', note: 'The HTTP client for the heavier jobs: strict timeouts, reused connections, and async when hundreds of pages must be fetched at once.', projects: ['driftwatch', 'crosscheck'] },
    { name: 'selectolax', note: 'A very fast HTML parser: I hand it a page and a CSS selector, and it returns the fields I want without slowing the run down.', projects: ['driftwatch'] },
    { name: 'tenacity', note: 'Wraps a call that can fail in automatic retries with a growing wait, so one dropped connection does not end the whole job.', projects: ['driftwatch', 'crosscheck'] },
    { name: 'pydantic', note: 'Declares the shape every record must have and refuses the rows that do not fit, before anything is stored or reported.', projects: ['driftwatch'] },
  ] },
  { name: 'Backend & web', blurb: 'Small services and thin interfaces to drive the work and show it.', swaps: ['Flask', 'Django', 'Express'], items: [
    { name: 'FastAPI', note: 'A Python web framework I use to put a small API or control panel in front of a running job, with typed inputs and free docs.', projects: ['brandwall', 'surgeline'] },
    { name: 'HTMX', note: 'Lets a normal server-rendered page update one part of itself on a click, so a control panel needs no front-end build step.', projects: ['surgeline'] },
    { name: 'WordPress / PHP · test target', note: 'A site I host myself purely to test against, so the automation is proven on my own server and never on someone else’s.', projects: ['crosscheck'] },
  ] },
  { name: 'Data & storage', blurb: 'Local, file-backed state that survives a crash halfway through a run.', swaps: ['PostgreSQL', 'DuckDB'], items: [
    { name: 'SQLite', note: 'A whole database inside one file: the job records what it has already done, so a crash resumes instead of starting over.', projects: ['surgeline', 'driftwatch', 'duewatch', 'crosscheck'] },
  ] },
  { name: 'Workflow automation', blurb: 'Wiring steps, retries and alerts together without a service for each one.', swaps: ['Zapier', 'Make', 'Airflow'], items: [
    { name: 'n8n', note: 'A workflow built by dragging boxes: a trigger, then HTTP calls, conditions and an alert, run on schedule without a service of its own.', projects: ['duewatch'] },
    { name: 'PyAutoGUI', note: 'Moves the mouse and types for me, for the rare program that has no API and can only be driven through its own window.', projects: [] },
  ] },
  { name: 'Scheduling & ops', blurb: 'Making a job run unattended, on time, and prove that it ran.', swaps: ['Airflow', 'Celery beat', 'Kubernetes CronJob'], items: [
    { name: 'systemd timers', note: 'The Linux way to run a job on a schedule: it keeps the logs, restarts a failure and records every run, unattended.', projects: ['driftwatch', 'duewatch'] },
    { name: 'cron', note: 'One line per schedule — the plain option when a job is simple and a full timer would be more machinery than it needs.', projects: ['duewatch'] },
    { name: 'Linux', note: 'The machine the jobs actually live on: the shell, the permissions, the logs and the services are part of the work.', projects: ['driftwatch', 'duewatch'] },
  ] },
  { name: 'DevOps', blurb: 'Reproducible environments and one command that runs the whole thing.', swaps: ['Podman', 'Task', 'pip-tools'], items: [
    { name: 'Docker / Docker Compose', note: 'Packs the job and everything it needs into an image, so it behaves the same on my machine, on a server and on yours.', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
    { name: 'GNU Make', note: 'One short command per task — make test, make run — with the real steps written down in the file instead of in my head.', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
    { name: 'uv', note: 'Installs and locks Python dependencies in seconds, so the exact environment a run needs can be rebuilt later.', projects: ['brandwall', 'surgeline', 'duewatch', 'crosscheck'] },
  ] },
  { name: 'Reporting', blurb: 'Turning a run into a file a client can open and act on.', swaps: ['XlsxWriter', 'Plotly', 'Jinja'], items: [
    { name: 'Excel reporting · openpyxl', note: 'Writes the results straight into a formatted .xlsx workbook, so the client opens, sorts and filters them in Excel.', projects: ['brandwall', 'surgeline', 'driftwatch', 'crosscheck'] },
    { name: 'matplotlib', note: 'Draws the charts that go into a report from the same numbers the run produced, so the picture and the data cannot drift apart.', projects: ['brandwall', 'crosscheck'] },
    { name: 'pdfplumber', note: 'Pulls the text and tables out of a PDF, so a document can be checked automatically or turned back into data.', projects: [] },
  ] },
  { name: 'Media', blurb: 'Turning a run into short, silent, captioned video proof.', swaps: ['MoviePy', 'ImageMagick', 'OBS'], items: [
    { name: 'ffmpeg', note: 'Cuts, converts and captions a screen recording from the command line, so a long run becomes a short clip that proves it.', projects: all },
  ] },
  { name: 'AI-assisted engineering', blurb: 'Using models where they shorten the loop, with every output checked.', swaps: ['OpenAI API', 'Ollama', 'LangChain'], items: [
    { name: 'Anthropic Claude API', note: 'Calls a model from inside a script for the judgement steps, with every answer checked back against the raw data.', projects: ['driftwatch'] },
    { name: 'Claude Code / MCP', note: 'An agent that works in the terminal on the real repository; MCP is the standard that lets it reach tools such as a browser.', projects: all },
  ] },
  // Owner-confirmed daily-work tools (2026-09-15); not part of the five case files, so no project link.
  { name: 'Daily work', blurb: 'Tools I work with day to day, outside the five case files.', swaps: ['PostgreSQL', 'Memcached', 'Java'], items: [
    { name: 'Go', note: 'A compiled language used at work for services and small command-line tools that have to start fast and stay light.', projects: [] },
    { name: 'MySQL / TiDB', note: 'The databases behind day-to-day work: MySQL on a single server, TiDB when the same data has to spread over several.', projects: [] },
    { name: 'Redis', note: 'An in-memory store used as a cache and a queue, for the paths that are hit too often to touch the database every time.', projects: [] },
  ] },
];
