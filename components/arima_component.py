import os
from services.arima_service import ARIMAService
from services.wiki_traffic_service import WikiTrafficService

def load_default_arima(app):
    print(">> START:: load_default_arima")
    arima_service = ARIMAService()
    wiki_traffic_service = WikiTrafficService()

    # Check for existing arima figures
    arima_figures_dir = os.path.join(app.static_folder, 'arima_figures')
    arima_existing_figures = set(os.listdir(arima_figures_dir)) if os.path.exists(arima_figures_dir) else set()

    res = arima_service.load_arima_results()
    if res:
        pass
    else:
        arima_service.run_arima_model(wiki_traffic_service.get_traffic_data_as_dataframe(),arima_existing_figures,7)

    print("Default arima results loaded successfully.")
    print(">> END:: load_default_arima")
