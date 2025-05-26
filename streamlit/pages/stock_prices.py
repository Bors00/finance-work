import streamlit as st
import psycopg2
import pandas as pd
from datetime import timedelta

def get_db_connection():
    # Se connecter à la base de données PostgreSQL via le service 'db'
    conn = psycopg2.connect(
        dbname="stocks_db",
        user="postgres",
        password="postgres",
        host="db"  # Nom du service PostgreSQL dans Docker Compose
    )
    return conn

st.title("Analyse du prix des actions")

try:
    conn = get_db_connection()
    cur = conn.cursor()
    # Jointure entre stock_prices et stocks pour récupérer le shortname
    cur.execute("""
        SELECT sp.*, s.shortname 
        FROM stock_prices sp
        JOIN stocks s ON sp.ticker = s.ticker
    """)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  # Obtenir l'intitulé des colonnes
    cur.close()
    conn.close()
    
    if rows:
        # Création du DataFrame complet
        df_full = pd.DataFrame(rows, columns=columns)
        df_full['date'] = pd.to_datetime(df_full['date'])
        
        # Liste complète des entreprises pour le menu de sélection
        all_companies = sorted(df_full['shortname'].unique().tolist())
        
        # Pour alléger l'affichage global, on limite les données aux 2000 dernières lignes
        df = df_full.tail(2000)
        
        # Sélection des entreprises via le menu déroulant
        selected_tickers = st.multiselect("Sélectionnez les entreprises à comparer", all_companies)
        
        if selected_tickers:
            st.markdown("## Détails pour les compagnies sélectionnées")
            # Création d'un onglet par compagnie sélectionnée
            tabs = st.tabs([f"{ticker}" for ticker in selected_tickers])
            
            # Options d'horizon temporel pour filtrer l'historique
            horizon_options = ["1 journée", "1 semaine", "1 mois", "3 mois", "6 mois", "1 an", "5 ans"]
            horizon_days = {
                "1 journée": 1,
                "1 semaine": 7,
                "1 mois": 30,
                "3 mois": 90,
                "6 mois": 180,
                "1 an": 365,
                "5 ans": 1825
            }
            
            for i, ticker in enumerate(selected_tickers):
                with tabs[i]:
                    st.markdown(f"### Détails pour **{ticker}**")
                    
                    # Récupération des données complètes pour le ticker
                    df_ticker = df_full[df_full['shortname'] == ticker].copy()
                    if df_ticker.empty:
                        st.warning(f"Aucune donnée pour {ticker}.")
                        continue
                    
                    # Sélection de l'horizon temporel
                    horizon_choice = st.radio(
                        "Sélectionnez l'horizon temporel",
                        horizon_options,
                        index=2,  # Par défaut : "1 mois"
                        key=f"horizon_{ticker}"
                    )
                    days = horizon_days[horizon_choice]
                    last_date = df_ticker['date'].max()
                    start_date = last_date - pd.Timedelta(days=days)
                    df_horizon = df_ticker[df_ticker['date'] >= start_date].sort_values(by='date')
                    
                    if df_horizon.empty:
                        st.warning("Aucune donnée disponible pour cet horizon.")
                        continue
                    
                    # 1) Évolution du prix de clôture
                    # 1) Évolution du prix de clôture + Moyennes Mobiles
                    st.markdown("**Évolution du prix de clôture**")

                    # Calcul des moyennes mobiles
                    df_horizon['ma30']  = df_horizon['close'].rolling(window=30).mean()
                    df_horizon['ma90']  = df_horizon['close'].rolling(window=90).mean()
                    df_horizon['ma120'] = df_horizon['close'].rolling(window=120).mean()

                    # Cases à cocher pour afficher les MA
                    cm1, cm2, cm3 = st.columns(3)
                    show_ma30  = cm1.checkbox("Afficher MA 30 jours",  key=f"ma30_{ticker}")
                    show_ma90  = cm2.checkbox("Afficher MA 90 jours",  key=f"ma90_{ticker}")
                    show_ma120 = cm3.checkbox("Afficher MA 120 jours", key=f"ma120_{ticker}")

                    # Préparation des colonnes à tracer
                    chart_cols = ['close']
                    if show_ma30:  chart_cols.append('ma30')
                    if show_ma90:  chart_cols.append('ma90')
                    if show_ma120: chart_cols.append('ma120')

                    # Affichage du graphique
                    st.line_chart(
                        df_horizon.set_index('date')[chart_cols],
                        height=300
                    )
                    
                    # 2) Volatilité sur 7 jours
                    df_horizon['volatility'] = df_horizon['close'].rolling(window=7).std()
                    st.markdown("**Volatilité sur 7 jours**")
                    st.line_chart(df_horizon.set_index('date')['volatility'])
                    
                    # 3) Volume des transactions
                    st.markdown("**Volume des transactions**")
                    st.bar_chart(df_horizon.set_index('date')['volume'])
                    
                    # 4) Informations clés
                    st.markdown("### Informations clés")
                    
                    # Récupération de la dernière ligne et de l'avant-dernière pour certains indicateurs
                    last_row = df_ticker.iloc[-1] if not df_ticker.empty else None
                    prev_row = df_ticker.iloc[-2] if len(df_ticker) > 1 else None
                    
                    previous_close = round(prev_row['close'], 2) if prev_row is not None else None
                    open_price = round(last_row['open'], 2) if last_row is not None else None
                    volume_latest = int(last_row['volume']) if last_row is not None else None
                    
                    # Moyenne des volumes sur 30 jours
                    df_last30 = df_ticker[df_ticker['date'] >= (last_date - pd.Timedelta(days=30))]
                    avg_volume = int(df_last30['volume'].mean()) if not df_last30.empty else None
                    
                    # Day's Range (min et max de la dernière journée)
                    if last_row is not None:
                        days_range = f"{round(last_row['low'], 2)} - {round(last_row['high'], 2)}"
                    else:
                        days_range = None
                    
                    # 52 Week Range
                    one_year_ago = last_date - pd.Timedelta(days=365)
                    df_52weeks = df_ticker[df_ticker['date'] >= one_year_ago]
                    if not df_52weeks.empty:
                        min_52 = round(df_52weeks['low'].min(), 2)
                        max_52 = round(df_52weeks['high'].max(), 2)
                        range_52_weeks = f"{min_52} - {max_52}"
                    else:
                        range_52_weeks = None
                    
                    # Quelques placeholders pour d’autres attributs
                    market_cap_intraday = "2.694T"
                    beta_5y = "1.76"
                    pe_ratio_ttm = "37.56"
                    eps_ttm = "2.94"
                    forward_div_yield = "0.04 (0.04%)"
                    bid = "110.03 x 1300"
                    ask = "110.05 x 400"
                    earnings_date = "May 28, 2025"
                    ex_div_date = "Mar 12, 2025"
                    target_est_1y = "171.01"
                    
                    colA, colB = st.columns(2)
                    with colA:
                        st.write(f"**Nom de l'entreprise:** {ticker}")
                        st.write(f"**Previous Close:** {previous_close if previous_close else 'N/A'}")
                        st.write(f"**Open:** {open_price if open_price else 'N/A'}")
                        st.write(f"**Day's Range:** {days_range if days_range else 'N/A'}")
                        st.write(f"**52 Week Range:** {range_52_weeks if range_52_weeks else 'N/A'}")
                        st.write(f"**Volume:** {volume_latest if volume_latest else 'N/A'}")
                        st.write(f"**Avg Volume:** {avg_volume if avg_volume else 'N/A'}")
                    with colB:
                        st.write(f"**Market Cap (intraday):** {market_cap_intraday}")
                        st.write(f"**Beta (5Y Monthly):** {beta_5y}")
                        st.write(f"**PE Ratio (TTM):** {pe_ratio_ttm}")
                        st.write(f"**EPS (TTM):** {eps_ttm}")
                        st.write(f"**Earnings Date:** {earnings_date}")
                        st.write(f"**Forward Dividend & Yield:** {forward_div_yield}")
                        st.write(f"**Ex-Dividend Date:** {ex_div_date}")
                        st.write(f"**1y Target Est:** {target_est_1y}")
                    
                    st.markdown("---")
        else:
            st.info("Sélectionnez au moins une entreprise pour voir les détails.")
    
    else:
        st.info("Aucune donnée disponible.")
        
except Exception as e:
    st.error(f"Erreur lors de la connexion à la base de données : {e}")
