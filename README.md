# CLBML: Catastrophic Events and Language-Based Machine Learning

This project aims to analyze the interrelationships and political responses to catastrophic events such as terrorist attacks and wars by examining their impact on information searches on the internet. The analysis focuses on understanding how people react and seek information in response to such events and whether there are statistical correlations between search frequencies in different languages.

## Project Structure

CLBML/
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
├── static/
│   └── style.css
├── models/
│   ├── __init__.py
│   ├── event.py
│   └── wikipedia_page.py
├── repositories/
│   ├── __init__.py
│   ├── event_repository.py
│   ├── wikipedia_repository.py
│   └── wiki_traffic_repository.py
├── services/
│   ├── __init__.py
│   ├── event_service.py
│   ├── outlier_service.py
│   ├── arima_service.py
│   ├── wikipedia_service.py
│   └── wiki_traffic_service.py
├── utils/
│   ├── __init__.py
│   ├── api.py
│   ├── database.py
│   └── exceptions.py
├── components/
│   ├── events_component.py
│   ├── wikipedia_component.py
│   ├── update_check_component.py
│   └── wiki_traffic_component.py
├── files/
│   ├── wiki_traffic_data.csv
│   ├── events_default.json
│   └── wikipedia_pages_default.json
├── requirements.txt
└── .env



Here is the syntax you can copy for your README.md file:

markdown
Copy code
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

Data was collected from Wikipedia in various languages (English, Arabic, Hebrew) for three major events: the Manchester bombings, the Israel-Hamas war (Iron Swords War), and the Charlie Hebdo attacks. The data was gathered using Wikipedias API and processed for statistical analysis using Python and the Pandas library. The analysis included examining correlations between search frequencies in different languages and comparing international responses to the events.

The analysis showed statistical correlations between search frequencies in different languages but significant differences in user responses to events based on language. For example, a high correlation was found between searches in English and Hebrew for the Iron Swords War, compared to a low correlation between searches in Arabic and English for the same event.

Advanced statistical models like ARIMA (AutoRegressive Integrated Moving Average) were used to analyze and predict search patterns. Statistical tools like Cross-Correlation and Auto-Correlation helped understand search patterns and the impact of events on user search behavior. The analysis revealed that during crises and catastrophic events, there is a significant increase in search frequencies across different languages, with local languages showing increased searches at specific times directly related to the event. Considering language limitations and their impact on information search is critical for a complete understanding of search behavior .
