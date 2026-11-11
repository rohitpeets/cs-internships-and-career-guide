# Your First Projects

A project is a program (or a device) you build yourself. It shows you can learn, finish things, and explain them. On a first resume it counts as much as a job.

Short on time? See [the 5-hours-a-week version](#the-5-hours-a-week-version).

## Find an idea

Don't start from "what looks impressive." Start from a real annoyance.

**Ask 5 people this: "What is something boring or annoying you do by hand every week?"** Ask a classmate, a coworker, a club officer, a family member, and someone who runs a small business.

You'll hear things like:

- "I copy the club's sign-up form into a spreadsheet by hand."
- "We track who has the store keys on paper."
- "I can't tell which free time we all share for group projects."

Pick the one you could finish in 2 to 4 weeks. The person who told you becomes your first user.

## Three project levels

| Level | What it is | Counts for |
|---|---|---|
| **1. Learning** | Follow a tutorial or build a standard app (calculator, to-do list, quiz game). | Practice. Recruiters have seen thousands, so keep it off your resume once you have a level 2. |
| **2. Original** | Solves a real problem for real people. You made the design choices. | Your main resume project. |
| **3. Shipped and used** | Level 2, online or installed, with at least 3 real users and something you improved from their feedback. | Your best story in interviews. |

Aim to have one level 2 or 3 project by the time you apply for internships.

## From tutorial to original

A tutorial teaches you the parts. To make it yours, change it in three ways:

1. **Change the data or the goal.** A weather app tutorial becomes a "should I bike to campus today?" app that also checks your class times.
2. **Add something the tutorial didn't have.** Sign-in, saved history, email alerts, a test suite, or a second data source.
3. **Break and fix it.** Feed it bad input. Fix what crashes. Write down one fix.

Done looks like: you can explain every file without the tutorial open, and the project does something the tutorial doesn't.

## Scope rule

**Write down 3 features. Build only those.** Everything else goes in a "later" list that you don't touch until the 3 are done and working.

A finished small project beats five half-finished big ones. If a project is not done after 6 weeks, cut features until it is.

## The 5-hours-a-week version

Working or commuting? You can still finish a project. Use two 2-hour blocks and one 1-hour block per week:

- **Week 1:** Talk to your 5 people. Pick one. Write 3 features.
- **Weeks 2 to 4:** One feature per week. Push to GitHub at the end of every block.
- **Week 5:** Make it work for someone else: write a README, fix the first-run problems.
- **Week 6:** Get 3 people to use it. Fix the top thing that confuses them.

That is 30 hours total, and it's enough for a real level 2 project.

## Using AI tools

AI coding tools can speed you up. They can also leave you with a project you can't explain. Use this rule:

- **You must be able to explain every line you commit.** If you can't, ask the tool to explain it, then rewrite it yourself or delete it.
- Write the design yourself first (what the pieces are, how data moves). Then use the tool for small pieces and for explaining errors.
- Check your class's rules before you use AI on coursework. Many classes ban it.
- Expect interview questions like "why did you build it this way?" and "what would break if...?" A tool can't answer those for you.

## Ship it

- [ ] Put the code on GitHub from day one ([GitHub guide](github.md)).
- [ ] Write a README: a screenshot, what it does, how to run it. It must be true of the code.
- [ ] Put it online if it's a website. A dead link is worse than no link.
- [ ] Add a live link or a short demo video to the repo's About box.
- [ ] Get **3 real users**. Watch one of them try it without helping. Write down what confused them and fix it.
- [ ] Write down one bug you fixed or one thing you measured. That's your interview story.
- [ ] Prepare a one-page defense sheet for the project. See [project deep dive](interviews.md#project-deep-dive).
- [ ] Add it to your [resume](resume.md) with an honest bullet.

**Where to host:**

- **Static sites** (HTML, CSS, JavaScript only): [GitHub Pages](https://pages.github.com) is free and simple.
- **Apps with a server or database:** several services have free plans that work for small projects (for example Render, Netlify, Cloudflare Pages, and Hugging Face Spaces for ML demos). Free plans change and may put your app to sleep when nobody is using it, so check the current limits before you rely on one, and open the link yourself before every application.
- **No hosting at all?** A 60-second screen recording linked from your README works.

Never put passwords or API keys in your code. Use an environment variable, and keep an example file (`.env.example`) with fake values.

## Be honest about results

Report what really happened. "My model beat the simple baseline on 3 of 5 categories and did worse on the other 2" is a good result. It shows you measured. Interviewers trust honest numbers and test inflated ones.

Put real numbers in the README: how many users, how many tests, how fast, how accurate, and what you compared it to.

## Hardware and CE project ideas

Computer engineering and electronics students: a build you can photograph and demo is strong.

- A sensor logger (temperature, light, soil moisture) that saves readings to a file or a web page.
- A bus-time or weather display on a small screen.
- A door or window alarm that sends you a message.
- A line-following or obstacle-avoiding robot.

Put the code, a wiring diagram, a parts list, and a photo or short video in the repo. For more on this path, see [embedded and hardware tracks](tracks.md).

## Other ways to build experience

These also count as project experience. Some need more background, so they are labeled.

| Way | Needs experience? | Notes |
|---|---|---|
| **Hackathon** | No | A weekend, a team, a demo. Beginners and solo entrants are welcome at many. |
| **Research with a professor** | No | Ask one whose class you did well in. See [networking](networking.md). |
| **Class capstone or team project** | No | Treat it like a real project: write a README, keep a log of decisions, and save your metrics. |
| **Open source** | Some | Start with documentation fixes and issues labeled "good first issue." Plan on 20 or more hours before your first accepted change. |
| **Structured fellowships or programs** | Often | Some are competitive and ask for a project already. Apply after you have one finished project. |

## Resources

**Start**
- [CS50x](https://cs50.harvard.edu/x/): Harvard's free intro to CS. The best place to start if you've never coded.
- [The Missing Semester](https://missing.csail.mit.edu): the terminal, Git, and editor skills classes skip.
- [The Odin Project](https://www.theodinproject.com): free web development path, project-based.

**Build**
- [Build Your Own X](https://github.com/codecrafters-io/build-your-own-x): tutorials for building your own Git, database, shell, and more.
- [App Ideas](https://github.com/florinpop17/app-ideas): project ideas sorted by level.
- [Full Stack Open](https://fullstackopen.com): modern web development (React, Node) from the University of Helsinki.
- [Crafting Interpreters](https://craftinginterpreters.com): build a programming language; free to read online.
- [Exercism](https://exercism.org): practice exercises in many languages with free mentoring.

**Data and ML**
- [Kaggle Learn](https://www.kaggle.com/learn): short free courses on Python, pandas, SQL, and machine learning.

**Hardware**
- [Nand2Tetris](https://www.nand2tetris.org): build a computer from logic gates up.
- [Adafruit Learn](https://learn.adafruit.com): step-by-step electronics and microcontroller projects.

More lists are in [resources](resources.md).

Next: [find people](networking.md) to build with.
