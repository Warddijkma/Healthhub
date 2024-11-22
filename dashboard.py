
import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Functie om data op te halen van CBS API
def fetch_cbs_data():
    # CBS API URL voor bevolkingsgegevens per gemeente
    url = "https://opendata.cbs.nl/ODataApi/odata/84583NED/TypedDataSet"
    response = requests.get(url)

    # Controleer of de API succesvol is aangeroepen
    if response.status_code != 200:
        st.error("Fout bij het ophalen van data van de CBS API.")
        return None

    # Parse de JSON-data naar een Pandas DataFrame
    try:
        data = response.json()['value']
        df = pd.DataFrame(data)
        return df
    except KeyError:
        st.error("De response van de API bevatte geen geldige data.")
        return None


# Functie om de data te verwerken
def process_data(df):
    # Kies de kolommen die we nodig hebben
    selected_columns = [
        "WijkenEnBuurten",  # Code van de wijk of gemeente
        "Gemeentenaam_1",   # Gemeentenaam
        "Bevolking_1jan_5",  # Bevolking per 1 januari
        "Mantelzorgers_65jaarOfOuder_30"  # Aantal mantelzorgers (65+)
    ]
    df = df[selected_columns]

    # Hernoem kolommen voor leesbaarheid
    df.columns = ["Code", "Gemeente", "Bevolking", "Mantelzorgers"]

    # Bereken mantelzorgers per 1.000 inwoners
    df["Mantelzorg_ratio"] = (df["Mantelzorgers"] / df["Bevolking"]) * 1000

    # Verwijder rijen met ontbrekende waarden
    df = df.dropna()

    return df


# Functie om een grafiek te maken
def plot_data(df):
    # Sorteer de data op mantelzorg_ratio
    df_sorted = df.sort_values("Mantelzorg_ratio", ascending=False).head(20)

    # Maak een staafdiagram
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_sorted["Gemeente"], df_sorted["Mantelzorg_ratio"], color="skyblue")
    ax.set_title("Top 20 Gemeenten met Hoogste Mantelzorg Ratio", fontsize=16)
    ax.set_xlabel("Gemeente", fontsize=12)
    ax.set_ylabel("Mantelzorgers per 1.000 inwoners", fontsize=12)
    ax.set_xticklabels(df_sorted["Gemeente"], rotation=45, ha="right")
    return fig


# Streamlit-app
def main():
    st.title("Mantelzorg Dashboard")
    st.write("""
    Dit dashboard toont gegevens over mantelzorgers in verschillende gemeenten
    in Nederland. De gegevens zijn gebaseerd op data van het CBS.
    """)

    # Data ophalen
    with st.spinner("Data ophalen van de CBS API..."):
        df = fetch_cbs_data()
        if df is None:
            st.stop()

    # Data verwerken
    df_processed = process_data(df)

    # Samenvatting tonen
    st.subheader("Samenvatting van de Data")
    st.write("Aantal gemeenten in de dataset:", len(df_processed))
    st.write(df_processed.head())

    # Grafiek plotten
    st.subheader("Visualisatie van Mantelzorg Ratio")
    fig = plot_data(df_processed)
    st.pyplot(fig)


if __name__ == "__main__":
    main()
