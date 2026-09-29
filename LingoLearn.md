# LingoLearn — Complete Native iOS Vocabulary Learning App

Build a complete, production-quality native iOS vocabulary-learning application called **LingoLearn**.

The final project must open directly in Xcode, compile successfully, run on a real iPhone or simulator, include meaningful bundled vocabulary data, implement all major user flows, and contain sufficient automated tests.

This is not a UI mockup or prototype. Build the application as a complete working product.

You are responsible for making the appropriate technical decisions yourself, including:

* application architecture;
* data modeling;
* persistence strategy;
* state management;
* navigation architecture;
* concurrency design;
* module boundaries;
* reusable component strategy;
* project organization;
* caching;
* search implementation;
* background work;
* testing architecture.

Do not wait for me to design these parts for you.

Choose solutions that are idiomatic, maintainable, scalable, and appropriate for a modern native iOS application.

---

# 1. Core Platform Requirements

Build a native iOS application targeting:

* iOS 17.0+
* iPhone as the primary device
* iPad with an appropriately adaptive interface

Prefer modern Apple-native technologies and APIs.

The application should:

* use native Swift / SwiftUI;
* avoid unnecessary third-party dependencies;
* work fully offline for its core functionality;
* store all learning data locally;
* optionally support iCloud synchronization;
* support Light and Dark Mode;
* support localization;
* support Dynamic Type and VoiceOver;
* follow modern Apple Human Interface Guidelines.

There must be no analytics, advertising, tracking, or unnecessary external network requests.

If iCloud Sync is enabled by the user, Apple iCloud communication is allowed.

---

# 2. Product Goal

LingoLearn should provide a complete vocabulary-learning workflow covering:

1. vocabulary books;
2. daily learning;
3. spaced repetition;
4. quizzes;
5. pronunciation;
6. search;
7. favorites;
8. mistake review;
9. statistics;
10. streaks;
11. achievements;
12. reminders;
13. widgets;
14. Siri / App Intents;
15. Spotlight integration;
16. import, export, backup, and restore.

The experience should feel like a polished consumer learning app rather than a technical demo.

---

# 3. First-Launch Onboarding

Create a polished first-launch onboarding experience.

Include three introductory pages explaining the application's main benefits.

Users should be able to skip the introductory pages.

During onboarding, allow the user to:

* choose an initial vocabulary book;
* set a daily learning goal;
* optionally complete a vocabulary-level assessment;
* enable study reminders.

Default vocabulary book:

**CET4**

Default daily goal:

**20 words**

## Optional vocabulary assessment

Sample approximately 40 words from multiple difficulty levels.

For each word, allow the user to indicate:

* Know
* Don't Know

Use the result to provide a rough vocabulary estimate and recommend an appropriate vocabulary book.

Clearly treat this as an in-app estimate rather than a standardized linguistic test.

Explain notification benefits before asking for notification permission.

After onboarding is completed, it should not automatically appear again.

Provide an option in Settings to view onboarding again.

---

# 4. Home

Create a useful and visually polished Home screen.

Include:

## Daily progress

Show a circular progress indicator displaying:

* today's completed learning;
* daily goal.

Show new words and reviewed words separately.

## Study streak

Display:

* current streak;
* flame indicator;
* remaining Streak Freeze availability.

Provide one Streak Freeze per calendar month.

If the user misses one eligible study day, automatically consume the freeze rather than immediately breaking the streak.

Unused monthly freezes should not accumulate indefinitely.

## Reviews due

Show the number of vocabulary words currently due for review.

Keep this value visually consistent across relevant Home and navigation elements.

## Current vocabulary book

Show:

* book name;
* progress;
* estimated completion date.

Allow opening the full book page.

## Word of the Day

Display a randomly selected unlearned word.

Allow opening its detail page.

## Quick actions

Provide:

* Start Learning
* Quick Review
* Random Quiz

## Daily goal celebration

When the user reaches the daily goal for the first time that day:

* show a full-screen celebration;
* use appropriate haptic feedback;
* evaluate newly unlocked achievements.

The celebration should not repeatedly appear every time the Home screen opens.

## Empty states

Provide carefully designed empty states for cases such as:

* no vocabulary books;
* vocabulary book fully completed;
* no reviews currently due.

Each empty state should explain the situation and provide an appropriate next action.

---

