# Your First Resume

A resume is a one-page summary of what you've done. A recruiter spends a few seconds on it, so it has to be clean and easy to scan. You don't need an internship to make a good one.

## The rules

- **One page.** Always, until you have years of full-time work.
- **Plain layout.** One column, one font, black text. No photo, icons, skill bars, or tables.
- **Contact info in the body, not the header/footer area.** In Word or Google Docs, the header and footer are separate zones that some resume-reading software (an ATS, applicant tracking system) skips. Type your name and contact line as normal text at the top of the page.
- **Standard section names:** Education, Projects, Experience, Leadership and Activities, Skills. Software and recruiters both look for these words.
- **No objective or summary** at this stage. It takes space and says little. Your projects say more.
- **Working links.** Write them out short (`github.com/your-name`), and click every one in the PDF before you send it. Point project links to the repo or live demo, not your profile.
- **Save as PDF.** Name it `FirstName_LastName_Resume.pdf`. Copy all the text out of the PDF and paste it into a plain text file. If it comes out jumbled, the software sees it jumbled too.
- **Professional email.** Your name, not a nickname.
- **Update dates every term:** expected graduation, "Present" on current roles, classes in progress, new GPA.

## Sections, in order

1. **Header:** name, city and state, phone, email, LinkedIn, GitHub.
2. **Education:** school, degree and major, expected graduation (month and year), GPA if 3.0 or higher, honors, 4 to 6 relevant classes.
3. **Projects:** your best 2 or 3. This is the main section when you have no internship.
4. **Experience:** any job counts: retail, food service, campus jobs, caregiving, a family business. It shows you show up and handle responsibility.
5. **Leadership and activities:** club roles, competitions, hackathons, tutoring, volunteering, events you organized.
6. **Skills:** only what you have really used, grouped:

```
Languages: Java, Python, C, SQL
Tools: Git, Linux, VS Code, Flask, MySQL
```

Leave out soft skills ("teamwork") and anything you've only watched a video about.

## Bullet formula (XYZ)

Write each bullet as: **Accomplished X, measured by Y, by doing Z.** Start with a strong verb (Built, Cut, Organized, Trained, Fixed, Wrote, Led).

- **Project:** "Cut study-planner page load from about 4 s to under 1 s (measured in Chrome DevTools) by caching course data instead of calling the API on every page."
- **Club:** "Grew weekly workshop attendance from about 10 to 30 by moving sessions right after intro CS labs and posting in class Discord servers."
- **Food service:** "Trained 5 new hires on the register and drive-thru headset during the holiday rush, cutting the time the manager spent on training."
- **Caregiving:** "Managed medications and 6+ appointments a week for a family member by setting up a shared calendar and checklist the family still uses."
- **Family business:** "Cut weekly inventory counting from about 6 hours to 2 by building a Google Sheets tracker with barcode-scanner input for the family store."

Good numbers: real users, tests written, time or money saved, response time, records handled, people trained or led. Lines of code is not a good number.

**No number? Say what it does and how you tested it.** "Built a shift-swap web app with sign-in, email alerts, and 18 unit tests for the claim logic." That's honest and specific.

**Never invent a number.** Interviewers ask "how did you measure that?" If you guessed, you're stuck. Use "about" only for numbers you really estimated from something real.

Use 2 to 4 bullets per item.

## Sample resume

A fictional sophomore with no internship. This is what "good enough to get interviews" looks like at this stage: real, specific, not inflated.

```
JORDAN LEE
Anytown, TX | (555) 555-0142 | jordan.lee@email.com | linkedin.com/in/jordan-lee | github.com/jordan-lee

EDUCATION
State University, Anytown, TX                                              Expected May 2029
B.S. in Computer Science | GPA: 3.4/4.0 | Dean's List (Fall 2025)
Relevant courses: Data Structures (in progress), Discrete Math, Computer Organization, Intro to Java

PROJECTS
Shift Swap Board | Python, Flask, SQLite                           github.com/jordan-lee/shift-swap
- Built a web app where coworkers post and claim open shifts; 9 coworkers used it for 6 weeks
  in place of a group text thread
- Fixed a bug that let two people claim the same shift by adding a database lock, then wrote
  18 pytest tests for the claim logic
Bus Arrival Display | C++, ESP32, LCD                              github.com/jordan-lee/bus-display
- Built a desk display that shows the next two campus bus times from the city's public transit feed
- Cached results and refreshed every 30 s instead of every 5 s to stay under the feed's rate limit

EXPERIENCE
Sales Associate, Main Street Hardware, Anytown, TX                                 Jun 2024 - Present
- Work 20 hours a week during the school year while taking a full course load
- Trained 4 new hires on the register and returns process during the 2025 holiday season
- Close the store 2 nights a week: balance the register and count high-value inventory

LEADERSHIP AND ACTIVITIES
Events Coordinator, Computing Club                                               Aug 2025 - Present
- Organized 5 workshops (Git basics, Linux, resume night) with 25 to 40 attendees each; booked
  rooms and recruited 3 upperclassmen to teach

SKILLS
Languages: Python, Java, C++, SQL, HTML/CSS
Tools: Git, GitHub, Flask, SQLite, Linux command line, VS Code, Arduino IDE
```

