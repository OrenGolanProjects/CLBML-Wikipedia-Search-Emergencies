import os
from services.auto_correlation_service import AutoCorrelationService
from services.wiki_traffic_service import WikiTrafficService

def load_default_auto_correlation(app):

    print(">> START:: load_default_auto_correlation")
    auto_correlation_service = AutoCorrelationService()
    wiki_traffic_service = WikiTrafficService()


    wiki_traffic_df = wiki_traffic_service.get_traffic_data_as_dataframe()
    auto_correlation_service.reset_directory()
    auto_correlation_service.auto_corr_check_directory_existence()
    auto_correlation_service.perform_auto_corr(wiki_traffic_df)

    print("Default auto correlation results loaded successfully.")
    print(">> END:: load_default_auto_correlation")

