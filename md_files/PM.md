# DataLit Project Management (PM.md)

This document outlines the 8-sprint development lifecycle of DataLit, a professional-grade Data Preparation Studio.

## Sprint M1: Project Setup & Architecture
**Goal**: Establish a scalable, modular foundation.
- **Modular Structure**: Organized into `core` (logic), `services` (orchestration), `pages` (UI), and `utils` (helpers).
- **Separation of Concerns**: UI components interact only with Services, which in turn use Core tools.
- **Environment**: Clean `requirements.txt` and Streamlit routing in `app.py`.
- **Dataset Independence**: No hardcoded schemas; the app adapts to any CSV, Excel, or JSON structure.

## Sprint M2: Data Upload & Profiling
**Goal**: Enable seamless data ingestion and instant health checks.
- **Multi-Format Loader**: Support for CSV, Excel, and JSON.
- **Google Sheets**: Integration via public CSV export endpoints.
- **Deep Profiling**: Automated analysis of missing values, data types, and descriptive statistics (mean, std, etc.).

## Sprint M3: Data Cleaning & Transformation Engine
**Goal**: Build a robust, reproducible transformation system.
- **Central Manager**: All changes flow through `dataset_manager.py` to maintain state integrity.
- **Transformation Toolset**: 
  - Missing value imputation (Mean/Median/Mode).
  - Outlier detection and handling (IQR/Z-Score).
  - Categorical cleaning (Standardization, Mapping).
  - Numeric scaling (MinMax, Z-score).
- **History System**: Full Undo/Redo capability and a persistent "Recipe Log."

## Sprint M4: Visualization Builder
**Goal**: Create a dynamic, role-based dashboarding experience.
- **Mandatory Charts**: Support for Histogram, Box, Scatter, Line, Bar, and Heatmap.
- **Intelligent UI**: Controls adapt based on the selected chart type and data resolution.
- **Performance**: High-speed rendering using `matplotlib` and `seaborn` backends.

## Sprint M5: Export System + Recipe Log
**Goal**: Ensure reproducible and portable results.
- **Multi-Format Export**: Cleaned data exportable as CSV, Excel, or JSON.
- **Recipe Logic**: Transformations are exportable as a standalone Python script, allowing users to replay their cleaning session in production.
- **PDF Reporting**: Generation of "Analysis Reports" with embedded charts and summaries.

## Sprint M6: Performance Optimization
**Goal**: Maintain responsiveness under heavy data loads.
- **Caching Strategy**: Intelligent use of `st.cache_data` for heavy computations.
- **Memory Efficiency**: Calculation of "Memory Savings" via categorical downcasting.
- **UI Responsiveness**: Optimized session state to prevent redundant re-renders.

## Sprint M7: AI Assistant (Rule-Based & LLM)
**Goal**: Provide guided cleaning suggestions.
- **Health Score**: A 0-100 visual metric of dataset quality.
- **Suggestion Engine**: Automated detection of duplicates, outliers, and missingness.
- **Fix Mechanism**: One-click "Apply Fix" buttons that integrate directly with the transformation engine.
- **LLM Insights**: Optional deep-dive analysis powered by OpenAI.

## Sprint M8: Testing & Deployment
**Goal**: Guarantee stability and reliability.
- **Full Test Suite**: Unit tests covering transformations, loading, and state management.
- **Edge Case Handling**: Verified behavior for empty, high-cardinality, and all-null datasets.
- **Cloud Ready**: Configured for instant deployment to Streamlit Community Cloud.

## Project Finalization (Post-M8 Audit)
**Goal**: Achieve 100% functional reproducibility for industrial-grade pipelines.
- **Transformation Parity**: Verified that all 17+ unique UI-driven cleaning steps (Rare Category Grouping, Specific Type Conversions, Binning, etc.) map correctly to the standalone Python `core/pipeline.py`.
- **Reproducibility Guarantee**: The exported recipe script is now a functional, production-ready 1:1 mirror of the interactive session.
- **Repository Optimization**: Documentation consolidated into a clean, "rich-only" structure in `/md_files`.
