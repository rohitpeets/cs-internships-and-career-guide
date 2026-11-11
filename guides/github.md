# GitHub Setup

GitHub is where programmers store and share code. Few recruiters look at it in the first screen. It matters later: when an interviewer or hiring manager clicks your link, it shows your resume is true. One finished repo with a good README is enough to start.

## Make your account

- [ ] Sign up at github.com with a personal email (your school email can stop working after you graduate).
- [ ] Pick a simple username, like your name. Avoid jokes and numbers.
- [ ] Add a clear photo and your name.
- [ ] Turn on two-factor login (see [Protect your account](#protect-your-account)).

## Git basics

**Git** tracks changes to your code. **GitHub** is a website that stores your Git projects. You need both.

**1. Install.** Install [Git](https://git-scm.com/downloads), or install [GitHub Desktop](https://desktop.github.com) if you prefer clicking to typing. Desktop includes Git.

**2. Tell Git who you are.** Once per computer, in a terminal:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Commits carry this email, and it's public on your repos. If you don't want your real email public, turn on "Keep my email addresses private" in GitHub Settings under Emails. GitHub then shows you a private `noreply` address to use as `user.email`.

**3. The five commands you'll use every day:**

```
git clone <repo-url>     # copy a repo to your computer
git add .                # choose the changes to save
git commit -m "Add login form"   # save a snapshot with a message
git push                 # upload your commits to GitHub
git pull                 # download changes you don't have yet
```

**4. Signing in.** GitHub does not accept your account password on the command line. Use one of these:
- GitHub Desktop: sign in once in the app.
- VS Code: sign in to GitHub when it asks.
- The GitHub command-line tool: install `gh`, run `gh auth login`, and follow the prompts.

**5. Practice 5 times.** Make a practice repo. Clone it, change a file, add, commit, push. Do it five times until you stop looking up the commands.

**Done looks like:** you can start a new project, push it, and see it on github.com without help.

## Profile and pins

- Optional: a profile README (a public repo with the **same name as your username**) with 3 lines: who you are, what you're learning, and your LinkedIn link. Skip badges and stat widgets.
- **Pin 2 to 4 repos** that run and have a README. GitHub allows up to 6. Don't pin empty homework folders.

## What a good repo looks like

- [ ] A clear name (`study-planner`, not `project1`).
- [ ] A README with: what it does (one sentence), a screenshot, how to run it, and what you used.
- [ ] **The README is true of the code.** If it says "supports login," login works. Interviewers will test your claims.
- [ ] It runs with one or two commands. If it's a website or app, put the live link in the repo's **About** box (the gear icon on the right of the repo page).
- [ ] No passwords or API keys in the code. Ever.
- [ ] A `.gitignore` file so you don't upload junk files.
- [ ] Commit messages that say what you did ("Add login form", not "stuff").

## 30-minute cleanup pass

Do this before you apply. Set a timer.

1. **Pins:** keep 2 to 4 best repos.
2. **README:** each pinned repo has what, screenshot, how to run, and a live link in About. Check it matches the code.
3. **Junk:** delete build folders, `node_modules`, and `.DS_Store` files from the repo, and add them to `.gitignore`.
4. **Names:** rename `project1` and `test2`. Delete empty or abandoned repos, or archive them (Settings, then Archive).
5. **Secrets:** search your code for `password`, `key`, and `token`. Use a `.env` file for secrets, keep it out of Git with `.gitignore`, and commit an example file (`.env.example`) with blank values. **If a secret was ever pushed, deleting it isn't enough. Go to the service that issued it and rotate it (make a new key and cancel the old one).** GitHub's history keeps the old one.
6. **Default branch** is `main`, and the repo About box has a short description and topics.

## Class projects

Put class projects on GitHub only if your professor allows it. Never post exam answers or code you were told to keep private. If a project is allowed, rename it so it's clear what you built (`library-system`, not `CS201-hw4`) and write a README. Group projects: it's fine to list your part honestly ("I built the database and login").

## Your activity graph

The green squares on your profile are not required. Employers know students have busy weeks. A few real projects beat a streak of tiny commits.

## Student Developer Pack

Free tools and trials for students (developer tools, cloud credits, domains). To apply you need a GitHub account and proof you're enrolled: a school email you've added and verified, or a document such as a school ID, class schedule, or enrollment letter. Details and offers change, so read the [pack page](https://education.github.com/pack). It can take a few days.

## Protect your account

- [ ] Turn on two-factor authentication (2FA) in Settings. Use an authenticator app or a passkey (a login stored on your phone or computer).
- [ ] Download your **recovery codes** and save them somewhere safe (a password manager or a printed copy). Without them, losing your phone can lock you out of your own code.

## Good habits

- Read other people's code.
- When you're ready for open source, pick a project you actually use and look for issues labeled "good first issue".

## Resources

- [GitHub Skills](https://skills.github.com): free hands-on courses inside GitHub.
- [Pro Git](https://git-scm.com/book/en/v2): the free official Git book.
- [Make a README](https://www.makeareadme.com): a simple guide with a template.
- [First Contributions](https://github.com/firstcontributions/first-contributions): practice making your first pull request.
- [GitHub Student Developer Pack](https://education.github.com/pack): free tools for students.

Next: [build a project](projects.md) worth putting here.