# 5. Vocabulary Books

Include built-in vocabulary books for at least:

* CET4
* CET6

Each book should display:

* total words;
* learned words;
* mastered words;
* overall progress.

Users must also be able to create custom vocabulary books.

Support:

* create;
* rename;
* delete;
* add words manually;
* edit custom words;
* import vocabulary;
* export vocabulary.

Deletion must require confirmation.

Manual word creation should support all information necessary for a useful vocabulary-learning experience, including at minimum:

* spelling;
* definitions.

Allow importing vocabulary files from:

* JSON
* CSV

The import experience should:

* validate data;
* detect duplicates;
* continue importing valid rows where reasonable;
* clearly report invalid data.

Allow exporting:

* individual vocabulary books;
* learning records.

Users should be able to switch the current active vocabulary book.

Progress for each vocabulary book must be preserved independently.

## Vocabulary book detail

Provide:

* full word list;
* search;
* sorting;
* filtering;
* bulk actions.

Useful sorting and filtering options should include:

* learning status;
* alphabetical order;
* date added.

Bulk actions should include:

* mark as mastered;
* reset learning progress;
* add to favorites.

Destructive operations require confirmation.

---

# 6. Learning Sessions

The main learning experience should use card-based vocabulary learning.

Allow the user to configure the number of cards per group:

**5–30**

Default:

**10**

## Start Learning

Mix:

* new vocabulary;
* currently due review vocabulary.

Default new-word-to-review ratio:

**1:2**

Allow this ratio to be changed in Settings.

## Quick Review

Quick Review should contain only words currently due for review.

## Session progress

Show:

* current card number;
* total cards;
* progress indicator;
* close control.

If the user exits an unfinished session:

* ask for confirmation;
* preserve already completed progress.

If the application is terminated during a learning group, the user should be able to resume the unfinished group later.

---

# 7. Learning Card

## Front side

Show:

* English word;
* pronunciation;
* part of speech;
* audio button.

Provide a Hint action.

Hints may include:

* first letter;
* partially obscured definition.

## Back side

Show:

* Chinese definitions;
* example sentences;
* Chinese translations;
* highlighted target word;
* pronunciation for example sentences;
* synonym summary;
* antonym summary;
* View Details action.

Tapping the card should provide a polished card-flip experience.

Respect the system Reduce Motion setting.

When Reduce Motion is enabled, replace strong 3D transitions with a subtle fade or equivalent accessible transition.

---

# 8. Learning Gestures

Support:

* swipe right → Know;
* swipe left → Don't Know;
* swipe up → Favorite;
* swipe down → Skip.

Skip should not count as an answer.

A skipped card should appear again later in the same learning group.

During swiping:

* move the card naturally with the gesture;
* provide directional visual feedback;
* show the relevant action label;
* provide haptic feedback after crossing the action threshold.

Suggested semantic colors:

* Know → green;
* Don't Know → red;
* Favorite → yellow.

Do not rely exclusively on color.

Provide visible buttons that perform the same actions so the app remains accessible and practical for one-handed use.

Also provide:

* Undo previous action.

Long-pressing a card should open the full word detail view.

---

# 9. Pronunciation

Use native system speech capabilities.

Support:

* American English;
* British English;
* adjustable speech speed.

Allow automatic pronunciation when a learning card appears.

This option must be configurable.

Allow replaying pronunciation at any time.

Example sentences should also support pronunciation.

Gracefully handle unavailable system voices.

---

# 10. End-of-Group Summary

After completing a learning group, show a summary including:

* known words;
* unknown words;
* time spent;
* newly favorited words;
* unknown-word list.

Provide actions such as:

* Review Unknown Words
* Another Group
* Finish

Words marked Don't Know should appear again at least once during the current learning round before they are considered complete.

---

# 11. Word Detail

Create a complete vocabulary detail page.

Include information such as:

* spelling;
* American pronunciation;
* British pronunciation;
* part of speech;
* Chinese definitions;
* English definition;
* example sentences;
* translations;
* synonyms;
* antonyms;
* roots / affixes;
* inflections;
* mnemonic information.

Allow example sentences to be pronounced.

Where appropriate, synonyms and antonyms should be tappable and open the corresponding vocabulary entry.

## Learning information

Display:

* current learning status;
* next review date;
* review count;
* learning accuracy.

## Actions

Allow:

