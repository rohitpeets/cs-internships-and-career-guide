# What Interviewers Actually Look For

An interview is not a test you pass by getting the perfect answer. It's a sample of what you'd be like to work with: how you think, how you talk about your work, and what you do when you're stuck. This guide covers each round and what gets scored. To get the interview in the first place, see [applying](applying.md).

## Recruiter call

Usually 15 to 30 minutes, by phone or video. The recruiter checks that you're real, interested, and a fit for the basics.

**Expect:** "Tell me about yourself." "Why this company?" "What have you built?" "When do you graduate?" "Are you authorized to work in the U.S.?" "Where are you in your search?" Sometimes "Which team or location do you prefer?"

**Your 30-second answer to "tell me about yourself":** present, past, future. Three or four sentences.

> I'm a junior studying computer engineering at [school]. Last year I built a tool that tracks lab equipment checkouts for my department. About 60 students use it, and I wrote the backend in Python. I also work part-time as an IT help desk tech, so I'm used to fixing problems for real users. I'm looking for a summer internship where I can work on backend or infrastructure, and your team's work on [specific thing] is why I applied.

Practice it out loud until it sounds like you talking, not reading. Have one question ready for the recruiter: "What do the next rounds look like?"

## Technical interview

### What a 45-minute round looks like

| Minutes | What happens |
|---|---|
| 0 to 5 | Introductions, maybe "tell me about a project" |
| 5 to 10 | The problem. You ask questions and work through an example |
| 10 to 35 | You explain a plan, write the code, and test it |
| 35 to 40 | Follow-ups: "What's the time complexity?" "What if the input were huge?" |
| 40 to 45 | Your questions for them |

