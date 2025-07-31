# 🏥 Social Determinants of Health (SDOH) Dashboard

A comprehensive web-based dashboard that provides interactive visualizations of Social Determinants of Health across the United States, using real-time data from the U.S. Census Bureau's American Community Survey (ACS).

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### 📊 Interactive Data Visualization
- **National Choropleth Map**: State-level visualization of SDOH metrics
- **County-Level Drill-Down**: Click any state to explore county-level data
- **Smart Color Coding**: Green scales for positive metrics (income, education), red scales for negative metrics (poverty, unemployment)
- **Interactive Controls**: Zoom, pan, and hover for detailed information

### 📈 Comprehensive SDOH Metrics
- **Median Household Income** - Economic indicator
- **Poverty Rate** - Economic hardship measure
- **Educational Attainment** - Bachelor's degree or higher percentage
- **Unemployment Rate** - Labor market indicator
- **Health Insurance Coverage** - Healthcare access measure

### 🔄 Real-Time Data Integration
- **Live Census API**: Direct connection to U.S. Census Bureau ACS 2022 data
- **Smart Caching**: 1-week CSV-based caching system to reduce API calls
- **No Mock Data**: All visualizations use authentic government statistics
- **Metadata Coverage**: Complete data source information and coverage details

### 📥 Data Export
- **CSV Export**: Download raw data for further analysis
- **PDF Reports**: Generate formatted reports with visualizations
- **Multiple Formats**: Support for various data export needs

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sdoh-dashboard.git
   cd sdoh-dashboard
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8501`
   - Start exploring SDOH data!

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python 3.8+
- **Web Framework**: Streamlit
- **Data Visualization**: Plotly (with go methods)
- **Data Processing**: Pandas, NumPy
- **Geographic Data**: Geopandas, Shapely
- **API Integration**: Requests
- **Export**: ReportLab (PDF), openpyxl (Excel)

### Data Flow
```
U.S. Census API → Data Processing → CSV Cache → Streamlit UI → Interactive Maps
```

### Key Components
- **`CensusDataManager`**: Handles API interactions and caching
- **Visualization Functions**: Create choropleth maps and charts
- **Export Functions**: Generate CSV and PDF outputs
- **Caching System**: Separate state and county cache files for optimal performance

## 📚 Data Sources

### Primary Data Source
- **U.S. Census Bureau American Community Survey (ACS)**
- **Year**: 2022 (1-Year Estimates)
- **Coverage**: All 50 states + Washington DC
- **Geographic Levels**: State and County
- **Update Frequency**: Annual

### Data Quality
- **Official Government Statistics**: Highest reliability
- **Population Coverage**: Comprehensive demographic representation
- **Regular Updates**: Annual data releases
- **Transparent Methodology**: Well-documented survey methods

## 🎯 Use Cases

### Research & Analysis
- **Academic Research**: Study health equity patterns
- **Policy Analysis**: Inform evidence-based policy decisions
- **Trend Analysis**: Compare metrics across states and counties
- **Grant Writing**: Support proposals with current demographic data

### Public Health Applications
- **Resource Allocation**: Identify areas of greatest need
- **Program Planning**: Target interventions based on SDOH data
- **Health Equity Assessment**: Understand disparities across regions
- **Community Health Assessment**: Local public health planning

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
- Follow the installation instructions above
- Run tests: `python -m pytest tests/`
- Check code style: `flake8 app.py`

## 📋 API Usage

The application connects to the U.S. Census Bureau API:
- **No API Key Required**: Basic queries work without authentication
- **Rate Limiting**: Handled through intelligent caching
- **Endpoints Used**: ACS 1-Year Profile Data
- **Timeout Settings**: 30-second timeout for reliability

## 🐛 Troubleshooting

### Common Issues

**Map not displaying**: Check internet connection for Census API access

**Slow loading**: First-time data fetch takes longer; subsequent loads use cache

**State selection not working**: Ensure JavaScript is enabled in your browser

**Data export failing**: Check write permissions in the application directory

### Performance Optimization
- Cache files reduce API calls by 90%+
- Separate state/county caches prevent data conflicts
- Efficient data processing with pandas vectorization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **U.S. Census Bureau** for providing comprehensive demographic data
- **Streamlit** for the excellent web app framework
- **Plotly** for powerful visualization capabilities
- **Open Source Community** for the foundational libraries

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review the implementation summary for technical details

---

**Built with ❤️ for public health research and policy**