* Favorite
* Unfavorite
* Add Note
* Edit Note
* Mark as Mastered
* Reset Progress
* Pronounce

Resetting progress requires confirmation.

## Sharing

Allow generating a visually attractive vocabulary card image and sharing it through the native iOS sharing interface.

---

# 12. Spaced Repetition

Implement an SM-2-style spaced-repetition system.

Initial values:

* Easiness Factor = 2.5
* interval = 0
* repetitions = 0

Use the following quality mapping:

Learning cards:

* Don't Know → q = 1
* Know → q = 4

Quiz:

* incorrect → q = 1
* correct → q = 4
* correct within 3 seconds → q = 5

For q < 3:

* reset repetitions;
* schedule short-term relearning;
* ensure the word appears again during the current day's relearning flow.

For q >= 3:

* first successful interval → 1 day;
* second successful interval → 6 days;
* later intervals → previous interval × Easiness Factor.

Use the standard SM-2 Easiness Factor formula:

`EF' = EF + (0.1 - (5 - q) × (0.08 + (5 - q) × 0.02))`

Minimum EF:

`1.3`

Review dates should behave correctly according to the user's local calendar and timezone.

## Learning states

Support meaningful states equivalent to:

* New
* Learning
* Reviewing
* Mastered

A word should become Mastered after:

* reaching an interval of at least 21 days;
* achieving at least three consecutive successful reviews.

An incorrect answer should return the word to an appropriate learning/relearning state.

## Review ordering

Prioritize:

1. most overdue;
2. due today;
3. optional early reviews.

Allow the user to configure a daily review limit.

## Review history

Provide a useful visual representation of a word's memory/review history using charts.

The scheduling algorithm should be designed so that it is deterministic and thoroughly unit-testable.

---

# 13. Quiz Modes

Provide the following quiz types:

1. English → Chinese multiple choice
2. Chinese → English multiple choice
3. Spelling input
4. Listening multiple choice
5. Dictation
6. Sentence cloze
7. Matching

Users may select a specific quiz type or a randomized Mixed Mode.

---

# 14. Quiz Scope

Allow quizzes based on:

* all words in the current vocabulary book;
* learned words;
* Mistake Book;
* Favorites.

Allow question counts:

* 10
* 20
* 50

If there are insufficient words, degrade gracefully rather than failing.

---

# 15. Multiple Choice

## English → Chinese

Display one English word and four Chinese definitions.

Exactly one answer must be valid.

## Chinese → English

Display one definition and four English words.

Exactly one answer must be valid.

Distractors should preferably come from:

* the same vocabulary book;
* the same part of speech where possible.

Avoid:

* duplicate choices;
* synonyms that create multiple defensible answers;
* ambiguous choices;
* accidentally including the correct answer twice.

Randomize answer positions.

---

# 16. Spelling

Display a Chinese definition.

Allow the user to type the English word.

Support:

* first-letter hint;
* case-insensitive matching;
* ignored leading/trailing whitespace.

---

# 17. Listening

Play pronunciation.

Provide four English word options.

---

# 18. Dictation

Play pronunciation.

Allow the user to type the word.

---

# 19. Sentence Cloze

Display an example sentence with the target word removed.

Provide four possible answers.

---

# 20. Matching

Display:

* five words;
* five definitions.

Allow users to match them through a natural touch interaction.

---

# 21. Quiz Interaction

Provide a configurable per-question time limit:

**5–30 seconds**

Show a countdown indicator.

Timeout counts as incorrect.

## Correct answer

Provide:

* success icon;
* subtle animation;
* haptic feedback.

## Incorrect answer

Provide:

* error icon;
* appropriate feedback;
* correct answer;
* haptic feedback.

Then allow the user to continue.

Respect Reduce Motion.

Every quiz result must contribute to the spaced-repetition system.

---

# 22. Quiz Results

After the quiz, show:

* accuracy;
* total duration;
* average time per question;
* incorrect-word list.

Incorrect words should support:

* viewing definitions;
* pronunciation;
* adding to Favorites.

Provide actions:

* Retry Incorrect
* Try Again
* Return

---

# 23. Quiz History

Store quiz history.

Provide a history screen showing previous sessions.

Users should be able to open a session and inspect its detailed results.

Historical results must remain historically accurate even if vocabulary content is later edited.

---

# 24. Mistake Book

