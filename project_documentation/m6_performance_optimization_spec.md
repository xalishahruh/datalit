Milestone 6 – Performance Optimization (Cache + Session State)
Objective
Optimize application performance, responsiveness, and scalability by introducing efficient caching, session state control, and memory-safe data handling.

Scope Overview
M6 focuses on:

Eliminating redundant computations

Optimizing dataset access and transformations

Improving UI responsiveness

Ensuring stable session behavior

Preparing system for larger datasets

 Architecture Additions
New / Updated Modules
utils/
├── cache_manager.py       # NEW → central caching logic
├── session_manager.py     # UPDATE → state lifecycle control
services/
├── dataset_manager.py     # UPDATE → cache-aware dataset handling
core/
├── profiling.py           # (optional enhancement)
⚙️ Core Concepts to Implement
1. Smart Caching Layer
Location:
utils/cache_manager.py
 Responsibilities:
Cache expensive computations

Cache transformed datasets

Avoid recomputation of:

profiling stats

transformation outputs

visualization data

Required Tools:
@st.cache_data

@st.cache_resource

 Requirements:
Cache keys must depend on:

dataset hash

transformation state

Must allow manual cache invalidation

2. Dataset Hashing Strategy
 Location:
utils/data_helpers.py (or cache_manager)

 Purpose:
Detect dataset changes and invalidate cache automatically

Requirements:
Generate hash using:

dataframe shape

column names

sample values

Used across:

caching

transformation tracking

3. Session State Control

Location:
utils/session_manager.py

Responsibilities:
Centralize all st.session_state access

Prevent duplication and memory leaks

Required Keys:
df                  # current dataset
original_df         # initial dataset
recipe_log          # transformations history
cache_keys          # cache tracking
ui_state            # UI selections
Requirements:
Initialize safely (no overwrites)

Reset functions must:

clear dataset

clear cache

reset UI state

4. Dataset Manager Optimization
Location:
services/dataset_manager.py

Enhancements:
Avoid full dataframe copies where unnecessary

Use caching for:

get_dataset()

transformation pipelines

Requirements:
Every transformation:

updates cache key

invalidates stale cache

Maintain immutability of original dataset

5. Lazy Evaluation Strategy
Concept:
Compute only when needed

Apply to:
profiling stats

visualizations

suggestions (future M7)

Requirements:
No heavy computation on page load

Trigger computation only:

on button click

when user changes config

6. UI Performance Optimization
Location:
pages/

Improvements:
Reduce unnecessary reruns

Prevent full page refresh on minor changes

Techniques:
Use st.form for grouped inputs

Use conditional rendering

Avoid nested expensive components

Requirements:
Heavy operations must show:

st.spinner

Charts should not re-render unnecessarily

7. Memory Optimization
Goals:
Reduce RAM usage

Prevent session crashes

Strategies:
Drop unused intermediate dataframes

Avoid chaining .copy() excessively

Use in-place operations when safe

Limit large object storage in session

8. Performance Monitoring (Optional but Recommended)
Location:
core/profiling.py

Features:
Track execution time of:

transformations

visualization rendering

Display simple metrics in UI

Integration Rules
Golden Rule:
ALL operations must still go through:

dataset_manager.add_transformation()
Why:
Keeps Recipe Log consistent

Enables Undo functionality

Maintains system integrity

Success Criteria
Performance
No noticeable lag for medium datasets (~50k rows)

Transformations execute efficiently

Caching
Repeated operations are significantly faster

Cache invalidates correctly on dataset change

Stability
No session crashes

No duplicated state keys

UX
UI feels responsive

No unnecessary re-renders

Maintainability
Clear separation:

caching logic

state management

business logic

Anti-Patterns to Avoid
❌ Caching mutable objects without control

❌ Direct session_state manipulation everywhere

❌ Recomputing dataset on every UI interaction

❌ Storing large unnecessary objects in session

❌ Breaking dataset_manager pipeline

Future Compatibility
M6 must support:

M7 AI Assistant (fast re-analysis)

Large dataset scaling

Efficient visualization rendering

Real-time suggestions

Final Deliverable
A fast, stable, and scalable application where:

Transformations feel instant

UI is smooth

Memory is controlled

System is ready for AI-driven workflows

