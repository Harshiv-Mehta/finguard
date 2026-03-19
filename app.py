from __future__ import annotations

from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from data_handler import count_recent_expenses, load_transactions, reset_transactions, save_transaction
from model import predict_risky_probability
from risk_engine import assess_transaction_risk
from simulation import simulate_financial_impact


st.set_page_config(
    page_title="FinGuard - AI Financial Safety Net",
    page_icon="🛡️",
    layout="wide",
)


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(14, 165, 233, 0.22), transparent 30%),
                linear-gradient(135deg, #07131f 0%, #0f172a 45%, #13293d 100%);
            color: #e5eef8;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .glass-card {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 22px;
            padding: 1.25rem 1.4rem;
            box-shadow: 0 18px 50px rgba(2, 8, 23, 0.36);
            backdrop-filter: blur(10px);
        }
        .alert-card {
            background: rgba(148, 163, 184, 0.08);
            border-left: 4px solid #f59e0b;
            padding: 0.8rem 1rem;
            border-radius: 14px;
            margin-bottom: 0.65rem;
        }
        .highlight-card {
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(52, 211, 153, 0.18));
            border: 1px solid rgba(125, 211, 252, 0.18);
            border-radius: 18px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 18px;
            padding: 0.85rem;
        }
        h1, h2, h3 {
            color: #f8fafc;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None


def validate_inputs(balance: float, expense_amount: float, monthly_needs: float, savings_goal: float) -> None:
    if balance < 0:
        raise ValueError("Current balance cannot be negative.")
    if expense_amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    if monthly_needs < 0:
        raise ValueError("Estimated monthly needs cannot be negative.")
    if savings_goal < 0:
        raise ValueError("Savings goal cannot be negative.")


def recommendation_text(risk_level: str, remaining_balance: float, model_probability: float | None) -> str:
    if remaining_balance < 0:
        return "🧯 Recommendation: Do not proceed because this purchase would overdraw your balance."
    if risk_level == "HIGH":
        return "🚦 Recommendation: Delay this purchase and prioritize essential expenses first."
    if model_probability is not None and model_probability >= 0.65:
        return "🤖 Recommendation: Your history suggests this transaction resembles past risky spending, so wait and reassess."
    if risk_level == "MEDIUM":
        return "⏳ Recommendation: Consider waiting 24 hours before going ahead."
    return "✅ Recommendation: This purchase looks reasonable if it still matches your financial goals."


def budget_health_text(remaining_balance: float, monthly_needs: float, savings_goal: float) -> str:
    if remaining_balance < 0:
        return "🚨 This move breaks your budget safety net."
    if remaining_balance < monthly_needs:
        return "⚠️ Essentials are exposed after this purchase."
    if remaining_balance < savings_goal:
        return "💡 Essentials are okay, but savings momentum takes a hit."
    return "🌱 Both your essentials and savings goal remain in a healthy range."


def render_alerts(alerts: list[str]) -> None:
    if not alerts:
        st.success("✅ No extra smart alerts were triggered.")
        return

    for alert in alerts:
        st.markdown(f'<div class="alert-card">{alert}</div>', unsafe_allow_html=True)


def build_analysis_payload(
    transactions: pd.DataFrame,
    balance: float,
    expense_amount: float,
    category: str,
    expense_type: str,
    monthly_needs: float,
    savings_goal: float,
) -> dict:
    recent_expenses = count_recent_expenses(transactions)
    risk_result = assess_transaction_risk(
        balance=balance,
        expense_amount=expense_amount,
        category=category,
        expense_type=expense_type,
        recent_expense_count=recent_expenses,
        monthly_needs=monthly_needs,
        savings_goal=savings_goal,
    )
    impact_result = simulate_financial_impact(
        balance=balance,
        expense_amount=expense_amount,
        monthly_needs=monthly_needs,
        savings_goal=savings_goal,
    )
    ml_probability = predict_risky_probability(
        transactions,
        {
            "balance_before": balance,
            "expense_amount": expense_amount,
            "monthly_needs": monthly_needs,
            "savings_goal": savings_goal,
            "recent_expense_count": recent_expenses,
            "category": category,
            "expense_type": expense_type,
        },
    )
    transaction_row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "balance_before": balance,
        "expense_amount": expense_amount,
        "category": category,
        "expense_type": expense_type,
        "monthly_needs": monthly_needs,
        "savings_goal": savings_goal,
        "remaining_balance": impact_result["remaining_balance"],
        "recent_expense_count": recent_expenses,
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "is_risky": int(risk_result["risk_level"] in {"MEDIUM", "HIGH"}),
        "message": risk_result["message"],
    }
    return {
        "risk_result": risk_result,
        "impact_result": impact_result,
        "ml_probability": ml_probability,
        "recent_expenses": recent_expenses,
        "transaction_row": transaction_row,
    }