Words answered incorrectly during quizzes should automatically appear in a Mistake Book.

After a word has been answered correctly three consecutive times following its latest incorrect answer, automatically remove it from the Mistake Book.

Another incorrect answer resets this streak.

Users must also be able to manually remove items.

Support:

* sorting;
* filtering;
* targeted quizzes;
* export.

---

# 25. Favorites

Favorites may be created from:

* learning-card gesture;
* Word Detail.

Provide:

* Favorite list;
* sorting;
* filtering;
* bulk removal;
* targeted quizzes;
* export.

---

# 26. Learning Statistics

Create a dedicated Statistics / Progress tab.

Provide:

## Learning-volume chart

Ranges:

* last 7 days;
* last 30 days;
* last 90 days.

Show:

* new vocabulary;
* reviewed vocabulary.

## Calendar heatmap

Display approximately the last 12 weeks of study activity in a GitHub-contribution-style heatmap.

Tapping a date should reveal that day's details.

## Vocabulary mastery distribution

Visualize:

* New
* Learning
* Reviewing
* Mastered

## Weekly learning time

Show a weekly time chart.

## Review accuracy

Show accuracy trends over time.

## Key metrics

Display:

* total study days;
* total learned words;
* longest streak;
* average words per active day;
* estimated completion date.

---

# 27. Weekly Report

Generate a summary for the previous week.

Include:

* words learned;
* words reviewed;
* quizzes completed;
* quiz accuracy;
* total study time;
* streak.

The report should become available every Monday.

If the application was not opened on Monday, generate it the next time the user launches the application.

Allow creating a shareable report image.

---

# 28. Achievements

Implement at least 15 achievements.

Include achievements equivalent to:

* First Study Session
* 3-Day Streak
* 7-Day Streak
* 30-Day Streak
* 100-Day Streak
* Master 50 Words
* Master 100 Words
* Master 500 Words
* Perfect Quiz
* Complete 50 Quizzes
* Favorite 20 Words
* Study for 10 Hours
* Complete a Vocabulary Book
* Night Owl — study after 23:00
* Early Bird — study before 07:00

Show locked achievements in a visually subdued state with visible progress.

When an achievement unlocks:

* show a polished celebration;
* display the badge prominently;
* provide haptic feedback.

Respect Reduce Motion.

Achievements must never unlock multiple times accidentally.

---

# 29. Search

Provide global vocabulary search.

Make it accessible from:

* vocabulary book screens;
* Home.

Search:

* English spelling;
* Chinese definitions.

Support:

* prefix matching;
* substring matching;
* typo tolerance with edit distance up to approximately 2 characters.

Store the latest 10 search queries.

Allow clearing search history.

Search results should display:

* word;
* vocabulary book;
* learning status.

Tap a result to open Word Detail.

---

# 30. Settings

Create a complete Settings tab.

## Learning

Allow configuring:

* daily goal: 10–100;
* cards per group: 5–30;
* new-word / review ratio;
* daily review limit;
* default quiz type;
* default time limit per question.

## Reminders

Provide:

* daily learning reminder;
* reminder time;
* review-due reminder;
* streak warning.

At approximately 21:00 local time, if the user has not studied that day and streak warnings are enabled, send an appropriate local notification.

## Pronunciation

Allow:

* American English;
* British English;
* speech rate;
* automatic pronunciation.

## Feedback and Appearance

Allow:

* sound effects on/off;
* haptics on/off;
* System / Light / Dark appearance;
* application-level text-size adjustment while continuing to respect Dynamic Type.

## Data

Provide:

* iCloud Sync;
* backup;
* restore;
* reset learning progress;
* clear temporary/cache data.

Backup the user's meaningful application data.

Restore should require confirmation before replacing or merging existing data.

Resetting learning progress should require strong confirmation.

Clearing cache must never remove learning data, notes, Favorites, vocabulary books, or settings.

## About

Display:

* app version;
* privacy information;
* open-source acknowledgements if applicable;
* View Onboarding Again.

---

# 31. Widgets

Provide WidgetKit widgets.

## Small

Show:

* today's progress ring;
* streak.

## Medium

Show:

* Word of the Day;
* pronunciation;
* one definition;
* daily progress.

## Large

Show:

* progress;
* reviews due;
* weekly activity visualization.

Widget taps should deep-link into the appropriate app screen.

