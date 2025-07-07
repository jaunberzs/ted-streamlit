
import streamlit as st
import pandas as pd
import requests
import zipfile
import io
import matplotlib.pyplot as plt

st.set_page_config(page_title="TED Market Analyzer", layout="wide")
st.title("📊 TED Market Analyzer — Экологические тендеры по Европе")

st.sidebar.header("🔍 Параметры фильтрации")
keywords_input = st.sidebar.text_input("Ключевые слова (через запятую):", "air, emission, dispersion, model, environment, noise, impact")
selected_keywords = [kw.strip().lower() for kw in keywords_input.split(",")]

# Все европейские страны + UK + CH
countries = {
    "Austria": "AT", "Belgium": "BE", "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY", "Czech Republic": "CZ",
    "Denmark": "DK", "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE", "Greece": "GR", "Hungary": "HU",
    "Ireland": "IE", "Italy": "IT", "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU", "Malta": "MT",
    "Netherlands": "NL", "Poland": "PL", "Portugal": "PT", "Romania": "RO", "Slovakia": "SK", "Slovenia": "SI",
    "Spain": "ES", "Sweden": "SE", "Norway": "NO", "Iceland": "IS", "Liechtenstein": "LI", "Switzerland": "CH", "United Kingdom": "UK"
}
selected_country_names = st.sidebar.multiselect("Страны:", list(countries.keys()), default=["Germany", "Latvia", "Poland"])
selected_country_codes = [countries[name] for name in selected_country_names]

start_button = st.sidebar.button("🚀 Запустить анализ")

if start_button:
    st.info("🔄 Загрузка и обработка данных...")
    try:
        url = "https://ted.europa.eu/resources/download/latest/TED_EXPORT.csv.zip"
        response = requests.get(url)
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        csv_filename = [name for name in zip_file.namelist() if name.endswith('.csv')][0]

        with zip_file.open(csv_filename) as csv_file:
            df = pd.read_csv(csv_file, sep=';', encoding='utf-8', low_memory=False)

        df = df[df['ISO_COUNTRY_CODE'].isin(selected_country_codes)]
        mask = df['TITLE'].fillna('').str.lower().apply(lambda t: any(k in t for k in selected_keywords))
        df = df[mask]

        st.success(f"✅ Найдено {len(df)} подходящих тендеров.")
        st.dataframe(df)

        # График
        if not df.empty:
            df['DATE_PUBLICATION'] = pd.to_datetime(df['DATE_PUBLICATION'], errors='coerce')
            df['Month'] = df['DATE_PUBLICATION'].dt.to_period('M')
            summary = df.groupby(['Month', 'ISO_COUNTRY_CODE']).size().unstack(fill_value=0)
            st.subheader("📈 Динамика по странам")
            st.bar_chart(summary)

        # Скачать CSV
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Скачать CSV", data=csv_bytes, file_name="filtered_ted.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Ошибка: {e}")
