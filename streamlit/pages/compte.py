import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from datetime import date  # pour le date picker

st.title("Construction de votre portefeuille")

# ------------------------------------------------------------------
# Sélecteur de date en haut à droite
# ------------------------------------------------------------------
# On crée deux colonnes larges pour placer le picker à droite
col_left, col_middle, col_right = st.columns([3, 4, 3])
with col_right:
    selected_date = st.date_input(
        "Date des données",
        value=date.today(),
        key="selected_date"
    )
with col_left:
# Bouton de déconnexion
    if st.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

# Connexion à la BDD PostgreSQL
@st.cache_resource(show_spinner=False)
def get_connection():
    return psycopg2.connect(
        host="db",
        database="stocks_db",
        user="postgres",
        password="postgres"
    )
conn = get_connection()

# Récupération de la liste des tickers
@st.cache_data(ttl=600)
def get_ticker_list(_conn):
    query = "SELECT DISTINCT ticker FROM stock_prices WHERE date <= %s ORDER BY ticker;"
    df = pd.read_sql(query, _conn, params=(selected_date,))
    return df["ticker"].tolist()
ticker_list = get_ticker_list(conn)

# -----------------------------------------------------------------
# Fonctions de recommandation avec prise en compte de selected_date
# -----------------------------------------------------------------

def get_stock_name(conn, ticker):
    try:
        query = "SELECT shortname FROM stocks WHERE ticker = %s LIMIT 1;"
        df = pd.read_sql(query, conn, params=(ticker,))
        if not df.empty:
            return df.iloc[0]["shortname"]
    except Exception as e:
        st.error(f"Erreur pour le ticker {ticker} : {e}")
    return None

def get_moving_average_recommendations(conn, tickers, as_of_date):
    """
    Stratégie Moyennes Mobiles simples :
    - On récupère 90 jours de cours (ou plus) pour chaque ticker.
    - On calcule MA10 et MA90.
    - On génère un signal d'achat si, à la date sélectionnée, MA10 > MA90.
    - On limite à 10 recommandations au maximum.
    """
    recommendations = []
    for ticker in tickers:
        # récupérer au moins 90 jours avant la date sélectionnée
        query = """
        SELECT date, close
        FROM stock_prices
        WHERE ticker = %s
          AND date <= %s
        ORDER BY date DESC
        LIMIT 90;
        """
        df = pd.read_sql(query, conn, params=(ticker, as_of_date))
        # on ne considère que les titres ayant 90 jours de données
        if df.shape[0] < 90:
            continue

        # trier par ordre chronologique
        df = df.sort_values("date")
        # calcul des moyennes mobiles
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma90'] = df['close'].rolling(window=90).mean()

        latest = df.iloc[-1]
        # signal d'achat pur : MA10 > MA90
        if pd.notnull(latest['ma10']) and pd.notnull(latest['ma90']) and latest['ma10'] > latest['ma90']:
            recommendations.append({
                "ticker": ticker,
                "name": get_stock_name(conn, ticker)
            })
            if len(recommendations) >= 10:
                break

    return recommendations

def get_momentum_recommendations(conn, tickers, as_of_date):
    results = []
    for ticker in tickers:
        query = """
        SELECT date, close
        FROM stock_prices
        WHERE ticker = %s
          AND date <= %s
        ORDER BY date DESC
        LIMIT 11;
        """
        df = pd.read_sql(query, conn, params=(ticker, as_of_date))
        if df.shape[0] < 11:
            continue
        df = df.sort_values("date")
        df["return"] = df["close"].pct_change()
        last5 = df["return"].iloc[-5:]
        if not (last5 > 0).all():
            continue
        first_price = df["close"].iloc[0]
        last_price  = df["close"].iloc[-1]
        momentum = (last_price / first_price) - 1 if first_price > 0 else 0
        results.append({
            "ticker": ticker,
            "name": get_stock_name(conn, ticker),
            "momentum": momentum
        })
        if len(results) >= 10:
            break
    return sorted(results, key=lambda x: x["momentum"], reverse=True)[:10]

