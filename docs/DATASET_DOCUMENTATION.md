# Dataset Documentation

## Data Sources & Schemas

### 1. NSE Bhavcopy (National Stock Exchange)
- **Legacy Format:** `SYMBOL, SERIES, OPEN, HIGH, LOW, CLOSE, LAST, PREVCLOSE, TOTTRDQTY, TOTTRDVAL, TIMESTAMP, TOTALTRADES, ISIN`
- **UDiFF Format:** `TradDt, BizDt, Sgmt, Src, FinInstrmTp, FinInstrmId, ISIN, TckrSymb, SctySrs, OpnPric, HghPric, LwPric, ClsPric, LastPric, PrvsClsgPric, UndrlygPric, SttlmPric, OpnIntrst, ChngInOpnIntrst, TtlTradgVol, TtlTrfVal`
- Automatically mapped to canonical internal schema: `trading_date, exchange, symbol, open, high, low, close, volume, turnover`.

### 2. BSE Bhavcopy (Bombay Stock Exchange)
- Fields: `SC_CODE, SC_NAME, SC_GROUP, SC_TYPE, OPEN, HIGH, LOW, CLOSE, LAST, PREVCLOSE, NO_TRADES, NO_OF_SHRS, NET_TURNOV`
- Date extracted from filename (e.g., `EQ_161123.CSV`) or record column.

### 3. SEBI Enforcement Orders (Weak Labels)
- Fields: `order_id, order_date, stock_symbol, exchange, allegation_type, investigation_start_date, investigation_end_date, source_url, notes`
- Used strictly for evaluating recall and detection lead time.

### 4. Synthetic Benchmark Dataset
- File: `datasets/sample/synthetic_pump_dump_series.csv`
- Explicitly labeled: `dataset_source: SYNTHETIC_BENCHMARK`. Never mixed with live data without origin labels.
