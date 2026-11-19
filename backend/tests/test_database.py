"""Integration tests for database persistence, services, and queries."""

from backend.app.database.connection import SessionLocal
from backend.app.services.stock_service import get_all_stocks, get_stock_by_symbol, get_stock_history
from backend.app.services.market_data_service import get_market_data_summary
from backend.app.services.detection_service import run_surveillance_detection
from backend.app.services.alert_service import get_alerts, update_alert_status
from backend.app.services.analytics_service import get_surveillance_overview, get_model_comparison_benchmark
from backend.app.schemas.detection import DetectionRunRequest
from backend.app.schemas.alert import AlertStatusUpdate


def test_database_stocks_and_history():
    """Verify stock listing and historical data retrieval."""
    db = SessionLocal()
    try:
        stocks = get_all_stocks(db, exchange_code="NSE")
        assert len(stocks) >= 2
        symbols = [s.symbol for s in stocks]
        assert "PUMPDUMP_SUSPECT" in symbols
        assert "SMALLCAP_NORM1" in symbols

        history = get_stock_history(db, "PUMPDUMP_SUSPECT")
        assert history is not None
        assert history.total_records >= 60
        assert history.history[0].close > 0
    finally:
        db.close()


def test_market_data_summary():
    """Verify aggregated dataset counts and date ranges."""
    db = SessionLocal()
    try:
        summary = get_market_data_summary(db)
        assert summary.total_stocks >= 2
        assert summary.total_market_records >= 120
        assert summary.total_featured_records >= 120
        assert summary.latest_trading_date is not None
    finally:
        db.close()


def test_detection_service_and_alerts():
    """Verify running surveillance on database data and updating alert status."""
    db = SessionLocal()
    try:
        req = DetectionRunRequest(exchange="NSE", symbol="PUMPDUMP_SUSPECT")
        res = run_surveillance_detection(db, req)
        assert res.status == "SUCCESS"
        assert res.records_analyzed >= 60
        assert res.anomalies_detected > 0

        # Query generated alerts
        alerts = get_alerts(db, risk_level="HIGH")
        assert len(alerts) > 0
        target_alert = alerts[0]

        # Update alert status
        up = update_alert_status(
            db, target_alert.id, AlertStatusUpdate(status="INVESTIGATING", investigator_notes="Assigned to surveillance desk.")
        )
        assert up is not None
        assert up.status == "INVESTIGATING"
        assert up.investigator_notes == "Assigned to surveillance desk."
    finally:
        db.close()


def test_analytics_and_model_benchmarks():
    """Verify overview statistics and model comparison calculations."""
    db = SessionLocal()
    try:
        overview = get_surveillance_overview(db)
        assert overview["total_stocks_monitored"] >= 2
        assert overview["high_risk_alerts"] > 0
        assert len(overview["highest_anomaly_stocks"]) > 0

        benchmarks = get_model_comparison_benchmark()
        assert len(benchmarks) == 4
        model_names = [b["model_name"] for b in benchmarks]
        assert "Hybrid Surveillance Engine" in model_names
        assert "Isolation Forest" in model_names
        assert "LSTM Autoencoder" in model_names
    finally:
        db.close()
