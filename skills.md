
# SkillForge AI — Practical Skills Framework

## 1. Project Purpose

SkillForge AI helps fresh graduates bridge the gap between academic
knowledge and practical software development.

The platform focuses on hands-on challenges, debugging, testing,
code comprehension, version control, and real-world problem-solving.

AI models provide guidance and explanations, while deterministic
tests and assessment rules evaluate measurable outcomes.

---

## 2. Core Competencies

### Skill 1: Problem Solving

**Goal:** Translate a problem statement into a working solution.

Learners should be able to:
- Understand requirements.
- Identify inputs, outputs, and edge cases.
- Break large problems into smaller steps.
- Choose appropriate algorithms and data structures.

**Assessment:**
- Correctness of the solution.
- Handling of edge cases.
- Clarity of reasoning.

### Skill 2: Debugging

**Goal:** Identify and fix defects systematically.

Learners should be able to:
- Read error messages.
- Trace program execution.
- Identify syntax, type, runtime, and logic errors.
- Verify that a fix does not introduce regressions.

**Assessment:**
- Defects correctly identified.
- Tests passing after the fix.
- Explanation of the root cause.

### Skill 3: Code Comprehension

**Goal:** Understand unfamiliar code before modifying it.

Learners should be able to:
- Explain a function's purpose.
- Trace data flow between functions.
- Identify dependencies.
- Predict behavior for different inputs.

**Assessment:**
- Accuracy of code explanations.
- Correct predictions of program behavior.
- Identification of relevant dependencies.

### Skill 4: Testing

**Goal:** Verify software behavior with meaningful tests.

Learners should be able to:
- Write unit tests.
- Test normal and boundary cases.
- Reproduce reported bugs.
- Understand test failures.

**Assessment:**
- Relevant test cases.
- Correct handling of edge cases.
- Ability to detect known defects.

### Skill 5: Git and Collaboration

**Goal:** Practice common team development workflows.

Learners should be able to:
- Understand commits and branches.
- Review a pull request.
- Explain a code change.
- Resolve simple merge conflicts.
- Write clear commit messages.

**Assessment:**
- Correct workflow decisions.
- Review quality.
- Clarity of change descriptions.

### Skill 6: API Development

**Goal:** Build and troubleshoot simple web APIs.

Learners should be able to:
- Understand HTTP methods and status codes.
- Validate incoming data.
- Return consistent responses.
- Handle common errors.
- Write API tests.

**Assessment:**
- Correct response behavior.
- Input validation.
- Error handling.
- Test results.

### Skill 7: Code Quality

**Goal:** Write readable and maintainable code.

Learners should be able to:
- Use meaningful names.
- Avoid unnecessary duplication.
- Organize code into functions and modules.
- Follow consistent formatting.
- Explain trade-offs in a proposed change.

**Assessment:**
- Readability.
- Maintainability.
- Appropriate modularity.
- Passing automated quality checks.

---

## 3. Difficulty Levels

### Beginner
- Basic functions and conditionals.
- Simple debugging tasks.
- Basic input validation.
- Introductory unit tests.

### Intermediate
- Multiple interacting functions.
- API implementation.
- Dependency and runtime errors.
- Test-driven bug fixing.
- Git branch and review workflows.

### Advanced
- Understanding an unfamiliar codebase.
- Investigating cross-module bugs.
- Refactoring while preserving behavior.
- Reviewing architectural trade-offs.
- Diagnosing failures using logs and tests.

---

## 4. AI Model Responsibilities

### OpenAI

Use OpenAI for:
- Explaining unfamiliar code.
- Generating graduated hints.
- Providing code-review feedback.
- Explaining why an approach may fail.
- Suggesting a personalized practice plan.

OpenAI should encourage independent reasoning rather than
immediately providing complete solutions.

### Gemma

Use the configured local Gemma model for supported tasks such as:
- Classifying common programming errors.
- Categorizing challenges by skill.
- Summarizing error messages.
- Providing lightweight local assistance.

