---
description: Manage Scrum project from Antigravity IDE — create user stories, move issues, manage sprints, and track the backlog for web_api_knowledge
---

# Scrum Workflow — web_api_knowledge

## Project Reference
- **GitHub Project:** https://github.com/users/luisfponce/projects/1
- **Project Name:** web_api-sprint_planning_proj
- **Repository:** https://github.com/luisfponce/web_api_knowledge
- **Scrum Status Columns:** Backlog → Ready → In progress → In review → Done

---

## Available Commands

### /scrum create-story
Create a new User Story (GitHub Issue) with Scrum format.

**Steps:**
1. Ask the user for: Title, Description (As a user...), Acceptance Criteria, Story Points estimate, Labels (feature/bug/chore/tech-debt)
2. Use `mcp_github-mcp-server_issue_write` with method `create`, filling the body in Scrum template:
```
## 📖 User Story
As a **[role]**, I want **[goal]**, so that **[benefit]**.

## ✅ Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## 📊 Story Points: [number]
## 🏷️ Type: [feature | bug | chore | tech-debt]
```
3. The issue will be auto-added to the project via GitHub Actions (project-automation.yml)
4. Confirm to user with link to the created issue

---

### /scrum backlog
View and triage the prioritized backlog.

**Steps:**
1. Use `mcp_github-mcp-server_list_issues` with owner=luisfponce, repo=web_api_knowledge, state=OPEN
2. Display issues in a formatted table: # | Title | Labels | State
3. Ask the user if they want to update priority or move any item to the current sprint

---

### /scrum sprint-status
View current sprint status (Current Iteration view).

**Steps:**
1. Open https://github.com/users/luisfponce/projects/1 in browser via `browser_subagent`
2. Navigate to "Current iteration" view
3. Capture screenshot and report: items in each column (Backlog, Ready, In progress, In review, Done)
4. Show velocity estimate if visible

---

### /scrum move [issue-number] [status]
Move an issue to a different Scrum column.

**Valid statuses:** `backlog`, `ready`, `in-progress`, `in-review`, `done`

**Steps:**
1. Use `browser_subagent` to navigate to the project board
2. Find the issue card and drag it to the target column, or use the status dropdown on the issue
3. Alternatively, open the issue URL directly and update the project field via the sidebar
4. Confirm the move to user

---

### /scrum close-issue [issue-number]
Close an issue and mark it as Done in the project.

**Steps:**
1. Use `mcp_github-mcp-server_issue_write` with method `update`, state=closed, state_reason=completed
2. The issue will appear as Done in the project board
3. Report to user

---

### /scrum new-sprint
Plan a new sprint by selecting backlog items.

**Steps:**
1. Run `/scrum backlog` to show all open issues
2. Ask user which issues to include in the next sprint
3. For each selected issue, navigate to the project and assign it to the "Next iteration" field via browser
4. Confirm the sprint plan to user

---

### /scrum sprint-review
Summarize completed sprint work.

**Steps:**
1. Use `mcp_github-mcp-server_list_issues` with state=CLOSED, filter recent
2. Also run `mcp_github-mcp-server_list_commits` to summarize recent commits on main
3. Generate a sprint review summary: completed stories, PRs merged, velocity
4. Present to user in markdown format

---

## Labels Guide (apply when creating issues)

| Label | When to use |
|---|---|
| `enhancement` | New feature or improvement |
| `bug` | Something is broken |
| `good first issue` | Simple task for onboarding |
| `frontend` | Frontend-related work |
| `tech-debt` | Refactoring or cleanup |
| `documentation` | Docs, README, Swagger |

---

## Notes
- New issues/PRs are **automatically added** to the project via `.github/workflows/project-automation.yml`
- Story Points should be set manually in the project sidebar after issue creation
- Sprint assignment (Iteration field) must be set in the project board
- Use `/scrum sprint-status` to get a real-time snapshot of the current iteration
