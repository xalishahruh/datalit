# DataLit 💎

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**DataLit** is a professional Data Transformation & AI-Assisted Cleaning Studio built with Streamlit. It provides an intuitive interface for data analysts, scientists, and engineers to load, profile, clean, visualize, and export datasets efficiently.

## 🌟 Why DataLit is Useful

Data cleaning and preparation often consume a large portion of a data professional's time. DataLit streamlines this process by offering a centralized, easy-to-use web application that combines traditional data manipulation tools with powerful AI-driven insights:

- **📂 Load & Profile Data**: Instantly upload your datasets and receive comprehensive insights into missing values, duplicates, and statistical distributions.
- **🛠️ Clean & Transform**: Apply a variety of transformations safely, such as imputing missing values, standardizing dates, changing data types, and scaling numerical features.
- **🤖 AI Assistant**: Let our rule-based engine and optional LLM insights guide you through the cleaning process with actionable recommendations.
- **📊 Visualize Data**: Build stunning, highly optimized interactive charts and dashboards, even with large datasets exceeding 50,000 rows.
- **📥 Export Results**: Download your clean, ready-to-use datasets along with a full recipe log documenting all applied transformations.

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.9 or higher installed on your system. 

### Installation

- Local

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/datalit.git
   cd datalit
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

- Deployed
1. Follow the link https://datalit.streamlit.app/
   
### Usage

Start the Streamlit application by running the following command from the root directory:

```bash
streamlit run app.py
```

Once the application is running, open your web browser and navigate to the local URL provided in your terminal (typically `http://localhost:8501`). Wait for the app to initialize, then select **Overview** from the sidebar to upload your first dataset and begin your journey.

#### Understanding the AI Assistant & Groq API

DataLit features a robust AI Assistant designed to help you analyze and clean your data intelligently. 

**What is Groq?** 
Groq is a high-speed AI inference provider that powers our AI Assistant. It processes queries incredibly fast, giving you real-time proposals on the best way to clean and transform your specific dataset.

**How does it work?**
For your convenience, DataLit has been configured with a default built-in Groq API key so that anyone using the tool can get AI suggestions right out of the box without any setup. 

However, if you'd like to use your own secure API key for personalized usage or higher rate limits:
1. Navigate to the **AI Assistant** tab.
2. Ensure you have a Groq account, or go to [console.groq.com/keys](https://console.groq.com/keys) to create one.
3. Generate a new API key.
4. Input your custom key directly into the "Groq API Key" field in the AI Assistant configurations panel.
5. You can use the default one by toggling it - everything is safe (API is created on Zero-Trust Basis)

> **Note:** The AI Assistant allows you to switch between Groq and OpenAI based on your preferences and availability of API keys.

## 🆘 Where to Get Help

If you encounter any issues or have questions regarding DataLit:

- **Documentation**: Explore our comprehensive [Project Documentation](docs/project_documentation) folder or references directly inside the app.
- **Issue Tracker**: Check out our existing issues on GitHub or submit a new bug report/feature request to get support from the maintainers.

## 🤝 Maintainers & Contributing

DataLit is developed and actively maintained by a team of open-source enthusiasts and data engineers. We welcome contributions from developers of all skill levels!

- To learn more about how you can contribute to the project, please read our detailed [Contribution Guidelines](docs/CONTRIBUTING.md).
- To reach the core maintainers, feel free to open a discussion or tag us in your pull requests.

Thank you for using DataLit! Let's make data preparation clean, fast, and enjoyable.

This project was implemented as the part of Data Wrabgling and Vizualisation module's coursework by students with the following IDs - 00017978; 00017636
