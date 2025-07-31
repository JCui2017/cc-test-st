# SDOH 

## Summary
This app provides an overview of Social Determinant of Health for the U.S., based on public data sources.
- sources of data include Census, and other possible public sources
- attributes include education, income, and other relevant SDOH metrics
- the default output is a national geographic map. the user can also select a specific state to drill down.

## Tech
venv, python, streamlit, plotly (using go methods)

## Requirements
0. Use venv
1. Implement these features in a thoughtful way. 
2. Verify the results. 
3. Launch the app and ensure it is running and UI is visible.
4. Provide a summary in the end for how much time was taken

## Features
  Data Integration:
  - Implement Census API integration
  - Use real data only. no mock-up data
  - Use local caching to persist data across sessions and reduce API calls
    - 1 week
    - use .csv to store locally
  - get county-level data 
  - provide meta-data about data coverage

  Map Visualization:
  - National Map: create choropleth map to show the value of selected metrics by state
  - US state choropleth maps, always use:
      locations=state_abbreviations,  # ['AL', 'AK', 'AZ', ...]
      locationmode='USA-states'
  - for "positive" metrics, such as Income, use shades of green; for "negative" metrics, such as unemployment, use shades of red
  - Implement zoom/pan functionality for better state drill-down
  - State Map: Upon clicking a state on the national map, plot choropleth map below for all counties within the selected state.

  User Experience:
  - use user-friendly and simple design
  - Implement error handling for failed API calls
  - Add data export functionality (CSV, PDF)