## Education edge cases

- **Transfer students:** list the four-year school you attend now first. Add the community college below it only if it helps (an associate degree, honors, or relevant classes). Example:
  ```
  State University, Anytown, TX — B.S. Computer Science, Expected May 2028
  Anytown Community College — A.S. Computer Science, May 2026 | Phi Theta Kappa
  ```
- **Which GPA?** Applications usually mean your current school's overall GPA. If your major GPA is much stronger, you can list both, labeled: "Major GPA: 3.6 | Overall: 3.1." If you just transferred and have no GPA yet at the new school, leave it off or use your community college GPA, labeled with that school.
- **Honors:** Dean's List (with terms), President's List, Phi Theta Kappa (the community college honor society), scholarships. One line in Education is enough.
- **Below 3.0?** Leave GPA off. Some applications will ask; answer honestly there.
- **Took time off or changed majors?** Just list the degree and expected date. You don't need to explain gaps on the page.

## Experience that isn't an internship

All of these go under Experience and count:

- **Research with a professor.** Ask one whose class you did well in; a few hours a week is a normal start. "Undergraduate Research Assistant" is a real title.
- **Structured programs with code review.** Free or paid courses and fellowships where someone reviews your pull requests give you real teamwork stories (merge conflicts, review feedback).
- **Campus jobs:** IT help desk, lab assistant, library tech, web assistant for a department.
- **TA, grader, or tutor** for a CS or math class.
- **Short company projects:** [Forage](https://www.theforage.com) has free, self-paced job simulations from companies (list them under Projects or Certificates, not as a job). [Parker Dewey](https://www.parkerdewey.com) posts short paid "micro-internships" for students. [Extern](https://www.extern.com) offers remote project-based externships with a paid monthly membership after a short free trial; check the current price before you sign up.

## Tailor it

Tailor carefully for your top 10 to 15 applications. Send a solid general version to the rest.

1. Paste the job posting into a doc.
2. Highlight every tool, language, and skill it names (for example: Java, REST APIs, SQL, Linux, unit testing).
3. For each one you have **really used**, make sure the posting's exact words appear on your resume ("REST API," not just "backend"). Put them in Skills and in a bullet that shows where you used it.
4. Move your most relevant project to the top of Projects.
5. Skip anything you haven't used. Interviewers will ask about every word.

## Keep it current

Keep a private **master file** (a Google Doc is fine). It lists everything you've done, with more detail than any one resume:

- Every project, job, club role, and class project.
- For each: dates, tools used, links, and real numbers (users, tests, time saved) with how you got each number.
- All the bullets you've ever written for it.

Build each resume by copying the best pieces from the master file. **Add to it the week you finish something**, while you still remember the details and numbers. This also makes LinkedIn and interview prep much faster.

## Resume audit

Run this before you send a resume anywhere. Every answer should be "yes."

1. Is it one page, one column, with contact info typed in the body (not the header/footer area)?
2. Does the text copy cleanly out of the PDF?
3. Does every bullet start with a strong verb?
4. Does every bullet say what you did **and** a result or how it was tested?
5. Is every number true, and could you explain how you got it?
6. Are projects above anything less relevant, with your best one first?
7. Is every skill something you could answer a question about?
8. Do all links open the right page (repo or demo, not a 404)?
9. Are dates, graduation date, and GPA current for this term?
10. Has someone else read it for typos in the last month?

**Teardown: three weak bullets, fixed**

| Before | Problem | After |
|---|---|---|
| "Worked on a website for a class." | No verb, no detail, no result. | "Built a course-review site in React and Node.js with a 3-person team; wrote the search API and its 12 tests." |
| "Responsible for helping customers." | Duty, not an accomplishment. | "Resolved about 30 customer questions per shift at the service desk, including returns and special orders." |
| "Used Python, Java, C++, SQL, AWS, Docker, and Kubernetes." | A list of tools in a bullet; some never really used. | Move real tools to Skills. Replace with: "Wrote a Python script that cleaned 3 years of club attendance data from 9 spreadsheets into one SQLite database." |

## Get it reviewed

- **Your career center.** Free, and they know what local employers want. Book a resume review.
- **An upperclassman who has interned.** Ask: "What would make you skip this resume?"
- **An AI tool, only as a second opinion.** It can catch weak verbs and typos. Check every line it changes: it may add numbers, skills, or claims that aren't true, and you're the one who'll be asked about them.

## Tools

- **Google Docs or Word** with a plain one-column template is all you need.
- **Optional:** the "Jake's Resume" template on [Overleaf](https://www.overleaf.com), a free LaTeX template many CS students use.

## Resources

- [Tech Interview Handbook: resume guide](https://www.techinterviewhandbook.org/resume/)
- [Jake's Resume template (Overleaf)](https://www.overleaf.com/latex/templates/jakes-resume/syzfjbzwjncs) (optional, LaTeX)
- [Forage](https://www.theforage.com): free virtual job simulations.
- [Parker Dewey](https://www.parkerdewey.com): short paid micro-internships.
- [Extern](https://www.extern.com): remote externships; paid membership after a free trial.
- Need project material first? See [projects](projects.md).

Next: [start applying](applying.md).