def render_sidebar(transactions: pd.DataFrame) -> None:
    st.sidebar.header("Control Center")
    st.sidebar.caption("Manage local simulations and quick insights.")

    if transactions.empty:
        st.sidebar.info("No saved simulations yet.")
    else:
        st.sidebar.metric("Saved Simulations", int(len(transactions)))
        st.sidebar.metric("Average Risk Score", f'{transactions["risk_score"].mean():.0f}/100')
        st.sidebar.download_button(
            "Export CSV",
            data=transactions.to_csv(index=False).encode("utf-8"),
            file_name="finguard_transactions.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if st.sidebar.button("Reset History", use_container_width=True):
        reset_transactions()
        st.session_state.analysis_result = None
        st.rerun()


def render_analysis_result() -> None:
    payload = st.session_state.analysis_result
    if not payload:
        return

    risk_result = payload["risk_result"]
    impact_result = payload["impact_result"]
    ml_probability = payload["ml_probability"]
    transaction_row = payload["transaction_row"]

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🛡️ Risk Analysis")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Risk Level", risk_result["risk_level"])
    metric2.metric("Risk Score", f'{risk_result["risk_score"]}/100')
    metric3.metric("Remaining Balance", f'₹ {impact_result["remaining_balance"]:,.2f}')

    if risk_result["risk_level"] == "LOW":
        st.success(risk_result["message"])
    else:
        st.warning(risk_result["message"])

    monthly_needs = float(transaction_row["monthly_needs"])
    savings_goal = float(transaction_row["savings_goal"])
    remaining_balance = float(impact_result["remaining_balance"])
    expense_amount = float(transaction_row["expense_amount"])

    st.markdown(
        f"""
        <div class="highlight-card">
            <strong>Budget health snapshot</strong><br/>
            {budget_health_text(remaining_balance, monthly_needs, savings_goal)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    budget_ratio = min(expense_amount / max(monthly_needs, 1.0), 1.0)
    savings_ratio = min(max(remaining_balance, 0.0) / max(savings_goal, 1.0), 1.0)
    st.progress(budget_ratio, text=f"Expense vs monthly needs: {budget_ratio * 100:.0f}%")
    st.progress(savings_ratio, text=f"Post-purchase savings coverage: {savings_ratio * 100:.0f}%")

    for item in impact_result["impact_messages"]:
        st.write(item)

    if ml_probability is not None:
        st.info(f"🤖 ML estimate: {ml_probability:.0%} chance that this transaction is risky.")
    else:
        st.caption("ML insight will appear once enough varied transaction history is available.")

    st.markdown("#### Smart AI Alerts")
    render_alerts(risk_result["alerts"])
    st.write(recommendation_text(risk_result["risk_level"], remaining_balance, ml_probability))

    save_col, discard_col = st.columns(2)
    if save_col.button("Save Simulation", use_container_width=True):
        save_transaction(transaction_row)
        st.session_state.analysis_result = None
        st.success("Simulation saved locally to transactions.csv")
        st.rerun()

    if discard_col.button("Discard Analysis", use_container_width=True):
        st.session_state.analysis_result = None
        st.info("Analysis discarded.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def plot_spending_by_category(transactions: pd.DataFrame) -> None:
    st.subheader("📈 Spending by Category")
    if transactions.empty:
        st.info("No transaction history yet. Save a few simulations to unlock this chart.")
        return

    totals = transactions.groupby("category", dropna=False)["expense_amount"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(totals.index, totals.values, color="#38bdf8")
    ax.set_ylabel("Amount")
    ax.set_xlabel("Category")
    ax.set_facecolor("#0f172a")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#e5eef8", rotation=20)
    ax.yaxis.label.set_color("#e5eef8")
    ax.xaxis.label.set_color("#e5eef8")
    plt.tight_layout()
    st.pyplot(fig)


def plot_balance_over_time(transactions: pd.DataFrame) -> None:
    st.subheader("💹 Balance Over Time")
    if transactions.empty:
        st.info("Saved balances will appear here once you log simulations.")
        return

    ordered = transactions.sort_values("timestamp").copy()
    ordered["timestamp"] = pd.to_datetime(ordered["timestamp"], errors="coerce")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ordered["timestamp"], ordered["remaining_balance"], marker="o", linewidth=2.2, color="#34d399")
    ax.set_ylabel("Remaining Balance")
    ax.set_xlabel("Time")
    ax.set_facecolor("#0f172a")
    fig.patch.set_facecolor("#0f172a")
    ax.tick_params(colors="#e5eef8", rotation=20)
    ax.yaxis.label.set_color("#e5eef8")
    ax.xaxis.label.set_color("#e5eef8")
    plt.tight_layout()
    st.pyplot(fig)


def main() -> None:
    apply_custom_styles()
    initialize_state()

    st.markdown(
        """
        <div class="glass-card">
            <h1>🛡️ FinGuard - AI Financial Safety Net</h1>
            <p>
                Predict risky spending before a transaction happens, simulate the impact on essentials and savings,
                and store local transaction history to improve your financial awareness.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    transactions = load_transactions()
    render_sidebar(transactions)
    recent_expenses = count_recent_expenses(transactions)

    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🧾 Transaction Input")
        with st.form("finguard_form"):
            balance = st.number_input("Current Balance", min_value=0.0, value=5000.0, step=100.0)
            expense_amount = st.number_input("Expense Amount", min_value=0.0, value=800.0, step=50.0)
            category = st.selectbox(
                "Category",
                ["Food", "Shopping", "Bills", "Travel", "Entertainment", "Health", "Education", "Other"],
            )
            expense_type = st.radio("Type", ["Need", "Want"], horizontal=True)
            monthly_needs = st.number_input("Estimated Monthly Needs", min_value=0.0, value=2500.0, step=100.0)
            savings_goal = st.number_input("Savings Goal", min_value=0.0, value=1500.0, step=100.0)
            analyze = st.form_submit_button("Analyze Transaction")
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.metric("Recent Expense Signals", recent_expenses)
        st.metric("Total Tracked Spending", f"₹ {transactions['expense_amount'].sum():,.2f}" if not transactions.empty else "₹ 0.00")
        latest_balance = float(transactions["remaining_balance"].iloc[-1]) if not transactions.empty else 0.0
        st.metric("Latest Remaining Balance", f"₹ {latest_balance:,.2f}")
        risky_share = (transactions["is_risky"].mean() * 100) if not transactions.empty else 0.0
        st.metric("Risky Transaction Share", f"{risky_share:.0f}%")

    if analyze:
        try:
            validate_inputs(balance, expense_amount, monthly_needs, savings_goal)
            st.session_state.analysis_result = build_analysis_payload(
                transactions=transactions,
                balance=balance,
                expense_amount=expense_amount,
                category=category,
                expense_type=expense_type,
                monthly_needs=monthly_needs,
                savings_goal=savings_goal,
            )
        except ValueError as exc:
            st.error(f"Input error: {exc}")

    render_analysis_result()

    st.markdown("### 📊 Dashboard")
    overview_tab, charts_tab, history_tab = st.tabs(["Overview", "Charts", "History"])

    with overview_tab:
        if transactions.empty:
            st.info("Save a few simulations to unlock spending insights.")
        else:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Average Expense", f"₹ {transactions['expense_amount'].mean():,.2f}")
            col_b.metric("Highest Expense", f"₹ {transactions['expense_amount'].max():,.2f}")
            common_category = transactions["category"].mode().iloc[0]
            col_c.metric("Top Category", common_category)

            latest_message = transactions.sort_values("timestamp", ascending=False)["message"].iloc[0]
            st.markdown(
                f"""
                <div class="highlight-card">
                    <strong>Latest saved insight</strong><br/>
                    {latest_message}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with charts_tab:
        chart_left, chart_right = st.columns(2, gap="large")
        with chart_left:
            plot_spending_by_category(transactions)
        with chart_right:
            plot_balance_over_time(transactions)

    with history_tab:
        st.subheader("🗂️ Transaction History")
        if transactions.empty:
            st.info("No saved transactions yet.")
        else:
            table = transactions.sort_values("timestamp", ascending=False).copy()
            st.dataframe(table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
