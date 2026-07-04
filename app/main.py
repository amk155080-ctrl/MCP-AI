from fastapi import FastAPI
from app.api.v8_daily_report_log import router as v8_daily_report_log_router

from app.api.health import router as health_router
from app.api.ranking import router as ranking_router

from app.api.v2.market import router as market_v2_router
from app.api.v2.semiconductor import router as semiconductor_v2_router
from app.api.v3.ranking import router as ranking_v3_router
from app.api.v14_asset import router as v14_asset_router
from app.api.v15_family_asset import router as v15_family_asset_router
from app.api.v15_auction_asset import (
    router as v15_auction_asset_router
)
from app.api.v15_auction_ai import (
    router as v15_auction_ai_router
)
from app.api.v15_auction_portfolio import router as v15_auction_portfolio_router
from app.api.v15_auction_risk import router as v15_auction_risk_router
from app.api.v15_auction_report import router as v15_auction_report_router
from app.api.v15_auction_engine import router as v15_auction_engine_router
from app.api.v15_auction_rights import router as v15_auction_rights_router
from app.api.v15_auction_import import router as v15_auction_import_router
from app.api.v16_document import router as v16_document_router
from app.api import rights_ai
from app.api.v19_cases import router as v19_cases_router
from app.api.v16_rights_v2 import router as v16_rights_v2_router

app = FastAPI(title="MCP 4.0 v1", version="1.0.0")

app.include_router(health_router)
app.include_router(ranking_router)

app.include_router(market_v2_router)
app.include_router(semiconductor_v2_router)
app.include_router(ranking_v3_router)
app.include_router(v14_asset_router)
app.include_router(v15_family_asset_router)
app.include_router(
    v15_auction_ai_router
)
app.include_router(v15_auction_portfolio_router)
app.include_router(v15_auction_risk_router)
app.include_router(v15_auction_report_router)
app.include_router(v15_auction_engine_router)
app.include_router(v15_auction_rights_router)
app.include_router(v15_auction_import_router)
app.include_router(v16_document_router)
app.include_router(rights_ai.router)
app.include_router(rights_ai.router)
app.include_router(v19_cases_router)
app.include_router(v16_rights_v2_router)

from app.api.v3.portfolio import router as portfolio_v3_router
app.include_router(portfolio_v3_router)
from app.api.v3.risk import router as risk_v3_router
app.include_router(risk_v3_router)
from app.api.v3.backtest import router as backtest_v3_router
app.include_router(backtest_v3_router)

from app.api.institutional import router as institutional_router
app.include_router(institutional_router)

from app.api.v4_ranking import router as ranking_v4_router
app.include_router(ranking_v4_router)

from app.api.v4_flow import router as flow_v4_router
app.include_router(flow_v4_router)

from app.api.v4_quality import router as quality_router
app.include_router(quality_router)

from app.api.v4_holding import router as holding_v4_router
app.include_router(holding_v4_router)

from app.api.v4_portfolio import router as portfolio_v4_recommend_router
app.include_router(portfolio_v4_recommend_router)

from app.api.v5_flow import router as flow_v5_router
app.include_router(flow_v5_router)

from app.api.v5_advisor import router as advisor_v5_router
app.include_router(advisor_v5_router)

from app.api.v5_backtest import router as backtest_v5_router
app.include_router(backtest_v5_router)

from app.api.v5_signal import router as signal_v5_router
app.include_router(signal_v5_router)

from app.api.v5_portfolio_optimize import router as portfolio_optimize_v5_router
app.include_router(portfolio_optimize_v5_router)

from app.api.v6_committee import router as committee_v6_router
app.include_router(committee_v6_router)

from app.api.v6_buy_priority import router as buy_priority_v6_router
app.include_router(buy_priority_v6_router)

from app.api.v6_entry_check import router as entry_check_v6_router
app.include_router(entry_check_v6_router)

from app.api.v6_position_size import router as position_size_v6_router
app.include_router(position_size_v6_router)

from app.api.v6_order_plan import router as order_plan_v6_router
app.include_router(order_plan_v6_router)

from app.api.v6_order_risk_check import router as order_risk_check_v6_router
app.include_router(order_risk_check_v6_router)

from app.api.v6_order_safe_plan import router as order_safe_plan_v6_router
app.include_router(order_safe_plan_v6_router)

from app.api.v6_execution_summary import router as execution_summary_v6_router
app.include_router(execution_summary_v6_router)