It's usually one or two problems on arrays, strings, hash maps, trees, or graphs. You'll write code in a shared editor or a doc, often without running it. Prepare with [coding practice](timeline.md#coding-interview-practice).

### What interviewers score

Most companies use a rubric with roughly these items. Getting the optimal answer is only one of them.

1. **Clarifying questions.** "Can the list be empty?" "Are there duplicates?" "How big can the input get?" Ask before you code.
2. **A simple solution first.** Say the brute-force idea and its cost out loud: "I could check every pair. That's O(n²)." Then improve it.
3. **Talking through your plan.** Explain the approach before typing, so the interviewer can steer you early.
4. **Working code.** Clear names, small helper functions, no half-finished lines.
5. **Testing your own code.** Walk through one normal example and one edge case (empty input, one item) line by line, before they ask.
6. **Recovering when stuck.** Getting stuck is expected. What you do next is scored.
7. **Complexity.** State the time and space cost of your final answer.

**Never go silent.** If you're stuck, say what you've tried and where it breaks:

> I tried sorting first, but that loses the original positions, which we need. I'm thinking a hash map from value to index might work instead. Can I try that?

Interviewers often give hints. Taking a hint well counts in your favor.

## Take-homes and live coding

**Take-home projects** (a small app or feature you build in a few days):

- **Keep the scope small.** Do what they asked, done well, instead of extra features half done.
- **Write a README** with how to run it, your assumptions ("I assumed usernames are unique"), and what you'd do with more time.
- **Add a few tests** for the main logic. It shows you check your own work.
- **Watch the time limit.** If they say 4 hours, don't spend 20. They will ask how long you took.

**Live coding** (building or changing something while they watch):

- **Plan before typing.** Spend the first few minutes saying what you'll build and in what order.
- **Run your code early and often** if the tool lets you. Small working steps beat one big untested block.
- **Narrate.** "I'm adding a check for an empty file here because..."

## Project deep dive

Many interviews include 10 minutes or more on a project from your resume. The interviewer is checking that you actually built it and understand it. Be ready to go that deep on any project you list.

**Make a one-page defense sheet for each project:**

- **Problem:** who it's for and what it solves, in one sentence.
- **Your exact role:** what *you* built. Not the team.
- **Architecture:** the main pieces and how data moves between them. Be able to sketch it.
- **One hard bug:** the symptom, how you found the cause, and the fix (use the [debugging story](#debugging-story-template) below).
- **One tradeoff:** a choice you made and what you gave up. ("I used SQLite instead of Postgres because it's one file and easy to host. It won't handle many users writing at once.")
- **One measurement:** a number. Users, speed, accuracy, time saved, test coverage.
- **What you'd change:** with what you know now.

Reread the code before the interview. If you can't explain a part, learn it or take it off your resume.

## AI tools

Using AI tools to build your projects is fine and common. Interviewers know. What they check is whether *you* understand the result.

Be ready for:

- **"Walk me through this function."** Line by line, in your own words.
- **"Why did you do it this way?"** Know the alternatives.
- **"What did the AI get wrong?"** Have a real example: a bug it introduced, an outdated library it suggested, code that worked but was slow. A good answer shows you check its output.

During interviews and online assessments, follow each company's rules. Most ban AI help unless they say otherwise.

## Behavioral

Behavioral questions start with "Tell me about a time..." They predict how you'll act at work from how you've acted before.

**Use STAR:** Situation, Task, Action, Result. Spend most of the time on Action. Say "I," not "we." The interviewer is hiring you, not your team.

**Worked example.** "Tell me about a time you had a conflict on a team."

> **Situation:** In my software engineering class, our four-person team was building a web app, and two weeks before the deadline one teammate kept pushing code that broke the main branch.
>
> **Task:** I was in charge of merging, so it was on me to fix the process without making it personal.
>
> **Action:** I asked him to talk one-on-one and found out he didn't know how to run the tests locally. I wrote a one-page setup guide, paired with him for 30 minutes, and set up a rule that pull requests needed one approval and passing tests before merging.
>
> **Result:** We had no more broken merges, shipped on time, and he ended up reviewing more pull requests than anyone. I learned to ask what's going on before assuming someone doesn't care.

**Prepare 6 stories.** Write each one in STAR form, 4 to 6 sentences:

- [ ] A team conflict or disagreement
- [ ] A mistake you made and fixed
- [ ] A time you led something
- [ ] A failure, and what you changed after it
- [ ] A tight deadline
- [ ] Learning something new fast

One story can answer several questions. **Your stories don't have to be from tech.** A retail or restaurant job, caregiving, helping run a family business, organizing an event, a sports team, or a club fundraiser all count. Handling an angry customer, keeping a budget, or getting vendors to commit is real experience. Say what you did and what happened.

## Debugging story template

"Tell me about a hard bug" is one of the most common questions. Fill this in for your best one:

1. **Symptom:** what you saw. ("The app showed the wrong totals, but only for some users.")
2. **First guess, and why it was wrong:** ("I thought it was the math, but the math was fine in tests.")
3. **How you narrowed it down:** logs, print statements, a debugger, a smaller test case, reading the docs. ("I logged the input and saw the bad totals were all from users in a different time zone.")
4. **Root cause:** ("Dates were stored in local time, so orders near midnight landed on the wrong day.")
5. **Fix:** ("I stored everything in UTC and converted only for display.")
6. **What you do differently now:** ("I add a test for time zones on anything with dates.")

## Questions to ask them

Always have questions. "No, I think you covered everything" sounds uninterested. Pick from these:

- "What does a typical week look like for an intern on this team?"
- "What did a past intern build that you were proud of?"
- "How do interns get feedback, and how often?"
- "What's something you've learned working here that surprised you?"
- "What would make someone really successful in this role in the first month?"

Skip questions about pay or time off in technical rounds. Save those for the recruiter.

## Video interview setup

Check this the day before, not five minutes before:

- [ ] Laptop plugged in, notifications off, other apps closed
- [ ] The interview link opens, and the app (Zoom, Teams, Google Meet) is installed and updated
- [ ] Camera at eye level, face lit from the front (a window or lamp facing you, not behind you)
- [ ] Plain background, quiet room; tell roommates or family the time
- [ ] Wired earbuds or a headset, tested with a friend
- [ ] Internet tested; your phone ready as a hotspot backup
- [ ] Recruiter's email or phone number written down in case the call drops
- [ ] Water, paper, and a pen
- [ ] Your defense sheets and STAR stories nearby, but don't read from them

If something breaks mid-call, say so calmly and fix it. It happens to everyone.

## Hardware, embedded, and security interviews

These tracks interview differently. Embedded and hardware roles ask about C, pointers and memory, microcontrollers, digital logic, and lab or debugging work with real hardware. Security roles often ask about networking, operating systems, and how attacks work, and may include a hands-on challenge. Coding problems still show up, but they're usually not the whole interview. See [tracks](tracks.md) for how to prepare for each one.

## Resources

- [Tech Interview Handbook: coding interview techniques](https://www.techinterviewhandbook.org/coding-interview-techniques/): how to approach a problem step by step.
- [Tech Interview Handbook: behavioral interviews](https://www.techinterviewhandbook.org/behavioral-interview/): more on STAR and common questions.
- [Tech Interview Handbook: self introduction](https://www.techinterviewhandbook.org/self-introduction/) and [questions to ask](https://www.techinterviewhandbook.org/final-questions/).
- [NeetCode](https://neetcode.io): problem lists with video explanations.
- [Pramp](https://www.pramp.com): free peer mock interviews. You take turns interviewing each other.
- Your career center: most offer free mock interviews and will review your STAR stories.

Next: [the 4-year timeline](timeline.md).
