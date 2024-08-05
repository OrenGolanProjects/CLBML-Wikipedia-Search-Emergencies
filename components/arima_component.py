import os
from services.arima_service import ARIMAService
from services.wiki_traffic_service import WikiTrafficService

def load_default_arima(app):
    print(">> START:: load_default_arima")
    arima_service = ARIMAService()
    wiki_traffic_service = WikiTrafficService()

    # Check for existing arima figures
    arima_service.arima_check_directory_existence()

    # arima_service.run_arima_model(wiki_traffic_service.get_traffic_data_as_dataframe(),arima_existing_figures,7)

    print("Default arima results loaded successfully.")
    print(">> END:: load_default_arima")