from app.api.v6_execution_save import router as execution_save_v6_router
app.include_router(execution_save_v6_router)

from app.api.v6_execution_logs import router as execution_logs_v6_router
app.include_router(execution_logs_v6_router)

from app.api.v7_dashboard import router as dashboard_v7_router
app.include_router(dashboard_v7_router)

from app.api.v7_dashboard_summary_text import router as dashboard_summary_text_v7_router
app.include_router(dashboard_summary_text_v7_router)

from app.api.v7_dashboard_kakao import router as dashboard_kakao_v7_router
app.include_router(dashboard_kakao_v7_router)

from app.api.v7_dashboard_html import router as dashboard_html_router
app.include_router(dashboard_html_router)

from app.api.v7_chart_data import router as chart_data_v7_router
app.include_router(chart_data_v7_router)

from app.api.v7_stock_detail import router as stock_detail_router
app.include_router(stock_detail_router)

from app.api.v8_monitor import router as monitor_v8_router
app.include_router(monitor_v8_router)

from app.api.v8_alert import router as alert_v8_router
app.include_router(alert_v8_router)

from app.api.v8_alert_log import router as alert_log_v8_router
app.include_router(alert_log_v8_router)

from app.api.v8_daily_report import router as daily_report_v8_router
app.include_router(daily_report_v8_router)

from app.api.v8_report_save import router as report_save_v8_router
app.include_router(report_save_v8_router)

app.include_router(v8_daily_report_log_router)

from app.api.v8_daily_report_log import router as v8_daily_report_log_router

from app.api.v8_report_html import router as report_html_v8_router
app.include_router(report_html_v8_router)

from app.api.v9_quote import router as quote_v9_router
app.include_router(quote_v9_router)

from app.api.v9_portfolio_evaluate import router as portfolio_evaluate_v9_router
app.include_router(portfolio_evaluate_v9_router)

from app.api.v9_target_check import router as target_check_v9_router
app.include_router(target_check_v9_router)

from app.api.v9_stop_check import router as stop_check_v9_router
app.include_router(stop_check_v9_router)

from app.api.v9_position_monitor import router as position_monitor_v9_router
app.include_router(position_monitor_v9_router)

from app.api.v9_position_monitor_html import router as position_monitor_html_router
app.include_router(position_monitor_html_router)

from app.api.v9_signal_engine import router as signal_engine_v9_router
app.include_router(signal_engine_v9_router)

from app.api.v9_signal_save import router as signal_save_v9_router
app.include_router(signal_save_v9_router)

from app.api.v9_signal_logs import router as signal_logs_v9_router
app.include_router(signal_logs_v9_router)

from app.api.v9_signal_stats import router as signal_stats_v9_router
app.include_router(signal_stats_v9_router)

from app.api.v10_order_prepare import router as order_prepare_v10_router
app.include_router(order_prepare_v10_router)

from app.api.v10_order_queue import router as order_queue_v10_router
app.include_router(order_queue_v10_router)

from app.api.v10_order_approve import router as order_approve_v10_router
app.include_router(order_approve_v10_router)

from app.api.v10_order_cancel import router as order_cancel_v10_router
app.include_router(order_cancel_v10_router)

from app.api.v10_order_status import router as order_status_v10_router
app.include_router(order_status_v10_router)

from app.api.v10_order_stats import router as order_stats_v10_router
app.include_router(order_stats_v10_router)

from app.api.v11_kis_auth import router as kis_auth_v11_router
app.include_router(kis_auth_v11_router)

from app.api.v11_kis_balance import router as kis_balance_v11_router
app.include_router(kis_balance_v11_router)

from app.api.v11_kis_positions import router as kis_positions_v11_router
app.include_router(kis_positions_v11_router)

from app.api.v11_kis_trading import router as kis_trading_v11_router
app.include_router(kis_trading_v11_router)

from app.api.v12_auto_trading import router as auto_trading_v12_router
app.include_router(auto_trading_v12_router)

from app.api.v12_dashboard import router as dashboard_v12_router
app.include_router(dashboard_v12_router)

from app.api.v12_scheduler_api import router as scheduler_v12_router
app.include_router(scheduler_v12_router)

from app.api.v12_performance import router as performance_v12_router
app.include_router(performance_v12_router)

from app.api.v13_ai_advisor import router as ai_advisor_v13_router
app.include_router(ai_advisor_v13_router)

app.include_router(
    v15_auction_asset_router
)
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "MCP AI",
        "message": "MCP cloud server is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "MCP Cloud",
    }

