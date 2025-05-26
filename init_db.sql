DROP TABLE IF EXISTS stock_prices;
DROP TABLE IF EXISTS stocks;
DROP TABLE IF EXISTS marches;
DROP TABLE IF EXISTS macros;
DROP TABLE IF EXISTS secteurs;


-- Table des secteurs (secteurs)
CREATE TABLE secteurs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(255) NOT NULL,
    code INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    parent_id INT DEFAULT NULL,  -- Permet de relier un sous-secteur à un secteur parent
    FOREIGN KEY (parent_id) REFERENCES secteurs(id) ON DELETE SET NULL
);

-- Table des entreprises (stocks)
CREATE TABLE stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    longName VARCHAR(255),
    shortName VARCHAR(255),
    sector VARCHAR(255),
    industry VARCHAR(255),
    country VARCHAR(100),
    fullTimeEmployees INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    zip VARCHAR(20),
    website VARCHAR(255),
    phone VARCHAR(50),
    longBusinessSummary TEXT,
    exchange VARCHAR(50),
    quoteType VARCHAR(50),
    marketCap BIGINT,
    enterpriseValue BIGINT,
    forwardEps FLOAT,
    trailingPE FLOAT,
    dividendRate FLOAT,
    dividendYield FLOAT,
    beta FLOAT,
    priceToBook FLOAT,
    pegRatio FLOAT,
    fiftyDayAverage FLOAT,
    twoHundredDayAverage FLOAT,
    fiftyTwoWeekHigh FLOAT,
    fiftyTwoWeekLow FLOAT,
    "52WeekChange" FLOAT,
    SandP52WeekChange FLOAT,
    sharesOutstanding BIGINT,
    floatShares BIGINT,
    bookValue FLOAT,
    exDividendDate DATE,
    earningsTimestamp BIGINT,
    earningsQuarterlyGrowth FLOAT,
    revenueQuarterlyGrowth FLOAT,
    lastFiscalYearEnd DATE,
    nextFiscalYearEnd DATE,
    mostRecentQuarter DATE,
    shortRatio FLOAT,
    sharesShort BIGINT,
    sharesPercentSharesOut FLOAT,
    priceHint INTEGER,
    regularMarketOpen FLOAT,
    regularMarketDayHigh FLOAT,
    regularMarketDayLow FLOAT,
    regularMarketVolume BIGINT,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT,
    indice VARCHAR(20) DEFAULT 'S&P500',
    historical_start DATE,
    historical_end DATE
);

-- Table des prix des actions (stock_prices)
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) REFERENCES stocks(ticker),
    date DATE NOT NULL,  -- La date journalière (entre historical_start et historical_end)
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume BIGINT
);

-- Table des marchés (marchés)
CREATE TABLE marches (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    localisation VARCHAR(255),
    devise VARCHAR(10)
);

-- Table données macroéconomiques
CREATE TABLE macros (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    GDP FLOAT,
    employment FLOAT,
    CPI FLOAT,
    country VARCHAR(100)
)
