# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design includes four classes: Owner, Pet, Task, and Schedule.

- **Owner** represents the pet owner and stores their contact info, available time for daily pet care, and lists of current and favorite pets. It provides methods to manage pets and update contact details.
- **Pet** represents an individual pet with a species and dietary preferences, linked to its owner.
- **Task** represents a single pet care activity (e.g., walking, feeding, grooming) with a duration, time, priority level (HIGH, MEDIUM, LOW), and completion status.
- **Schedule** holds a priority-sorted list of tasks and a total time tracker. Its core responsibility is generating a daily plan via `generate_schedule()`, which takes a list of tasks and the owner's available time, then produces an optimized schedule that fits within the time constraint.

The relationships are: an Owner owns many Pets (1-to-many), a Pet has many Tasks (1-to-many), an Owner has one Schedule (1-to-1), and a Schedule contains many Tasks (1-to-many).


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
Design brainstorming, making plantUML, install VSCode extensions
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