# -----------------------------------------------------------------
# Récupération du dernier cours à la date sélectionnée
# -----------------------------------------------------------------
def get_latest_cost(conn, ticker, as_of_date):
    query = """
    SELECT close
    FROM stock_prices
    WHERE ticker = %s
      AND date <= %s
    ORDER BY date DESC
    LIMIT 1;
    """
    df = pd.read_sql(query, conn, params=(ticker, as_of_date))
    return df["close"].iloc[0] if not df.empty else None

# -----------------------------------------------------------------
# Gestion du DataFrame de portefeuille en session_state
# -----------------------------------------------------------------
if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = pd.DataFrame(
        columns=["id", "Ticker", "Nombre d'actions", "Coût récent", "Valeur de la position"]
    )

def generate_id():
    df = st.session_state["portfolio"]
    return 0 if df.empty else df["id"].max() + 1

# Ajout de ligne
col_add, _ = st.columns([3, 7])
with col_add:
    if st.button("Ajouter une ligne"):
        new_id = generate_id()
        new_row = pd.DataFrame([{
            "id": new_id,
            "Ticker": "",
            "Nombre d'actions": 0,
            "Coût récent": None,
            "Valeur de la position": None
        }])
        st.session_state["portfolio"] = pd.concat(
            [st.session_state["portfolio"], new_row],
            ignore_index=True
        )
        st.rerun()

# Édition via AgGrid
df_for_grid = st.session_state["portfolio"]
if df_for_grid.empty:
    df_for_grid = pd.DataFrame([{
        "id": 0, "Ticker": "", "Nombre d'actions": 0,
        "Coût récent": None, "Valeur de la position": None
    }])

gb = GridOptionsBuilder.from_dataframe(df_for_grid)
gb.configure_column("id", hide=True)
gb.configure_column("Ticker", editable=True,
                    cellEditor="agSelectCellEditor", cellEditorParams={"values": ticker_list})
gb.configure_column("Nombre d'actions", editable=True, type=["numericColumn"])
gb.configure_column("Coût récent", editable=False)
gb.configure_column("Valeur de la position", editable=False)
gridOptions = gb.build()
gridOptions["columnDefs"].insert(0, {
    "headerName": "", "field": "checkbox",
    "checkboxSelection": True, "headerCheckboxSelection": True,
    "pinned": "left", "width": 50, "suppressMenu": True
})
gridOptions["rowSelection"] = "multiple"
gridOptions["suppressRowClickSelection"] = True

grid_response = AgGrid(
    st.session_state["portfolio"],
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    reload_data=False,
    height=300,
    rowSelection="multiple"
)

edited_df = pd.DataFrame(grid_response.get("data", [])).drop(columns=["checkbox"], errors="ignore")

# Suppression de ligne
selectbox_container = st.empty()
if not st.session_state["portfolio"].empty:
    ticker_options = st.session_state["portfolio"]["Ticker"].tolist()
    selected_ticker = selectbox_container.selectbox(
        "Sélectionnez le Ticker à supprimer",
        options=ticker_options,
        key="delete_select"
    )
    if st.button("Effacer la ligne sélectionnée"):
        df = st.session_state["portfolio"]
        st.session_state["portfolio"] = df[df["Ticker"] != selected_ticker].reset_index(drop=True)
        st.rerun()
else:
    selectbox_container.write("Aucune ligne disponible pour suppression.")

# Mise à jour des coûts et valeurs
new_rows = []
for _, row in edited_df.iterrows():
    ticker = row.get("Ticker")
    shares = int(row.get("Nombre d'actions", 0)) if row.get("Nombre d'actions") else 0
    if ticker and shares > 0:
        latest_cost = get_latest_cost(conn, ticker, selected_date)
        value_pos = round(shares * latest_cost, 2) if latest_cost is not None else None
    else:
        latest_cost, value_pos = None, None
    new_rows.append({
        "id": row.get("id"),
        "Ticker": ticker,
        "Nombre d'actions": shares,
        "Coût récent": latest_cost,
        "Valeur de la position": value_pos
    })