The actual capabilities depend on the selected model checkpoint
and available hardware.

### Deterministic Evaluation Engine

Use normal program logic and automated tests for:
- Running unit tests in a secure environment.
- Checking expected outputs.
- Recording test results.
- Calculating completion statistics.
- Validating required task outcomes.

AI-generated assessments must not replace executable tests
when correctness can be tested directly.

---

## 5. Assessment Rubric

Score each dimension from 0 to 4.

| Score | Meaning |
|---|---|
| 0 | No working attempt or no relevant evidence |
| 1 | Needs substantial guidance |
| 2 | Partially successful; important gaps remain |
| 3 | Meets the task requirements independently |
| 4 | Meets requirements and handles edge cases well |

Assess the following dimensions:

1. Correctness
2. Debugging approach
3. Test quality
4. Code readability
5. Problem-solving and explanation

### Suggested scoring rules

- Correctness should be based primarily on automated tests.
- Test quality should consider meaningful edge cases.
- Readability can use deterministic checks and a documented rubric.
- Problem-solving explanations can be reviewed using a structured rubric.
- Missing evidence should be marked as unassessed rather than
  automatically treated as a lack of ability.

A total score is useful for tracking progress, but it should not
be treated as proof of job readiness.

---

## 6. Personalized Learning Rules

Use assessment results to recommend the next practice activity.

- Repeated debugging failures:
  Recommend error-tracing challenges.
- Weak test coverage:
  Recommend unit-testing exercises.
- Incorrect API responses:
  Recommend HTTP and input-validation challenges.
- Difficulty understanding unfamiliar code:
  Recommend code-reading exercises.
- Repeated Git workflow mistakes:
  Recommend branch and pull-request simulations.

Learners should receive hints before full explanations.

Reassess skills with a different but comparable task to check
whether the learner can transfer the skill to a new problem.

---

## 7. Challenge Format

Every coding challenge should contain:

- Unique challenge ID.
- Title and description.
- Target competency.
- Difficulty level.
- Starter code, if applicable.
- Requirements and constraints.
- Public example tests.
- Hidden test cases.
- Expected behavior.
- Evaluation criteria.
- Optional hints.
- Learning resources.

### Example Challenge

**ID:** DEBUG-001

**Title:** Fix the Addition Function

**Skill:** Debugging

**Difficulty:** Beginner

**Problem:**
The function should return the sum of two numbers, but its
current implementation produces an incorrect result.

**Starter code:**

```python
def add_numbers(a, b):
    return a - b
```

**Expected behavior:**

```python
assert add_numbers(2, 3) == 5
assert add_numbers(-1, 1) == 0
assert add_numbers(0, 0) == 0
```

**Success criteria:**
- The function returns the correct sum.
- All provided tests pass.
- The learner can explain the defect.

---

## 8. Data and Privacy

- Never include API keys in challenge files.
- Do not send private repositories or personal information
  to external models without appropriate permission.
- Use synthetic sample projects for public challenges.
- Keep learner progress separate by learner ID.
- Provide clear explanations of what information is processed
  by cloud models versus local models.

---

## 9. Contribution Guidelines

Contributors can improve SkillForge AI by:
- Adding new coding challenges.
- Creating tests for existing challenges.
- Adding language-specific exercises.
- Improving assessment rubrics.
- Adding debugging scenarios.
- Reviewing AI feedback for accuracy.
- Improving documentation and accessibility.
- Reporting reproducible bugs.

Every new challenge should include a description, competency,
difficulty level, test cases, and expected behavior.

---

## 10. Success Metrics

Measure whether learners improve through:
- Pre-assessment and post-assessment results.
- Success on unseen but comparable tasks.
- Number of defects diagnosed correctly.
- Quality of tests written.
- Ability to explain and review code changes.
- Completion of practical development workflows.

The main goal is improved independent problem-solving,
not simply higher AI usage or more completed exercises.