Refresh widgets when important learning data changes and around the transition to a new day.

---

# 32. Siri / App Intents

Provide useful system actions equivalent to:

* Start Learning
* Start Review
* How Many Words Did I Study Today?
* Look Up Word `{word}`

These actions should integrate naturally with the app's flows.

---

# 33. Spotlight

Index vocabulary so users can search for words through iOS Spotlight.

Include:

* spelling;
* definition.

Selecting a result should open the appropriate Word Detail screen.

Keep indexed vocabulary synchronized with user-created and imported content.

---

# 34. Local Notifications

Support:

* daily reminder;
* review-due reminder;
* streak warning.

Provide an action such as:

**Study Now**

Opening the notification should take the user directly to the relevant learning flow.

---

# 35. Visual Design

Use a modern, friendly vocabulary-learning visual language.

Primary color:

`#0EA5E9`

Secondary color:

`#14B8A6`

Semantic colors:

* Success: `#22C55E`
* Error: `#EF4444`
* Warning: `#F59E0B`

Create a consistent design system covering:

* spacing;
* corner radius;
* typography;
* shadows;
* semantic colors;
* animation behavior.

The interface should feel polished and cohesive rather than like independent demo screens.

Use reusable components where appropriate.

Create a custom App Icon and launch experience.

Support Light and Dark Mode throughout the entire application.

---

# 36. UI States

Every important screen should appropriately handle:

* normal state;
* loading state;
* empty state;
* error state.

Empty states should include:

* icon or illustration;
* useful explanation;
* appropriate next action.

Errors should explain what happened and provide Retry when retry is meaningful.

---

# 37. Accessibility

Accessibility is a core requirement.

Fully support Dynamic Type.

At large accessibility text sizes:

* text must remain readable;
* important content must not be clipped;
* controls must remain accessible;
* layouts may reflow or scroll.

Provide appropriate VoiceOver information for interactive elements.

Any gesture-only feature must have an equivalent accessible control.

Respect:

**Reduce Motion**

When enabled, replace or disable:

* 3D card rotation;
* shake effects;
* large confetti motion;
* aggressive achievement animations.

Use simpler transitions such as fades.

Correct/incorrect feedback must not depend only on color.

Combine:

* color;
* icon;
* text;
* accessibility feedback.

Aim for a minimum contrast ratio of approximately:

**4.5:1**

for normal text and relevant UI elements.

---

# 38. Performance

The application should feel fast and responsive.

Targets:

* fast startup after initial vocabulary import;
* smooth 60 fps learning-card interactions;
* responsive long vocabulary lists;
* efficient chart rendering;
* reasonable steady-state memory usage;
* no expensive work on the main thread.

Bundled vocabulary import must not freeze the UI.

Perform expensive statistics calculations efficiently and avoid repeatedly recalculating identical data during UI updates.

Measure important performance behavior in a Release build and document meaningful limitations rather than artificially optimizing for unrealistic benchmark numbers.

---

# 39. Bundled Vocabulary Data

Provide:

* `cet4.json`
* `cet6.json`

Together they must contain at least:

**500 vocabulary words**

Minimum:

* CET4 ≥ 300
* CET6 ≥ 200

Every word should contain useful real vocabulary data.

At minimum, each word should include:

* spelling;
* American pronunciation;
* British pronunciation;
* at least two definitions;
* at least one example sentence.

Do not fill the files with obvious placeholder or synthetic test entries.

Document the vocabulary-file format.

Vocabulary data must live in standalone resource files rather than being hard-coded into Swift source code.

---

# 40. Automated Testing

Create meaningful automated tests covering the application's most important domain logic.

Target strong coverage of business logic rather than meaningless coverage of trivial UI code.

At minimum, thoroughly test:

## Spaced repetition

Cover:

* all quality scores;
* interval calculation;
* Easiness Factor;
* minimum Easiness Factor;
* state transitions;
* mastery logic;
* incorrect-answer reset;
* local-date handling;
* midnight boundaries;
* timezone changes where relevant.

## Quiz generation

Cover:

* unique choices;
* correct-answer integrity;
* distractor validity;
* quiz-type generation;
* insufficient vocabulary;
* randomized answer positions.

## Streaks

Cover:

* normal streaks;
* missed days;
* streak resets;
* Streak Freeze;
* monthly freeze reset;
* midnight boundaries.