new_df = pd.DataFrame(new_rows)
if not new_df.equals(st.session_state["portfolio"]):
    st.session_state["portfolio"] = new_df
    st.rerun()

# -----------------------------------------------------------------
# Affichage graphique et tableau si le portefeuille n'est pas vide
# -----------------------------------------------------------------
if not st.session_state["portfolio"].empty:
    # Récupération des données pour chaque ticker à la date sélectionnée
    prtf_tickers = st.session_state["portfolio"]["Ticker"].unique()
    dfs_list = []
    query = """
        SELECT sp.ticker, sp.date, sp.open, sp.high, sp.low, sp.close,
               s.shortname, s.marketcap, s.trailingpe, s.pricetobook
        FROM stock_prices AS sp
        JOIN stocks AS s ON sp.ticker = s.ticker
        WHERE sp.ticker = %s
          AND sp.date <= %s
    """
    for ticker in prtf_tickers:
        df_temp = pd.read_sql(query, conn, params=(ticker, selected_date))
        dfs_list.append(df_temp)
    df_prtf = pd.concat(dfs_list, ignore_index=True)
    df_prtf["info"] = df_prtf["ticker"].apply(lambda t: f"https://finance.yahoo.com/quote/{t}")
    latest_data = df_prtf.loc[
        df_prtf.groupby('ticker')['date'].idxmax(),
        ['ticker','shortname','info','close','marketcap','trailingpe','pricetobook']
    ]

    # Sélecteur de tickers et MA
    all_tickers = df_prtf['ticker'].unique().tolist()
    selected_tickers = st.multiselect(
        "Choisissez les actions à afficher",
        all_tickers, default=all_tickers, key="multiselect_tickers"
    )
    ma1, ma2, ma3 = st.columns(3)
    show_ma30 = ma1.checkbox("MA 30 jours", key="ma30")
    show_ma90 = ma2.checkbox("MA 90 jours", key="ma90")
    show_ma120 = ma3.checkbox("MA 120 jours", key="ma120")

    # Graphe & camembert
    col_chart, col_pie = st.columns(2)
    with col_chart:
        df_plot = (
            df_prtf[df_prtf['ticker'].isin(selected_tickers)]
            .sort_values(['ticker','date'])
            .drop_duplicates(['ticker','date'])
        )
        for w in (30, 90, 120):
            df_plot[f'ma{w}'] = (
                df_plot.groupby('ticker')['close']
                       .transform(lambda x: x.rolling(w).mean())
            )
        fig = go.Figure()
        for t in selected_tickers:
            dft = df_plot[df_plot['ticker'] == t]
            fig.add_trace(go.Scatter(x=dft['date'], y=dft['close'],
                                     mode='lines', name=f"{t} Close"))
            if show_ma30:
                fig.add_trace(go.Scatter(x=dft['date'], y=dft['ma30'],
                                         mode='lines', name=f"{t} MA30", line=dict(dash='dash')))
            if show_ma90:
                fig.add_trace(go.Scatter(x=dft['date'], y=dft['ma90'],
                                         mode='lines', name=f"{t} MA90", line=dict(dash='dot')))
            if show_ma120:
                fig.add_trace(go.Scatter(x=dft['date'], y=dft['ma120'],
                                         mode='lines', name=f"{t} MA120", line=dict(dash='longdash')))
        fig.update_layout(title="Variations du prix des actions",
                          xaxis_title="Date", yaxis_title="Close Price")
        st.plotly_chart(fig)

    with col_pie:
        total_value = st.session_state["portfolio"]["Valeur de la position"].sum().round(2)
        fig2 = px.pie(
            st.session_state["portfolio"],
            values="Valeur de la position",
            names="Ticker",
            title=f"Portefeuille total : ${total_value}",
            hole=0.3
        )
        st.plotly_chart(fig2)

    # Tableau full-width
    st.data_editor(
        latest_data,
        column_config={
            "info":        st.column_config.LinkColumn("Infos", display_text="Voir sur Yahoo Finance"),
            "close":       st.column_config.NumberColumn("Lastest close", format="$%.2f"),
            "marketcap":   st.column_config.NumberColumn("Market cap",    format="$%d"),
            "trailingpe":  st.column_config.NumberColumn("Trailing P/E", format="$%.2f"),
            "pricetobook": st.column_config.NumberColumn("P/B Ratio",     format="$%.2f"),
        },
        hide_index=True,
    )

