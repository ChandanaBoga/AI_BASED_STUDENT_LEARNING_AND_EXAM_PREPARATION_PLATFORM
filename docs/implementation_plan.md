# Semester-Wise Quiz Data Generation & Integration

We are replacing the repetitive 19,000-line `quiz_data.js` with a high-quality, programmatically generated dataset of 1,900 unique questions (50 per subject) across 38 subjects. To circumvent AI token limits and improve maintainability, we are splitting this data into semester-wise JavaScript files.

## User Review Required

> [!IMPORTANT]
> **Data Structure Change**: Instead of a single `quizData` object in a massive file, we are using files named `quiz_sem1.js` through `quiz_sem8.js`. These will be merged at runtime into the main `quizData` object to maintain compatibility with the existing quiz engine.

## Proposed Changes

### Quiz Data Generation [DONE & PENDING]

We use Python scripts to generate validated, unique JSON data for each semester.

#### [NEW] [quiz_sem1.js](file:///c:/Program%20Files/webapp/frontend/assets/quiz_sem1.js) to [quiz_sem8.js](file:///c:/Program%20Files/webapp/frontend/assets/quiz_sem8.js)
- Each file contains a `const quizDataSem[N]` object.
- Exactly 50 questions per subject.
- Subjects are prefixed (e.g., `sem1-c`, `sem2-ds`).

### Frontend Integration

#### [MODIFY] [combined_app.html](file:///c:/Program%20Files/webapp/frontend/combined_app.html)
- Add script tags for all 8 semester files.
- Add a master initialization block to merge all `quizDataSem[N]` into the global `quizData` object used by the search and quiz logic.

#### [DELETE] [quiz_data.js](file:///c:/Program%20Files/webapp/frontend/assets/quiz_data.js)
- Once the semester system is verified, the original repetitive file will be removed.

## Open Questions

- No major open questions. We are following the subject list derived from the existing curriculum.

## Verification Plan

### Automated Tests
- Run each `generate_quiz_sem[N].py` script. The scripts include `assert` statements to verify:
    - Exactly 50 questions per subject.
    - No duplicate question text within a subject.
    - Valid JSON structure.

### Manual Verification
- Verify the "See Before Questions" preview function shows 50 unique questions for various subjects.
- Verify the "Search" functionality in the dashboard correctly identifies subjects across all semesters.
