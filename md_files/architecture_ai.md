# DataLit | AI Development & Architecture Log
**Project Theme:** End-to-End Modular Data Processing & AI-Assisted Profiling

---

## 🏗️ Core Architecture & Initialization
The DataLit application was built using a highly modular, service-oriented architecture centered on **Streamlit**.

- **Session State Management**: Centralized `dataset_manager.py` service to track the "working dataframe" and transformation history.
- **Performance Optimized**: Implemented `st.cache_data` for computationally expensive profiling and automated data reloading. 
- **Modular Services**: Backend logic segregated into `core/` (transformation, profiling, validation) and UI components into `pages/`.

---

## 📂 Phase 1: Data Ingestion & Profiling
Implemented a robust entry layer capable of handling diverse industrial data formats.

- **Unified Loader**: Support for `.csv`, `.xlsx`, `.json`, and Google Sheets (Web UI).
- **Profound Profiling**: 
  - Dynamic Dtype inference.
  - Advanced descriptive statistics (Skewness/Kurtosis for numeric, Cardinality (%) for categorical).
  - **Memory Analysis**: A niche utility to calculate compression potential via type-casting.
- **Constraints Validation Engine**: Immediate feedback system flagging datasets that fail to meet "ideal" criteria (e.g., < 1000 rows or < 8 columns).

---

## 🧹 Phase 2: Cleaning & Preparation Studio
A comprehensive suite of data engineering tools was developed to handle messy real-world datasets.

- **Missing Values**: Flexible imputation strategies including Constant, Mean, Median, Mode, and Time-series fills (FFill/BFill).
- **Duplicate Removal**: Scans for exact row duplicates or specific column-level collisions.
- **Outlier Engine**: Automated detection using IQR/Z-Score with options to cap (Winsorize) or remove corrupted records.
- **Categorical Suite**: Multi-layer mapping UI, rare category grouping, and unmatched value handling (e.g., mapping unknown values to "Other").

---

## 📊 Phase 3: Visualization & Insight Strategy
- **Visualization Builder**: Rule-based recommendation engine that suggests optimal charts (Scatter, Box, Heatmap, etc.) based on column data types without burning LLM tokens.
- **AI-Driven Strategy**: A deep analysis module that identifies "Critical Risks" and "Strategic Actions" using either OpenAI or a rule-based fallback algorithm.

---

## ⌨️ Phase 4: NLP Command Suite (Beta)
Developed a heuristic natural language processor for faster data manipulation via a text interface.
Supported commands include:
- `drop column [name]`
- `rename [col] to [new_name]`
- `remove outliers`
- `fill missing in [col] with [method]`
- `encode [col]` (One-hot encoding)
- `drop missing in [col]`

---

## 🛠️ Key Technical Troubleshooting & Fixes
- **Import Errors**: Resolved module-level import conflicts seen on Streamlit Cloud by standardizing placement at the top of scripts.
- **Arrow Serialization**: Patched common Arrow serialization errors by enforcing consistent type-casting for `object` and `int64` columns during UI rendering.
- **Caching**: Implemented intelligent cache invalidation in `dataset_manager` to ensure UI reactivity during complex pipeline chains.

---

## 🌟 Final Delivery Status
The DataLit project satisfies all 10 milestones of the requirement checklist, including Bonus features (AI integration, Google Sheets connectivity, and comprehensive automated profiling).
