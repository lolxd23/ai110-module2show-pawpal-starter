# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design consists of four classes: Owner, Pet, Task, and Scheduler. An Owner has a one-to-many relationship with Pet (one owner can have multiple pets), and each Pet has a one-to-many relationship with Task (one pet can have multiple tasks — feedings, walks, medications, appointments). The Scheduler class is not owned by any single entity; instead it operates across all Task objects system-wide, handling sorting, conflict detection, and recurrence logic. This keeps the data-holding classes (Owner, Pet, Task) separate from the algorithmic logic (Scheduler).
- What classes did you include, and what responsibilities did you assign to each?
Owner is responsible for representing the pet's caretaker — it holds the owner's name and their list of pets, and handles adding new pets and gathering all tasks across every pet they own.
Pet is responsible for representing an individual animal — it holds the pet's name, species, and age along with its list of tasks, and handles adding new tasks to itself and returning its own upcoming tasks.
Task is responsible for representing a single care event (a feeding, walk, medication, or appointment) — it holds the task type, time, recurrence info, priority, and completion status, and handles marking itself complete, checking if it's due today, and checking for conflicts with other tasks.
Scheduler is responsible for the algorithmic logic that spans the whole system — it doesn't hold pet-specific data itself, but instead sorts tasks by priority, detects scheduling conflicts, manages recurring tasks, and generates the "today's tasks" view across all owners and pets.

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
