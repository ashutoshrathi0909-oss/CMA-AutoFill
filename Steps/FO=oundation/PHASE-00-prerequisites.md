# PHASE 00: Prerequisites & Tooling Setup

> **Purpose:** Set up every account, tool, MCP server, and skill BEFORE any coding begins.
> **Who does this:** Ashutosh (manually, following this guide)
> **Time estimate:** 2-3 hours
> **Result:** Your machine is fully armed. Claude Code has maximum power from task #1.

---

## Section A: Accounts to Create

Create these accounts (all free tier). Save credentials in a secure note.

| # | Account | URL | Why You Need It | What to Save |
|---|---------|-----|-----------------|--------------|
| 1 | **GitHub** | github.com | Code storage, version control, Vercel auto-deploy | Username, email |
| 2 | **Vercel** | vercel.com | Frontend hosting (sign up WITH your GitHub account) | Auto-linked to GitHub |
| 3 | **Supabase** | supabase.com | Database, auth, file storage | Project URL, anon key, service role key |
| 4 | **Google AI Studio** | aistudio.google.com | Gemini API keys for extraction + classification | API key |
| 5 | **Resend** | resend.com | Email notifications (review ready, CMA complete) | API key |

### Supabase Project Setup
- Create a new project called `cma-autofill`
- Region: **Mumbai (ap-south-1)** — closest to India
- Save these from Settings → API:
  - Project URL (looks like `https://xxxxx.supabase.co`)
  - `anon` public key
  - `service_role` secret key (keep this secret!)
- Save from Settings → Database:
  - Connection string (for direct DB access)

### Google AI Studio Setup
- Go to aistudio.google.com
- Click "Get API Key" → Create API key
- This single key works for Gemini 2.0 Flash, Gemini 3 Flash, and Gemini 3.1 Pro
- Free tier: 1,000 requests/day (more than enough for 5 CMAs/month)

### Vercel Setup
- Sign up using "Continue with GitHub" (links them automatically)
- This means: push code to GitHub → Vercel deploys automatically
- No manual deploy needed ever

---

## Section B: Install Core Tools on Your Machine

### B1: Install Node.js
- Download from nodejs.org (LTS version)
- Verify: open terminal → `node --version` → should show v20+ or v22+
- This is required for Claude Code, MCP servers, and Next.js frontend

### B2: Install Git
- Download from git-scm.com (Windows installer)
- During install: choose "Git from the command line and also from 3rd-party software"
- Verify: `git --version`
- Configure:
  - `git config --global user.name "Your Name"`
  - `git config --global user.email "your-github-email@example.com"`

### B3: Install GitHub CLI
- Download from cli.github.com
- Verify: `gh --version`
- Authenticate: `gh auth login` → follow the browser flow
- This lets Claude Code and CCPM interact with GitHub directly

### B4: Install Python (for FastAPI backend)
- Download from python.org (3.11 or 3.12)
- IMPORTANT: Check "Add Python to PATH" during install
- Verify: `python --version` and `pip --version`

### B5: Install VS Code
- Download from code.visualstudio.com
- Install extensions:
  - Python (by Microsoft)
  - Tailwind CSS IntelliSense
  - ESLint
  - Prettier
- Open terminal inside VS Code: `Ctrl + `` (backtick key)

### B6: Install Claude Code
- In VS Code terminal: `npm install -g @anthropic-ai/claude-code`
- Run: `claude` → authenticate with your Anthropic account
- Verify: Claude Code responds in terminal
- You need Claude Pro ($20/mo) or Claude Max subscription

---

## Section C: Install CCPM (Claude Code Project Manager)

CCPM is the system that turns our phase documents into trackable GitHub Issues and lets multiple Claude Code agents work in parallel.

### What CCPM Gives Us
- Converts each phase into an "Epic" with sub-tasks
- Each sub-task becomes a GitHub Issue
- Claude Code agents work on issues independently
- Progress is posted as GitHub Issue comments
- You see everything on github.com like a project board

### Install CCPM
- Navigate to your project folder in terminal
- Run: `curl -sSL https://automaze.io/ccpm/install | bash`
- This creates a `.claude/` folder with all PM commands

### CCPM Commands We'll Use
| Command | What It Does |
|---------|-------------|
| `/pm:prd-new [name]` | Create a new Product Requirement Doc |
| `/pm:prd-parse [name]` | Break PRD into implementation tasks |
| `/pm:epic-oneshot [name]` | Push all tasks as GitHub Issues |
| `/pm:issue-start [id]` | Start Claude Code on a specific task |
| `/pm:issue-sync [id]` | Post progress to GitHub |
| `/pm:epic-show [name]` | Dashboard of all task status |
| `/pm:epic-merge [name]` | Merge all completed work |

### Our Workflow With CCPM
```
1. You feed a PHASE-XX.md document to Claude Code
2. Run /pm:prd-new cma-phase-XX
3. CCPM creates Epic + sub-tasks
4. /pm:epic-oneshot pushes to GitHub
5. /pm:issue-start [task-id] — Claude Code builds that task
6. You review the code/output
7. If good → next task. If not → comment feedback
8. /pm:epic-show shows overall progress
```

---

## Section D: Install MCP Servers (5 Total)

MCP servers extend Claude Code's capabilities. Run these commands in your terminal.

### D1: Supabase MCP (CRITICAL — install first)
**What it does:** Claude Code directly creates tables, runs queries, manages your database
**Without it:** You'd copy-paste SQL between Claude Code and Supabase dashboard
**Install:**
```
claude mcp add supabase --transport sse -- npx -y @supabase/mcp-server
```
**Configure:** Add your Supabase URL and service_role key when prompted