## Statistics

Cover:

* daily aggregation;
* weekly aggregation;
* monthly aggregation;
* empty data;
* calendar boundaries.

## Achievements

Cover every achievement trigger.

Ensure achievements cannot unlock repeatedly.

## Import / Export

Cover:

* JSON;
* CSV;
* duplicate handling;
* invalid rows;
* backup;
* restore;
* export/import round trips.

## Search

Cover:

* prefix matching;
* substring matching;
* Chinese-definition matching;
* typo tolerance.

---

# 41. UI Testing

Provide automated UI coverage for several core user journeys.

At minimum:

1. complete first-launch onboarding;
2. complete one learning group;
3. view the group summary;
4. complete one quiz;
5. inspect quiz results;
6. modify the daily goal;
7. confirm the Home progress UI responds correctly.

Build the UI so automated tests can reliably identify important controls.

---

# 42. Code Quality

The final project must:

* compile without errors;
* compile without warnings caused by project code;
* avoid unsafe force-unwrapping;
* avoid `try!`;
* handle failures explicitly;
* surface meaningful user-facing errors;
* use structured logging where appropriate;
* keep UI and business logic appropriately separated;
* remain understandable and maintainable.

Use previews and sample data where they meaningfully improve development and verification.

Do not leave placeholder production code.

Do not leave:

* `TODO`
* fake implementations
* stubbed buttons
* empty screens
* commented-out unfinished functionality.

---

# 43. Privacy

The application should be privacy-friendly by design.

Core functionality must work offline.

Do not add:

* tracking;
* telemetry;
* advertising;
* third-party analytics.

Provide the required privacy manifest.

Document any Apple system service that may involve network communication, particularly optional iCloud synchronization.

---

# 44. Deliverables

Deliver a complete Xcode project containing everything required to build and run LingoLearn.

The project must include:

1. complete iOS application;
2. Widget Extension;
3. automated unit tests;
4. automated UI tests;
5. bundled CET4 vocabulary data;
6. bundled CET6 vocabulary data;
7. App Icon assets;
8. launch assets;
9. semantic color assets;
10. privacy manifest;
11. complete README.

---

# 45. README

The README should explain:

* project overview;
* supported iOS / Xcode requirements;
* how to build and run;
* overall architecture;
* important technical decisions;
* persistence strategy;
* spaced-repetition design;
* vocabulary data format;
* how to add new vocabulary books;
* import/export behavior;
* iCloud behavior;
* widgets and system integrations;
* how to run tests;
* known limitations.

Include an architecture diagram or clear architecture description.

---

# 46. Implementation Process

Before coding, inspect the complete specification and independently determine the most appropriate architecture and implementation strategy.

Then:

1. briefly present the implementation plan;
2. identify major subsystems and dependencies;
3. define a sensible development order;
4. proceed directly with implementation.

Do **not** stop and wait for my confirmation after presenting the plan.

Continue until the application is implemented as completely as reasonably possible.

You are explicitly expected to make technical decisions yourself.

Do not ask me to choose:

* data models;
* architecture patterns;
* persistence structure;
* service boundaries;
* project folder layout;
* navigation implementation;
* state-management details;
* concurrency strategy;
* internal APIs;

unless an unavoidable product-level ambiguity prevents implementation.

Prefer making a strong engineering decision and documenting it.

---

# 47. Completion Requirements

Before declaring the project complete:

* build the application;
* fix all compile errors;
* fix project-generated warnings where practical;
* run the test suite;
* fix failing tests;
* verify the main user flows;
* inspect obvious edge cases;
* verify bundled vocabulary resources;
* verify widgets build correctly;
* verify deep links / system integrations where they can be tested locally.

Do not claim a feature works merely because code for it exists.

Where tooling allows, actually execute and verify it.

If an operating-system limitation prevents automated verification, document exactly what remains to be manually verified.

---

# 48. Final Report

When implementation is complete, provide a concise engineering report containing:

* major architectural decisions you made;
* major features completed;
* tests executed and their results;
* build status;
* performance considerations;
* known limitations;
* any functionality requiring manual device verification.

The goal is not merely to produce a large amount of code.

The goal is to deliver the most complete, coherent, maintainable, and production-quality implementation of **LingoLearn** possible while demonstrating strong independent iOS product-engineering judgment.
