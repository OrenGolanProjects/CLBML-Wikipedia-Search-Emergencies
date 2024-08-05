# CLBML: Catastrophic Events and Language-Based Machine Learning

This project aims to analyze the interrelationships and political responses to catastrophic events such as terrorist attacks and wars by examining their impact on information searches on the internet. The analysis focuses on understanding how people react and seek information in response to such events and whether there are statistical correlations between search frequencies in different languages.

## Project Structure
```
    CLBML/
    │
    ├── app.py
    ├── instance/
    │ ├── CLBML.db
    ├── templates/
    │ ├── base.html
    │ ├── events.html
    │ ├── research.html
    │ ├── welcome.html
    │ ├── wiki_traffic.html
    │ └── wikipedia.html
    ├── tests/
    │ ├── test_cross_correlation.py
    ├── static/
    │ └── style.css
    ├── models/
    │ ├── init.py
    │ ├── event.py
    │ └── wikipedia_page.py
    ├── repositories/
    │ ├── init.py
    │ ├── event_repository.py
    │ ├── wikipedia_repository.py
    │ └── wiki_traffic_repository.py
    ├── services/
    │ ├── init.py
    │ ├── event_service.py
    │ ├── outlier_service.py
    │ ├── arima_service.py
    │ ├── wikipedia_service.py
    │ └── wiki_traffic_service.py
    ├── utils/
    │ ├── init.py
    │ ├── api.py
    │ ├── database.py
    │ └── exceptions.py
    ├── components/
    │ ├── events_component.py
    │ ├── wikipedia_component.py
    │ ├── update_check_component.py
    │ └── wiki_traffic_component.py
    ├── files/
    │ ├── wiki_traffic_data.csv
    │ ├── events_default.json
    │ └── wikipedia_pages_default.json
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

