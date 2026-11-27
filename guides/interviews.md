# Interviews

An interview is not a test you pass by getting the perfect answer. It's a sample of what you'd be like to work with: how you think, how you talk about your work, and what you do when you're stuck. This guide covers each round and what gets scored. To get the interview in the first place, see [applying](applying.md).

Formats vary by company and role. Everything below is a typical shape, not a rule. Ask the recruiter: "What will the rounds look like, and is there anything I should prepare?" Most will tell you.

## Recruiter call

Usually 15 to 30 minutes, by phone or video. The recruiter checks that you're real, interested, and a fit for the basics.

**Expect:** "Tell me about yourself." "Why this company?" "What have you built?" "When do you graduate?" "Are you authorized to work in the U.S.?" "Where are you in your search?" Sometimes "Which team or location do you prefer?"

**Your 30-second answer to "tell me about yourself":** present, past, future. Three or four sentences. Pattern:

> I'm a [year] [major] at [school]. [Past: one project or job with a result.] [Present: what you're doing now.] I'm looking for a [role] where I can [skill], and I'm interested in [company or team] because [one specific thing].

Example:

> I'm a junior studying computer engineering at [school]. Last year I built a tool that tracks lab equipment checkouts for my department. About 60 students use it, and I wrote the backend in Java. I also work part-time at an IT help desk, so I'm used to fixing problems for real users. I'm looking for a summer internship where I can work on backend or infrastructure, and your team's work on [specific thing] is why I applied.

Practice it out loud until it sounds like you, not a script. Have one question ready: "What do the next rounds look like?" Send a two-line thank-you within 24 hours.

## Technical interview

### What a 45-minute round can look like

An example only. Your round may differ.

| Minutes | What happens |
|---|---|
| 0 to 5 | Introductions, maybe "tell me about a project" |
| 5 to 10 | The problem. You ask questions and work through an example |
| 10 to 35 | You explain a plan, write the code, and test it |
| 35 to 40 | Follow-ups: "What's the time complexity?" "What if the input were huge?" |
| 40 to 45 | Your questions for them |

