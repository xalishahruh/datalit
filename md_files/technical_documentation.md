# DataLit: Comprehensive Technical Documentation

This document provides a detailed overview of the DataLit platform, its features, technical stack, development lifecycle, and the evolution of its engineering process.

---

## 🚀 1. Platform Overview
**DataLit** is a production-grade AI-powered data preparation and visualization studio. It is designed to bridge the gap between raw data and clean, actionable insights using a combination of heuristic rules and advanced LLM assistance.

---

## 🛠️ 2. Technology Stack

### **Core Frameworks**
- **Streamlit**: Used for the reactive web interface and session state management.
- **Python 3.x**: The primary language powering the backend logic and data processing.

### **Data Engineering & Analysis**
- **Pandas**: The backbone for all dataframe manipulations, cleaning, and transformations.
- **NumPy**: Utilized for high-performance numerical operations and manual scaling logic.
- **Openpyxl**: Enables native Excel (.xlsx) file reading and writing.

### **Visualization Suite**
- **Plotly**: Powers interactive, responsive charts.
- **Seaborn & Matplotlib**: Used for static statistical visualizations (e.g., Correlation Heatmaps).

### **AI & Natural Language Processing**
- **OpenAI SDK**: Provides the interface for LLM integrations (GPT-4o, GPT-3.5).
- **Groq API**: Integrated as a high-speed inference provider for real-time cleaning proposals.

### **Integration & Security**
- **Gspread & Google-auth**: Facilitates secure Google Sheets connection and data pulls.
- **Python-dotenv**: Manages environment variables and API keys securely across sessions.

---

## ✨ 3. Complete Feature Set

### **I. Data Acquisition Hub**
- **Multi-Format Support**: Native loading for CSV, XLSX, and JSON.
- **Google Sheets Integration**: Automatic URL conversion to CSV for cloud-based data ingestion.
- **Intelligent Profiling**: Full data dictionary generation including types, missingness, and sample distributions.
- **Sample Datasets**: Pre-loaded samples (Titanic, Penguins) for immediate system demonstrations.

### **II. Cleaning & Transformation Engine**
- **Missing Value Studio**: Mean, Median, Mode, Constant, and Forward/Backward fill imputation.
- **Deduplication**: Robust row-wise and subset-based duplicate detection and removal.
- **Categorical Suite**: Standard formatting (Trim, Lower, Title), rare category grouping ("Other"), and manual mapping.
- **Numeric Tools**: Outlier detection using both IQR and Z-Score methods. Min-Max and Z-Score scaling.
- **Column Ops**: Dynamic renaming, math-based feature engineering, and binning.

### **III. AI-Guided Natural Language Assistant**
- **Heuristic Parser**: Fast, regex-based execution for common commands (e.g., "drop column X").
- **LLM-Driven Proposals**: Advanced translation of complex English requests into structured JSON transformation steps.
- **Preview & Confirm Architecture**: A safety-first UI that allows users to audit suggested changes before execution.

### **IV. Visualization Builder**
- **Rule-Based Recommender**: Automatic chart proposals based on column data types.
- **Interactive Charts**: Support for Histograms, Box Plots, Scatter Plots, Line Charts, and Grouped Bars.

### **V. Reproducible Export System**
- **Multi-Format Export**: Cleaned data available as CSV or XLSX.
- **Recipe Log**: Export the entire cleaning history as a JSON "Recipe" file.
- **Python Pipeline Generator**: One-click generation of a standalone Python script to reproduce the entire cleaning logic programmatically.

---

## 🏗️ 4. Development Process & Stages

### **Stage 1: Architecture & Foundation (M1-M2)**
- Established the modular file structure (`core/`, `services/`, `utils/`).
- Implemented the `DatasetManager` as the central state engine.

### **Stage 2: Foundation Logic & Verification (M3)**
- Developed the transformation engine for numeric and categorical data.
- **Milestone**: Achieved 39+ passing unit tests using `pytest` to guarantee logic stability.

### **Stage 3: Visualization & Export (M4-M5)**
- Integrated plotting libraries and built the rule-based chart recommender.
- Finalized data export buffers (BytesIO) for memory-safe file downloads.

### **Stage 4: Performance & Refinement (M6)**
- Implemented intelligent caching layer to handle large-scale datasets (50k+ rows).
- Optimized UI responsiveness through lazy profiling and explicit form actions.

### **Stage 5: AI Integration (M7)**
- Built the Natural Language to JSON translation layer.
- Secured the platform by migrating to environment variables and multi-provider LLM support.

---

## 📈 5. Historical Changes & Evolution
- **State Consolidation**: Migrated from fragmented `st.session_state` calls to a centralized `dataset_manager.py` service.
- **Security Hardenning**: Removed hardcoded API keys in favor of a secure `.env` and `load_dotenv()` pattern.
- **Performance Pivot**: Shifted from automatic heavy data profiling to a "Generate on Demand" model to prevent browser crashes on large files.
- **Dependency Optimization**: Reduced application footprint by implementing certain scaling and transformation logic manually using NumPy to minimize external package overhead.
