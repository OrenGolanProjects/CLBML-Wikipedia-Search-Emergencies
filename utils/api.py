import pandas as pd
import requests


def get_wikipedia_traffic_data(language, endpoint_page_title, start_date, end_date,page_title):
    base_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
    headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}

    api_url = f"{base_url}/{language}.wikipedia/all-access/all-agents/{endpoint_page_title}/daily/{start_date}/{end_date}"

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    response_data = response.json()["items"]
    df = pd.DataFrame(response_data)

    df = df.drop(columns=["project", "article", "granularity", "access", "agent"])
    df.rename(columns={'views': f"{language}_{page_title}"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y%m%d%H")

    df = df.drop_duplicates(subset=['timestamp'], keep='first')
    df.set_index('timestamp', inplace=True)

    return df.asfreq('d')
