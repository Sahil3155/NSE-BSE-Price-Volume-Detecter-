# System Architecture

## Architecture Diagram

```mermaid
flowchart TD
    subgraph Data Sources
        NSE[NSE Bhavcopy CSV / ZIP]
        BSE[BSE Bhavcopy CSV / ZIP]
        SEBI[SEBI Enforcement Weak Labels]
    end

    subgraph Data Pipeline
        LDR[Exchange Loaders & Schema Detector]
        CLN[Validation & Cleaning Pipeline]
        ENG[Feature Engineering Engine]
        LDR --> CLN --> ENG
    end

    subgraph Surveillance ML Engine
        IF[Isolation Forest Model]
        LSTM[PyTorch LSTM Autoencoder]
        RULE[Deterministic Microstructure Rules]
        HYB[Hybrid Risk Scoring & Explainability]
        ENG --> IF
        ENG --> LSTM
        ENG --> RULE
        IF --> HYB
        LSTM --> HYB
        RULE --> HYB
    end

    subgraph Storage Layer
        DB[(PostgreSQL / SQLite Database)]
        MODELS[(Trained Model Weights & Scalers)]
    end

    subgraph Backend APIs
        FAST[FastAPI REST Service]
        FAST --> DB
        FAST --> HYB
    end

    subgraph Frontend Surveillance UI
        UI[React 18 + Vite + TypeScript + Recharts]
        UI -->|HTTP / JSON| FAST
    end

    NSE --> LDR
    BSE --> LDR
    SEBI --> LDR
    ENG --> DB
    HYB --> DB
    IF --> MODELS
    LSTM --> MODELS
```

---

## Component Separation of Concerns
1. **Data Ingestion (`backend/data_pipeline/ingestion/`):** Exchange-specific adapters for NSE (legacy and UDiFF format) and BSE, plus SEBI weak-label ingestion.
2. **Preprocessing (`backend/data_pipeline/preprocessing/`):** Validation of OHLC price bounds ($High \ge Low, High \ge Open, High \ge Close$), date parsing, deduplication, and `TimeSeriesNormalizer`.
3. **Feature Engineering (`backend/data_pipeline/feature_engineering/`):** 16 core price, volume, and microstructure features computed with zero look-ahead bias.
4. **Machine Learning (`backend/ml/`):** Isolation Forest and PyTorch LSTM Autoencoder trained with chronological data splits.
5. **Backend REST API (`backend/app/`):** Modular FastAPI routers using Pydantic schemas, dependency injection, and SQLAlchemy 2.0 ORM.
6. **Frontend UI (`frontend/`):** Dark financial terminal styled with Tailwind CSS, Recharts, and TypeScript.