# -----------------------------------------------------------------
# Onglets de recommandations
# -----------------------------------------------------------------
st.subheader("Stratégies de recommandation de portefeuille")
tab_ma, tab_mom = st.tabs(["Moyennes Mobiles", "Momentum"])

with tab_ma:
    st.subheader("Recommandations Moyennes Mobiles")

    # Spinner pendant le calcul
    with st.spinner("Calcul des moyennes mobiles…"):
        # 1) Calcul MA10 et MA90 pour chaque ticker
        metrics = []
        for ticker in ticker_list:
            df = pd.read_sql(
                """
                SELECT date, close
                FROM stock_prices
                WHERE ticker = %s
                  AND date <= %s
                ORDER BY date DESC
                LIMIT 90;
                """,
                conn,
                params=(ticker, selected_date)
            )
            if df.shape[0] < 90:
                continue
            df = df.sort_values("date")
            df["ma10"] = df["close"].rolling(window=10).mean()
            df["ma90"] = df["close"].rolling(window=90).mean()
            latest = df.iloc[-1]
            metrics.append({
                "Ticker": ticker,
                "Nom": get_stock_name(conn, ticker),
                "MA10": latest["ma10"],
                "MA90": latest["ma90"],
                "signal": latest["ma10"] > latest["ma90"]
            })

        # 2) Filtrer uniquement les signaux d'achat
        df_signal = pd.DataFrame(metrics)
        df_signal = df_signal[df_signal["signal"]].copy()

    # 3) Affichage du tableau filtré
    if df_signal.empty:
        st.write("Aucun signal d'achat (MA10 > MA90) trouvé.")
    else:
        df_signal["Signal"] = "ACHAT"
        display_df = df_signal[["Ticker", "Nom", "MA10", "MA90", "Signal"]]
        display_df = display_df.rename(columns={
            "Ticker":    "Symbole",
            "Nom":       "Entreprise",
            "MA10":      "Moyenne Mobile 10j",
            "MA90":      "Moyenne Mobile 90j",
            "Signal":    "Signal d'achat"
        })
    styled = display_df.style.applymap(
        lambda _: "color: green;", subset=["Signal d'achat"]
    )
    st.dataframe(styled, use_container_width=True)


with tab_mom:
    st.subheader("Recommandations Momentum")
    with st.spinner("Calcul des recommandations momentum en cours…"):
        rec_mom = get_momentum_recommendations(conn, ticker_list, selected_date)

    if rec_mom:
        rows = []
        for rec in rec_mom:
            ticker = rec["ticker"]
            name   = rec["name"]
            query = """
            SELECT date, close
            FROM stock_prices
            WHERE ticker = %s
              AND date <= %s
            ORDER BY date DESC
            LIMIT 6;
            """
            df_tmp = pd.read_sql(query, conn, params=(ticker, selected_date))
            df_tmp = df_tmp.sort_values("date")
            df_tmp["return"] = df_tmp["close"].pct_change()
            rets = df_tmp["return"].iloc[-5:].tolist()

            row = {"Ticker": ticker, "Nom": name}
            for i, r in enumerate(rets, start=1):
                row[f"Rdt_{i}"] = r
            rows.append(row)

        # 1) Création du DataFrame
        df_mom = pd.DataFrame(rows)

        # 2) Renommage des colonnes Rdt_i → Rendement t-(6-i)
        rename_map = {f"Rdt_{i}": f"Rendement t-{6-i}" for i in range(1, 6)}
        df_mom = df_mom.rename(columns=rename_map)

        # 3) Affichage
        st.dataframe(df_mom, use_container_width=True)

    else:
        st.write("Aucune recommandation momentum.")

