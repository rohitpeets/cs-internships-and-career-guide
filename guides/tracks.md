# Career Tracks

"CS internship" does not only mean software engineering. This guide covers seven paths, what each one asks for, and how to start. You do not have to choose now. Read the one or two that sound interesting, try a 4-week starter project, and see if you like it. Paces below are suggestions; the job-outlook figures link to their source.

The job board has a page for each track. They are sorted by job title, so a few postings may land in the wrong place.

**A rough look at demand.** The U.S. Bureau of Labor Statistics (BLS) projects growth from 2025 to 2035 of about 10% for software developers, QA analysts and testers (median pay about $134,000 in May 2025), 21% for information security analysts, 35% for data scientists, and 9% for computer hardware engineers. It projects computer support specialists, the usual help-desk job, to shrink about 3%. Projections are estimates and say nothing about how hard any one internship is to land. Use them as one input, next to what you enjoy.

**Quick picker**
- You like building apps and websites: [Software](#software).
- You like code that runs on small devices, like sensors and robots: [Embedded and firmware](#embedded-and-firmware).
- You like how chips and circuits work: [Hardware and chips](#hardware-and-chips).
- You like breaking things to learn how they work: [Security](#security).
- You like fixing computers and networks: [IT and networking](#it-and-networking).
- You like finding patterns in numbers: [Data and ML](#data-and-ml).
- You want a mission-driven job, or a clearance: [Government and defense](#government-and-defense).

**Words used here**
- **CTF:** "capture the flag." A security puzzle contest. You find hidden text (a "flag") by solving challenges.
- **Certification (cert):** a paid exam from a company that proves you know a topic.

**Short on time?** Pick one track and do week 1 of its starter project in an hour a week, for four weeks. Progress counts even if it's slow.

## Software

**The work.** You build and fix apps, websites, and services that run on servers. It is the largest track, so it has the most openings and the most applicants.

**Classes that help.** Data Structures, Algorithms, Databases, Software Engineering.

**4-week starter project.** Build a small web app that stores data, such as a study-group scheduler. Week 1: pick 3 features. Weeks 2 and 3: one feature per week. Week 4: put it online and get 3 people to try it. More in [projects](projects.md).

**Certs.** Skip them. Projects and experience matter more.

**Contests and clubs.** ACM chapter, hackathons, ICPC.

**Job titles to search.** Software Engineer Intern, Software Developer Intern, Web Developer Intern, Backend Intern, Full Stack Intern.

**How interviews commonly differ.** Coding problems on a screen, then a project talk. See [interviews](interviews.md).

Job list: [software track](../track-software.md).

## Embedded and firmware

**The work.** You write code for small computers inside devices: cars, medical tools, drones, appliances. The code is usually C or C++. You work close to the hardware, so you read data sheets and use tools like an oscilloscope.

**Classes that help.** Computer Organization, Operating Systems, Digital Logic, any C or C++ course, Microcontrollers if offered.

**4-week starter project.** Buy a cheap microcontroller board (Arduino or Raspberry Pi Pico, about $10 to $25). Week 1: blink an LED. Week 2: read a sensor. Week 3: show the reading on a screen or send it to your laptop. Week 4: pack it into one small device, like a temperature logger, and film a 1-minute demo. For a map of what to learn after that, see the [Embedded Engineering Roadmap](https://github.com/m3y54m/Embedded-Engineering-Roadmap) (long, so treat it as optional). To read real flight-software code later, [F Prime](https://github.com/nasa/fprime) is NASA's open-source framework. It's advanced, so come back to it after your first board project.

**Certs.** Skip them. A working board on your desk beats a cert.

**Contests and clubs.** Robotics club, your school's IEEE student branch, rocketry or drone clubs.

**Job titles to search.** Embedded Software Intern, Firmware Intern, Embedded Systems Intern, Controls Intern, Test Automation Intern.

**How interviews commonly differ.** Expect C questions: pointers, memory, bits. Be ready to explain a hardware project in detail. Many companies still ask a few standard coding problems too. (This pattern comes from student accounts, not a survey, so ask the recruiter.)

Job list: [embedded track](../track-embedded.md).

## Hardware and chips

**The work.** You help design and test chips and circuit boards. Digital design means describing circuits in a hardware language like Verilog. Verification means proving the design works. Others work on board layout or lab testing.

**Classes that help.** Digital Logic, Computer Architecture, Circuits, an HDL (hardware description language) course.

**4-week starter project.** Free practice on [HDLBits](https://hdlbits.01xz.net/wiki/Main_Page) in Verilog. Week 1: gates and simple logic. Week 2: adders. Week 3: counters and flip-flops. Week 4: a small state machine, such as a traffic-light controller, with a testbench (code that checks your design). [Chipyard](https://github.com/ucb-bar/chipyard) is an open chip-design framework if you want to see how a real one is built, but it's advanced and best after you've done HDL coursework.

**Certs.** Skip them.

**Contests and clubs.** IEEE student branch, robotics club, FPGA or chip-design clubs.

**Job titles to search.** Hardware Engineering Intern, Digital Design Intern, Design Verification Intern, ASIC Intern, FPGA Intern, Electrical Engineering Intern.

**How interviews commonly differ.** Often circuit and logic questions, plus a deep talk about a class or lab project. Fewer LeetCode-style problems.

**Timing.** Many large employers post in late summer and fall. Check each company's student page, and ask your engineering career office about co-op programs.

Job list: [hardware track](../track-hardware.md).

## Security

**The work.** You find weak spots before attackers do, defend networks, or watch for attacks. Entry-level paths: security analyst (watching alerts), application security (reviewing code), and penetration testing (ethical hacking, which many people reach after a few years rather than first). BLS notes that information security analysts often have prior experience in a related job such as IT, so an IT or help-desk job can be a good first step.

**Classes that help.** Networking, Operating Systems, Intro to Security, Linux.

**4-week starter project.** Week 1: learn the Linux command line on [OverTheWire](https://overthewire.org/wargames/). Week 2 and 3: solve 10 beginner challenges on [picoCTF](https://picoctf.org) (free; it's now run under the name CyLab Security Academy). Week 4: write up two of them step by step in a public repo. Writeups show how you think. Next steps: [Juice Shop](https://github.com/juice-shop/juice-shop) is a deliberately insecure web app you run on your own computer to practice (run it locally only, never on a public server). [Awesome CTF](https://github.com/apsdehal/awesome-ctf) is a long list of tools and practice sites, but it hasn't been updated since mid-2024, so some links may be dead.

**Certs.** CompTIA Security+ is a common first one, and I've seen it listed in many government and contractor job posts (check postings in your target area). CompTIA's certification page says V8 is the current version and the English V7 exam retires June 11, 2027. That page doesn't publish a price, but resale and training sites checked in late 2026 consistently list the U.S. voucher at about $439, raised from $425 in mid-2026. Before you pay, look at CompTIA's academic store: it discounts vouchers for students, reportedly by up to half. Renewal costs money too, so treat the voucher as the start, not the total. Pay for it only if you are aiming at those jobs. Skip it if you are mainly applying for software roles.

**Contests and clubs.** [National Cyber League](https://www.nationalcyberleague.org) (online; fall 2026 registration cost $45 and closed in October, so watch for the next season), the Collegiate Cyber Defense Competition ([CCDC](https://www.ccdc.io); schools field a team, so ask your department), CTF clubs.

**Job titles to search.** Security Intern, Cybersecurity Analyst Intern, SOC Analyst Intern, Application Security Intern, Information Security Intern.

**How interviews commonly differ.** Scenario questions: "You see odd traffic on a server. What do you check first?" Networking basics, Linux, and one CTF or lab you can talk about.

**Money.** The CyberAI Scholarship for Service (formerly CyberCorps: Scholarship for Service) pays tuition and a stipend for cybersecurity students, in exchange for government work after. NSF's current call lists U.S. citizens and permanent residents, and your school must take part. Federal hiring was disrupted in 2025 (see [Government and defense](#government-and-defense)) and some scholars reported rescinded offers, so read the current terms before you commit.

Job list: [security track](../track-security.md).

## IT and networking

**The work.** You keep an organization's computers, accounts, and networks running. Every company has an IT team, so these jobs exist in every city. It is a good way to get paid experience early, and many people move into cloud, security, or software from here. Think of it as a stepping stone: BLS projects computer support specialist jobs to shrink about 3% through 2035, so plan to grow into systems, cloud, or security.

**Classes that help.** Networking, Operating Systems, Databases, Systems Administration.

**4-week starter project.** Build a home lab. Week 1: install Linux in a virtual machine. Week 2: set up a file server and two user accounts. Week 3: set up a small network in a free simulator such as Cisco Packet Tracer. Week 4: write a 1-page runbook (steps for fixing common problems). For more things to run on your lab, see [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) and [awesome-sysadmin](https://github.com/awesome-foss/awesome-sysadmin).

**Certs.** More useful here than in other tracks. CompTIA A+ (basics) and Network+ help for help-desk jobs. CCNA (Cisco's networking cert) lists at US$300 for the exam on Cisco's page. It's valid for three years; renew by retaking the exam or earning CE credits before it expires. Take one only after you have seen the topic in class or in your lab, and ask your department if it offers discounts.

**Contests and clubs.** Cyber defense teams, IT or networking clubs, campus IT help desk (a paid student job).

**Job titles to search.** IT Intern, Help Desk Technician, Systems Administrator Intern, Network Engineer Intern, Cloud Support Intern, Technical Support Intern.

**How interviews commonly differ.** Troubleshooting questions ("a user can't connect, what do you do?") and customer-service skills matter as much as coding.

Job list: [IT track](../track-it.md).

## Data and ML

**The work.** You clean data, find patterns, build charts, and sometimes train models. Titles run from data analyst (spreadsheets, SQL, charts) to machine learning engineer (code and models). Analyst roles are easier to land first.

**Classes that help.** Statistics, Databases, Linear Algebra, Data Structures, any Python data course.

**4-week starter project.** Pick a public data set about something you care about. Week 1: load it and clean it (Python's pandas is common; you can also do it in Java or SQL). Week 2: answer 3 questions with SQL or pandas. Week 3: make 3 clear charts. Week 4: write a 1-page summary of what you found, and what you are not sure about. Two free courses to follow: [Data Science for Beginners](https://github.com/microsoft/Data-Science-For-Beginners) (10 weeks) and [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) (9 weeks, self-paced; a certificate needs a live cohort).

**Certs.** Skip them at first. A project with a clear write-up counts more.

**Contests and clubs.** Data science club, ACM, campus research groups, hackathons with data themes.

**Job titles to search.** Data Analyst Intern, Data Science Intern, Machine Learning Intern, Business Intelligence Intern, Data Engineering Intern.

**How interviews commonly differ.** SQL questions, basic statistics, and "walk me through a data project." Machine learning roles add model questions. See [interviews](interviews.md).

Job list: [data track](../track-data.md).

## Government and defense

**The work.** Federal agencies, national labs, and defense contractors hire for software, cyber, embedded, data, and engineering. Many jobs need U.S. citizenship, and some need a security clearance.

**Classes that help.** The same as the track you want, such as Networking for cyber or Digital Logic for hardware.

**4-week starter project.** Week 1: make a [USAJOBS](https://www.usajobs.gov) account and save a search. Week 2: read 5 student postings and write down what they ask for. Week 3: check your resume against them. Week 4: apply to one program, or ask your career office which employers recruit on campus.

**Certs.** Security+ can help for cyber jobs. Skip it otherwise.

**Contests and clubs.** National Cyber League, CCDC, IEEE student branch, [IEEEXtreme](https://ieeextreme.org) (a 24-hour team programming contest; its site says IEEE student membership is required, and the 2026 edition was October 31).

**Job titles to search.** Pathways Intern, Student Trainee, Cyber Intern, Software Engineer Intern with "defense," "aerospace," or "national lab" in the company name.

**How interviews commonly differ.** Often a panel or a phone interview with a manager, plus questions about teamwork and following rules. Honest answers on forms matter a lot.

**Timing and risk.** These jobs often open in the fall, partly because clearances take months. Do not wait for spring. Also know that federal student hiring was disrupted in early 2025: the State Department canceled its Pathways internship program, per [The Nation](https://www.thenation.com/article/politics/trump-hiring-freeze-public-service-workers-internships/), the freeze was later rescinded, and an executive order that February began ending the Presidential Management Fellows program, according to the [GAO](https://www.gao.gov/products/GAO-25-106658). The GAO also reported Pathways hiring had already fallen 64% since fiscal 2013. Keep a second option open. The SMART scholarship is another route (full tuition, stipends, and a job after graduation, per its site, which names the Department of War); I couldn't read its eligibility rules there, so check them.

Job list: [government track](../track-gov.md).

## Resources

- Practice sites and courses for data, hardware and security: [resources by situation](resources.md#by-situation).
- [USAJOBS](https://www.usajobs.gov): federal job search.

Next: [GitHub](github.md)
