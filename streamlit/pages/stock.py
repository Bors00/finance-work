import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

def get_db_connection():
    # Se connecter à la base de données PostgreSQL via le service 'db'
    conn = psycopg2.connect(
        dbname="stocks_db",
        user="postgres",
        password="postgres",
        host="db"  # Nom du service PostgreSQL dans Docker Compose
    )
    return conn

st.title("Analyse des marchés")

try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM stocks")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description] #Obtenir l'intitule des colonnes
    cur.close()
    conn.close()
    
    if rows:
        
        df = pd.DataFrame(rows, columns=columns)

        df_sector = df.groupby('sector', as_index=False)['volume'].sum()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###### Répartition du volume des transactions par secteur")
        fig = px.pie(df_sector,
                     names='sector',
                     values='volume',
                     hole=0.3)
        
        st.plotly_chart(fig)
        
        #Creation d'un selecteur de categorie
        selected_sector = st.selectbox("Sélectionnez le secteur à analyser", df['sector'].unique())

        if selected_sector:
            df_selected_sector = df[df['sector'] == selected_sector]
            top_5_ticker = df_selected_sector.groupby('ticker')['volume'].sum().nlargest(5).index
            filtered_tickers = df_selected_sector[df_selected_sector['ticker'].isin(top_5_ticker)]
        else:
            top_5_ticker = df.groupby('ticker')['volume'].sum().nlargest(5).index
            filtered_tickers = df[df['ticker'].isin(top_5_ticker)]

        st.markdown("<br>", unsafe_allow_html=True)

        # Conversion de la colonne 'ticker' en index pour les colonnes marketcap et enterprisevalue
        df_mrktcapVsEntval = filtered_tickers.set_index("ticker")[["marketcap", "enterprisevalue"]]
        df_mrktcapVsEntval = df_mrktcapVsEntval.reset_index().melt(id_vars="ticker", var_name="legende", value_name="valeur")

        # Creation du graphique avec des barres groupees pour le meme ticker afin de faire la comparaison Market Cap vs Enterprise Value par Ticker
        mrktcapVsEntval = px.bar(df_mrktcapVsEntval, 
                    x="ticker", 
                    y="valeur", 
                    color="legende", 
                    barmode="group",
                    title="Capitalisation boursière vs Valeur comptable pour le top 5 des entreprises avec volumes de transactions les plus élevés")

        # Affichage du graphique
        st.plotly_chart(mrktcapVsEntval)

            
        st.markdown("<br>", unsafe_allow_html=True)

        # Conversion les colonnes en numerique et remplacer les valeurs invalides
        for col in ["trailingpe", "pricetobook"]:
            filtered_tickers[col] = pd.to_numeric(filtered_tickers[col], errors='coerce') # Conversion des erreurs en NaN
        
        # Conversion de la colonne 'ticker' en index pour les colonnes trailingpe et pricetobook
        df_gpeVsPrice = filtered_tickers.set_index("ticker")[["pricetobook", "trailingpe"]]
        df_gpeVsPrice = df_gpeVsPrice.reset_index().melt(id_vars="ticker", var_name="legende", value_name="valeur")

        # Creation du graphique avec des barres groupees pour le meme ticker afin de faire la comparaison Market Cap vs Enterprise Value par Ticker
        gpeVsPrice = px.bar(df_gpeVsPrice, 
                    x="ticker", 
                    y="valeur", 
                    color="legende", 
                    barmode="group",
                    title="Ratio Price-to-Book(P/B) VS Ratio Trailing P/E, pour le top 5 des entreprises avec volumes de transactions les plus élevés")

        # Affichage du graphique
        st.plotly_chart(gpeVsPrice)
        st.markdown("*Info:*")
        st.markdown("- le [ratio Price-to-Book(P/B)](https://finance.yahoo.com/news/5-stocks-attractive-price-book-120500451.html?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAAKNrM3U5xw9iBQkPDnhJmF5ARPZUuUd3IG_zqtr2A7VA1tN7-229UViARIRj_S_7skRc20m6HdI5HsE1J80QP3yZ5LCZU_O0VJatVEAb0DEQHTsfxpl4QcuXzbzfuPy2nYw0g7lkyLxdWloW98snE700zqz7aojae1zBcZnORLtj) "
        "permet de comparer la valeur marchande actuelle d'une entreprise à sa valeur comptable. Un P/B > 1 indique que le marché  surévalue la valeur de l'entreprise tandis qu'un P < 1 indique que l'entreprise est sous évaluée.")
        st.markdown("- le [ratio Trailing P/E](https://www.wallstreetprep.com/knowledge/pe-ratio-price-to-earnings/) "
        "permet de déterminer combien les investisseurs sont prêts à dépenser pour un dollar de bénéfice par action. Plus il est élevée, plus cela révèle que les investisseurs ont de grandes attentes sur la croissance de l'entreprise.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("###### Informations générales des entreprises sélectionnées")
        st.dataframe(filtered_tickers[['ticker','shortname','sector','industry','country','marketcap','enterprisevalue','trailingpe','pricetobook']])    

    else:
        st.info("Aucune donnée disponible.")
except Exception as e:
    st.error(f"Erreur lors de la connexion à la base de données : {e}")