It's often one or two problems on arrays, strings, hash maps, trees, or graphs. You'll write code in a shared editor or a doc, sometimes without running it. Prepare with [coding practice](timeline.md#coding-interview-practice). Some companies skip this style for take-homes, debugging rounds, or pair programming, so ask. If you want to target employers that say they avoid whiteboard-style rounds, see [hiring-without-whiteboards](https://github.com/poteto/hiring-without-whiteboards) (self-submitted list, so verify each company).

### What interviewers score

Rubrics differ, but many look at roughly these things. Getting the optimal answer is only one of them.

1. **Clarifying questions.** "Can the list be empty?" "Are there duplicates?" "How big can the input get?" Ask before you code.
2. **A simple solution first.** Say the brute-force idea and its cost out loud: "I could check every pair. That's O(n²)." Then improve it.
3. **Talking through your plan.** Explain the approach before typing, so the interviewer can steer you early.
4. **Working code.** Clear names, small helper functions, no half-finished lines.
5. **Testing your own code.** Walk through one normal example and one edge case (empty input, one item) line by line, before they ask.
6. **Recovering when stuck.** Getting stuck is expected. What you do next is scored.
7. **Complexity.** State the time and space cost of your final answer.

**Never go silent.** If stuck, say what you've tried and where it breaks:

> I tried sorting first, but that loses the original positions, which we need. I'm thinking a hash map from value to index might work instead. Can I try that?

Interviewers often give hints, and taking one well counts in your favor.

### One problem, talked through

Problem: given an array of ints and a target, return the indexes of two numbers that add up to the target.

> **Clarify:** "Exactly one answer? Can I use the same element twice? Can the array be empty?"
> **Brute force:** "Check every pair. O(n²) time, O(1) space."
> **Better:** "As I scan, I store each value and its index in a hash map. For each number I check whether `target - number` is already there. One pass, O(n) time, O(n) space."

```java
public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> seen = new HashMap<>(); // value -> index
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (seen.containsKey(need)) {
            return new int[] { seen.get(need), i };
        }
        seen.put(nums[i], i);
    }
    return new int[0]; // no pair found
}
```

> **Test:** "For {2, 7, 11} and target 9: i=0 stores 2. i=1 needs 2, finds it, returns {0, 1}. Empty array: the loop never runs, so it returns an empty array."

That's the whole pattern: clarify, brute force, improve, code, test, state the cost.

**Score yourself** after each mock (0 to 2 each): clarify, simple solution first, plan aloud, code, test your own code, stuck recovery, complexity. Find your lowest line and work on that next. Practicing with someone watching matters: in a small 2020 study of 48 students ([ScienceDaily summary](https://www.sciencedaily.com/releases/2020/07/200714101228.htm)), those interviewed on a whiteboard with an observer performed about half as well as those solving privately. It's one small study, but a good reason to practice with a person watching.

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
- **One tradeoff:** a choice you made and what you gave up.
- **One measurement:** a number. Users, speed, accuracy, time saved, test coverage.
- **What you'd change:** with what you know now.

Example:

```
Project: Shift Swap Board
Problem: Coworkers swapped shifts in a group chat; double-claims happened.
My role: all backend and database; a teammate did the UI.
Architecture: browser -> Java web server -> SQLite; email alerts over SMTP.
Hard bug: two people claimed the same shift. Cause: a race condition.
          Fix: a database transaction plus a unique constraint.
Tradeoff: SQLite is one file and easy to host, but handles many
          simultaneous writers poorly.
Measurement: 9 coworkers used it for 6 weeks; 18 tests.
Would change: add sign-in, move to Postgres.
```

Reread the code before the interview. If you can't explain a part, learn it or take it off your resume.

## AI tools

Using AI tools to build your projects is common, and interviewers know. What they check is whether *you* understand the result. Some companies are now experimenting with letting candidates use AI in coding rounds (Meta piloted it, per press reports), so ask which rules apply to your round. Meta's hiring page now says many of its interviews include an AI assistant built into the interview environment and candidates are expected to use it, and some companies run a round like that at intern and new-grad level too: [a sourced list by company](https://nyrion.ai/companies/interns-and-new-grads).

Be ready for:

- **"Walk me through this function."** Line by line, in your own words.
- **"Why did you do it this way?"** Know the alternatives.
- **"What did the AI get wrong?"** Have a real example: a bug it introduced, an outdated library it suggested, code that worked but was slow. A good answer shows you check its output.

During interviews and online assessments, follow each company's rules for the round you're in. If the rules aren't clear, ask the recruiter before, not after.

## Behavioral

Behavioral questions start with "Tell me about a time..." They're used because past behavior is a decent guide to future behavior. Interviewers typically listen for four things (my summary, not a published rubric): that the story is **specific** (real names, numbers, dates), that **you** did the work, that you can name **what went wrong or what you'd change**, and that you stayed **calm and kind** under pressure.

**Use STAR:** Situation, Task, Action, Result. Spend most of the time on Action. Say "I," not "we." The interviewer is hiring you, not your team.

**Worked example.** "Tell me about a time you had a conflict on a team."

> **Situation:** In my software engineering class, our four-person team was building a web app, and two weeks before the deadline one teammate kept pushing code that broke the main branch.
>
> **Task:** I was in charge of merging, so it was on me to fix the process without making it personal.
>
> **Action:** I asked him to talk one-on-one and found out he didn't know how to run the tests locally. I wrote a one-page setup guide, paired with him for 30 minutes, and set up a rule that pull requests needed one approval and passing tests before merging.
>
> **Result:** We had no more broken merges, shipped on time, and he ended up reviewing more pull requests than anyone. I learned to ask what's going on before assuming someone doesn't care.

**Prepare 5 or 6 stories.** Write each one in STAR form, 4 to 6 sentences, in a table you can reuse:

| # | Story | Action (I...) | Result | Fits questions about |
|---|---|---|---|---|
| 1 | Teammate kept breaking the build | | | conflict, leadership |
| 2 | Missed a deadline at my job | | | mistake, failure |
| 3 | Ran a club event | | | led something, deadline |
| 4 | Learned a framework in 2 weeks | | | learning fast |
| 5 | Angry customer at work | | | conflict, pressure |

- [ ] A team conflict or disagreement
- [ ] A mistake you made and fixed
- [ ] A time you led something
- [ ] A failure, and what you changed after it
- [ ] A tight deadline
- [ ] Learning something new fast

One story can answer several questions. **Your stories don't have to be from tech.** A retail or restaurant job, caregiving, organizing an event, a sports team, or a club all count. Handling an angry customer, keeping a budget, or getting people to show up is real experience. Say what you did and what happened.

## Debugging story template

"Tell me about a hard bug" is one of the most common questions. Fill this in for your best one:

1. **Symptom:** what you saw. ("The app showed the wrong totals, but only for some users.")
2. **First guess, and why it was wrong:** ("I thought it was the math, but the math was fine in tests.")
3. **How you narrowed it down:** logs, print statements, a debugger, a smaller test case, reading the docs. ("I logged the input and saw the bad totals were all from users in a different time zone.")
4. **Root cause:** ("Dates were stored in local time, so orders near midnight landed on the wrong day.")
5. **Fix:** ("I stored everything in UTC and converted only for display.")
6. **What you do differently now:** ("I add a test for time zones on anything with dates.")

## Questions to ask them

Always have questions. "No, you covered everything" sounds uninterested. Pick from these:

- "What does a typical week look like for an intern on this team?"
- "What did a past intern build that you were proud of?"
- "How do interns get feedback, and how often?"
- "What's something you've learned working here that surprised you?"
- "What would make someone really successful in this role in the first month?"

Save pay and time-off questions for the recruiter.

## After the interview

Within 24 hours, send a short note ([template](applying.md#offers)): thank them, name one specific topic you enjoyed, and offer to send anything else.

## Video interview setup

Check this the day before, not five minutes before:

- [ ] Laptop plugged in, notifications off, other apps closed
- [ ] The interview link opens, and the app (Zoom, Teams, Google Meet) is installed and updated
- [ ] Camera at eye level, face lit from the front (a window or lamp facing you, not behind you)
- [ ] Plain background, quiet room; tell roommates or family the time
- [ ] Wired earbuds or a headset, tested with a friend
- [ ] Internet tested; your phone ready as a hotspot backup
- [ ] Recruiter's email or phone number written down in case the call drops
- [ ] Water, paper, a pen, and your defense sheets and STAR stories nearby (don't read from them)

If something breaks mid-call, say so calmly and fix it. It happens to everyone.

## Hardware, embedded, and security interviews

These often have fewer coding problems and more questions about circuits, C, or troubleshooting. Formats vary by company, so ask the recruiter. See "How interviews differ" for each track in [Career tracks](tracks.md).

## Resources

- [Tech Interview Handbook: coding interview techniques](https://www.techinterviewhandbook.org/coding-interview-techniques/): how to approach a problem step by step.
- [Tech Interview Handbook: behavioral interviews](https://www.techinterviewhandbook.org/behavioral-interview/): more on STAR and common questions.
- [Tech Interview Handbook: self introduction](https://www.techinterviewhandbook.org/self-introduction/) and [questions to ask](https://www.techinterviewhandbook.org/final-questions/).
- Java references for checking your work after you try a problem: [NeetCode's solutions repo](https://github.com/neetcode-gh/leetcode) (has a Java folder) and [williamfiset/algorithms](https://github.com/williamfiset/algorithms). Try first, then compare. Don't memorize.
- Behavioral prep list (optional, last updated in 2025): [awesome-behavioral-interviews](https://github.com/ashishps1/awesome-behavioral-interviews).
- Coding practice: [pacing and problem lists](timeline.md#coding-interview-practice). Peer mock interviews: [Pramp](https://www.pramp.com) (check what's free now).
- Your career center: most offer free mock interviews and will review your STAR stories.

Next: [Networking](networking.md)
