# CLBML: Catastrophic Events and Language-Based Machine Learning

This project aims to analyze the interrelationships and political responses to catastrophic events such as terrorist attacks and wars by examining their impact on information searches on the internet. The analysis focuses on understanding how people react and seek information in response to such events and whether there are statistical correlations between search frequencies in different languages.

## Project Structure
```
        CLBML-Wikipedia-Search-Emergencies/
    │
    ├── app.py
    ├── instance/
    │   ├── CLBML.db
    ├── templates/
    │   ├── base.html
    │   ├── events.html
    │   ├── research.html
    │   ├── welcome.html
    │   ├── wiki_traffic.html
    │   └── wikipedia.html
    ├── tests/
    │   ├── test_auto_correlation.py
    │   ├── test_cross_correlation.py
    ├── static/
    │   ├── favicon.ico
    │   ├── style.css
    │   ├── arima_figures/
    │   │   ├── arima_forecast_ar_Charlie Hebdo shooting.png
    │   │   ├── arima_forecast_ar_Israel–Hamas war.png
    │   │   ├── arima_forecast_ar_Manchester Arena bombing.png
    │   │   ├── arima_forecast_en_Charlie Hebdo shooting.png
    │   │   ├── arima_forecast_en_Israel–Hamas war.png
    │   │   ├── arima_forecast_en_Manchester Arena bombing.png
    │   │   ├── arima_forecast_fr_Charlie Hebdo shooting.png
    │   │   ├── arima_forecast_he_Israel–Hamas war.png
    │   ├── auto_corr_figures/
    │   │   ├── auto_corr_ar_Charlie Hebdo shooting.png
    │   │   ├── auto_corr_ar_Israel–Hamas war.png
    │   │   ├── auto_corr_ar_Manchester Arena bombing.png
    │   │   ├── auto_corr_en_Charlie Hebdo shooting.png
    │   │   ├── auto_corr_en_Israel–Hamas war.png
    │   │   ├── auto_corr_en_Manchester Arena bombing.png
    │   │   ├── auto_corr_fr_Charlie Hebdo shooting.png
    │   │   ├── auto_corr_he_Israel–Hamas war.png
    │   ├── peaks_figures/
    │   │   ├── peaks_ar_Charlie Hebdo shooting.png
    │   │   ├── peaks_ar_Israel–Hamas war.png
    │   │   ├── peaks_ar_Manchester Arena bombing.png
    │   │   ├── peaks_en_Charlie Hebdo shooting.png
    │   │   ├── peaks_en_Israel–Hamas war.png
    │   │   ├── peaks_en_Manchester Arena bombing.png
    │   │   ├── peaks_fr_Charlie Hebdo shooting.png
    │   │   ├── peaks_he_Israel–Hamas war.png
    ├── models/
    │   ├── __init__.py
    │   ├── event.py
    │   ├── wikipedia_page.py
    ├── repositories/
    │   ├── __init__.py
    │   ├── event_repository.py
    │   ├── wikipedia_repository.py
    │   ├── wiki_traffic_repository.py
    ├── services/
    │   ├── __init__.py
    │   ├── arima_service.py
    │   ├── auto_correlation_service.py
    │   ├── cross_corr_service.py
    │   ├── event_service.py
    │   ├── outlier_service.py
    │   ├── peaks_service.py
    │   ├── reset_service.py
    │   ├── wikipedia_service.py
    │   ├── wiki_traffic_service.py
    ├── utils/
    │   ├── __init__.py
    │   ├── api.py
    │   ├── database.py
    │   ├── exceptions.py
    ├── components/
    │   ├── __pycache__/
    │   │   ├── arima_component.cpython-311.pyc
    │   │   ├── auto_correlation_component.cpython-311.pyc
    │   │   ├── events_component.cpython-311.pyc
    │   │   ├── peaks_component.cpython-311.pyc
    │   │   ├── update_check_component.cpython-311.pyc
    │   │   ├── wikipedia_component.cpython-311.pyc
    │   │   ├── wiki_traffic_component.cpython-311.pyc
    │   ├── arima_component.py
    │   ├── auto_correlation_component.py
    │   ├── events_component.py
    │   ├── peaks_component.py
    │   ├── update_check_component.py
    │   ├── wikipedia_component.py
    │   ├── wiki_traffic_component.py
    ├── files/
    │   ├── arima_results.csv
    │   ├── cross_correlation.csv
    │   ├── events_default.json
    │   ├── peaks_results.csv
    │   ├── wikipedia_pages_default.json
    │   ├── wiki_traffic_data.csv
    ├── requirements.txt
    └── .env
```

## Abstract

This study analyzes the interrelationships and political responses to catastrophic events like terrorist attacks and wars and their impact on information searches on the internet. The aim is to understand how people react and seek information in response to such events and identify statistical correlations between search frequencies in different languages.

Data was collected from Wikipedia in various languages (English, Arabic, Hebrew) for three major events: the Manchester bombings, the Israel-Hamas war (Iron Swords War), and the Charlie Hebdo attacks. The data was gathered using Wikipedia's API and processed for statistical analysis using Python and the Pandas library. The analysis included examining correlations between search frequencies in different languages and comparing international responses to the events.

## Setup

To set up the project after downloading it from Git, follow these steps:

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Create and activate a virtual environment:**

```
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
```
3. **Install the required dependencies:**
    
```
    pip install -r requirements.txt
```

4. **Create a .env file in the root directory of the project with the following content:**

```
    FLASK_APP=app.py
    FLASK_ENV=development
    DATABASE_URI=sqlite://clear/CLBML.db
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    DELETE_DATABASES=True
```

5. **Open the project in VSCode.**
6. **Open a new terminal:**
    - In the top menu bar, click on Terminal and then select New Terminal.
7. **Activate the virtual environment and update python pip:**
```
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    python.exe -m pip install --upgrade pip
```
8. **Run the Flask application:**
```
    flask run
    or
    flask run --debug # for debug mode!
```
9. **Access the application:**
    - Open your web browser and navigate to http://127.0.0.1:5000/ to access the application.

