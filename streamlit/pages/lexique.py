import streamlit as st

st.title("Lexique des termes en finance")

lexique = {
    "Portefeuille": "Ensemble des actifs financiers détenus par un investisseur (actions, obligations, liquidités, etc.).",
    "Asset Allocation (Répartition d'actifs)": "Processus de diversification des investissements entre différentes classes d'actifs pour optimiser le rendement et gérer le risque.",
    "Diversification": "Répartition des investissements sur plusieurs actifs afin de réduire l'impact négatif de la sous-performance d’un seul.",
    "Risque": "Mesure de l’incertitude associée aux rendements futurs d’un investissement, souvent lié à la volatilité.",
    "Volatilité": "Indicateur de la fluctuation des prix d’un actif sur une période donnée, reflétant le niveau de risque.",
    "Rendement": "Gain ou perte réalisé sur un investissement sur une période donnée, exprimé en pourcentage.",
    "Bêta": "Mesure de la sensibilité d’un actif par rapport aux mouvements du marché global ; un bêta supérieur à 1 indique une plus grande volatilité que le marché.",
    "Alpha": "Indicateur de la performance d’un investissement par rapport à un indice de référence, reflétant la valeur ajoutée par le gestionnaire de portefeuille.",
    "Benchmark": "Indice ou référence utilisé pour comparer la performance d’un portefeuille ou d’un fonds.",
    "Liquidité": "Capacité d’un actif à être rapidement vendu ou acheté sans impacter significativement son prix.",
    "Effet de levier": "Utilisation de capitaux empruntés pour augmenter la capacité d’investissement et potentiellement amplifier les gains (ou les pertes).",
    "Actions": "Titres de propriété représentant une part du capital d’une entreprise, donnant droit à des dividendes et à une participation dans la gouvernance.",
    "Obligations": "Titres de créance émis par des entreprises ou des gouvernements, représentant un emprunt avec un taux d’intérêt fixe ou variable.",
    "ETF (Fonds Négocié en Bourse)": "Fonds d’investissement répliquant la performance d’un indice et négocié en bourse comme une action.",
    "Fonds Commun de Placement": "Structure d’investissement collectif permettant à plusieurs investisseurs de regrouper leurs ressources pour investir dans un portefeuille diversifié.",
    "Indice Boursier": "Agrégat statistique reflétant la performance d’un ensemble d’actions (ex. CAC 40, S&P 500).",
    "Capitalisation Boursière": "Valeur totale de toutes les actions en circulation d’une entreprise, calculée en multipliant le nombre d’actions par le cours de l’action.",
    "Analyse Fondamentale": "Évaluation de la valeur intrinsèque d’un actif en se basant sur ses fondamentaux économiques (bilan, compte de résultat, perspectives de croissance).",
    "Analyse Technique": "Étude des graphiques et des tendances de marché afin de prédire les mouvements futurs des prix.",
    "Gestion Passive": "Stratégie visant à reproduire la performance d’un indice de référence plutôt qu’à le battre, souvent via des ETF ou des fonds indiciels.",
    "Gestion Active": "Stratégie où le gestionnaire cherche à surpasser le marché par des choix d’investissement ciblés et opportunistes.",
    "Spread": "Différence entre le prix d’achat (bid) et le prix de vente (ask) d’un actif, souvent indicateur de sa liquidité.",
    "Arbitrage": "Stratégie consistant à profiter des écarts de prix sur différents marchés ou produits financiers pour réaliser un profit sans risque.",
    "Hedging (Couverture)": "Technique utilisée pour réduire ou compenser le risque de fluctuation des prix d’un actif grâce à des instruments dérivés ou des positions opposées.",
    "Volatilité Implicite": "Estimation de la volatilité future d’un actif, déduite des prix des options sur ce même actif."
}

for terme, definition in lexique.items():
    st.markdown(f"- **{terme}** : {definition}")