### D2: GitHub MCP (CRITICAL)
**What it does:** Claude Code creates commits, pushes code, creates PRs, manages issues
**Without it:** You'd manually run git commands after every change
**Install:**
```
claude mcp add github -- npx -y @modelcontextprotocol/server-github
```
**Configure:** Uses your `gh auth login` credentials automatically

### D3: Playwright MCP (IMPORTANT — for testing)
**What it does:** Claude Code opens a real browser, clicks buttons, fills forms, tests your app
**Without it:** You'd manually test every page and feature yourself
**When needed:** Phases 9-11 mainly, but install now
**Install:**
```
claude mcp add playwright -- npx -y @anthropic/mcp-playwright
```

### D4: Context7 MCP (HELPFUL — latest docs)
**What it does:** Fetches current documentation for Next.js, FastAPI, Supabase SDK in real-time
**Without it:** Claude Code might use outdated API patterns from its training data
**Install:**
```
claude mcp add context7 -- npx -y context7-mcp@latest
```

### D5: Sequential Thinking MCP (HELPFUL — complex logic)
**What it does:** Forces Claude Code to think step-by-step before writing complex code
**Without it:** Claude Code might rush into wrong architecture on hard problems
**When critical:** Phases 4-5 (AI extraction + classification pipeline)
**Install:**
```
claude mcp add sequential-thinking -- npx -y @anthropic/mcp-sequential-thinking
```

### Verify All MCPs
- In Claude Code, run: `/mcp`
- You should see all 5 servers listed and connected
- If any shows disconnected, re-run its install command

---

## Section E: Install Claude Skills

### E1: Official Anthropic Skills (from marketplace)
In Claude Code terminal:
```
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```
These give Claude Code better ability to work with Excel files (critical for CMA writer), PDFs, and structured documents.

### E2: QA Testing Skills
```
npx @qaskills/cli add playwright-e2e
npx @qaskills/cli add pytest-patterns
```
These teach Claude Code proper testing patterns so every feature gets tested.

### E3: Custom CMA Domain Skill (We Create This)
We will create a file at `.claude/skills/cma-domain/SKILL.md` that teaches Claude Code:
- What CMA documents are and why accuracy matters
- The 384 classification rules structure
- The Excel template layout (289 rows, 15 sheets)
- Pipeline flow: Extract → Classify → Validate → Generate → Review
- Common CA terminology and Indian financial document formats

**This skill is created in the CLAUDE.md setup (next section). Not done now.**

---

## Section F: Create GitHub Repo + Vercel Connection

### F1: Create the Repository
- Go to github.com → New Repository
- Name: `cma-autofill`
- Private repository (your business code!)
- Initialize with README
- Add `.gitignore` → choose Node template
- Create repository

### F2: Clone to Your Machine
```
cd C:\Projects   (or wherever you keep projects)
git clone https://github.com/YOUR-USERNAME/cma-autofill.git
cd cma-autofill
```

### F3: Connect Vercel
- Go to vercel.com/new
- Import your `cma-autofill` repository
- Framework: Next.js (auto-detected later)
- Deploy (it will be empty for now — that's fine)
- Result: You get a URL like `cma-autofill.vercel.app`

### F4: Verify Auto-Deploy
- Make any small change (edit README.md)
- `git add . && git commit -m "test" && git push`
- Check Vercel dashboard — it should auto-deploy within 60 seconds
- Every future push = automatic deployment

---

## Section G: Files to Gather

Before Phase 01, collect these files into a folder called `reference/` in your project:

| File | What It Is | Where You Have It |
|------|-----------|------------------|
| `cma_writer.py` | Your completed Excel Writer module (100% accuracy) | From previous development |
| `CMA.xlsm` | Empty CMA template (the target format) | From father's firm |
| `CMA_15092025.xls` | Completed reference CMA (Mehta Computers) | From father's firm |
| `CMA_classification.xls` | Your 384 classification rules table | From previous development |
| Sample P&L / Balance Sheet | Test documents (Mehta Computers originals) | From father's firm |

These reference files are what Claude Code will use to understand the domain and test against.

---

## Verification Checklist

Before moving to Phase 01, confirm ALL of these:

- [ ] GitHub account created, `gh auth login` works
- [ ] Vercel account linked to GitHub
- [ ] Supabase project created, all 3 keys saved
- [ ] Google AI Studio API key saved
- [ ] Resend account created, API key saved
- [ ] Node.js installed (`node --version` shows v20+)
- [ ] Git installed and configured
- [ ] Python installed (`python --version` shows 3.11+)
- [ ] VS Code installed with extensions
- [ ] Claude Code installed and authenticated
- [ ] CCPM installed (`.claude/` folder exists)
- [ ] All 5 MCP servers connected (`/mcp` shows them)
- [ ] Official skills installed
- [ ] QA skills installed
- [ ] GitHub repo `cma-autofill` created and cloned
- [ ] Vercel connected to repo, auto-deploy works
- [ ] Reference files gathered in `reference/` folder
- [ ] All API keys stored in a secure note

**Once all boxes are checked → Move to PHASE-01-project-init.md**

---

## ⚠️ Important Notes

1. **Do NOT start coding before this checklist is complete.** Missing an MCP server mid-build wastes time.
2. **Keep API keys out of code.** They go in `.env` files that are `.gitignore`d.
3. **The repo is PRIVATE.** Your CMA business logic and client data must never be public.
4. **Free tiers are enough for MVP.** Don't upgrade anything until you have 5 paying firms.
