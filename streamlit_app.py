
import streamlit as st
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="MTF Position Simulator", layout="wide")

# ----------------------
# Mock defaults (you can change in sidebar)
# ----------------------
DEFAULT_STOCK = "NSE:ITC"
DEFAULT_LTP = 412.8
DEFAULT_INVEST = 200000
DEFAULT_EXPOSURE = 5
DEFAULT_TARGET = 495.36
DEFAULT_STOPLOSS = 380.0
DEFAULT_DAYS = 30
DEFAULT_INTEREST = 9.0  # annual %

# Charges assumptions (% on turnover)
DEFAULT_BROKERAGE = 0.05
DEFAULT_TXN_CHARGES = 0.02
DEFAULT_OTHER_CHARGES = 0.01
GST_RATE = 0.18

# ----------------------
# Helper Function
# ----------------------
def simulate(ltp, invest, exposure, target_price, stop_price, holding_days,
             interest_rate, brokerage_pct, txn_charges_pct, other_charges_pct):
    total_position = invest * exposure
    qty = total_position / ltp if ltp else 0
    broker_margin = total_position - invest
    turnover = total_position * 2

    brokerage = turnover * brokerage_pct/100
    txn_charges = turnover * txn_charges_pct/100
    other_charges = turnover * other_charges_pct/100
    gst = (brokerage + txn_charges) * GST_RATE

    # interest only for MTF
    interest = broker_margin * (interest_rate/100) * (holding_days/365)

    total_charges_cnc = brokerage + txn_charges + other_charges + gst
    total_charges_mtf = total_charges_cnc + interest

    breakeven_mtf = ltp + (total_charges_mtf / qty) if qty else None

    cnc_net_pnl = (target_price - ltp) * qty - total_charges_cnc
    mtf_net_pnl = (target_price - ltp) * qty - total_charges_mtf

    cnc_roi = (cnc_net_pnl / total_position) * 100 if total_position else 0
    mtf_roi = (mtf_net_pnl / invest) * 100 if invest else 0

    per_day_interest = (broker_margin * (interest_rate/100)) / 365
    ideal_days = round(total_charges_mtf / per_day_interest) if per_day_interest > 0 else None

    return dict(
        total_position=total_position, qty=qty, broker_margin=broker_margin,
        turnover=turnover, brokerage=brokerage, txn_charges=txn_charges,
        other_charges=other_charges, gst=gst, interest=interest,
        total_charges_cnc=total_charges_cnc, total_charges_mtf=total_charges_mtf,
        breakeven_mtf=breakeven_mtf,
        cnc_net_pnl=cnc_net_pnl, mtf_net_pnl=mtf_net_pnl,
        cnc_roi=cnc_roi, mtf_roi=mtf_roi, ideal_days=ideal_days
    )

# ----------------------
# Sidebar Inputs
# ----------------------
with st.sidebar:
    st.header("Inputs")
    stock = st.text_input("Stock Symbol", DEFAULT_STOCK)
    ltp = st.number_input("LTP (₹)", value=DEFAULT_LTP, step=0.1)
    invest = st.number_input("Investment Value (₹)", value=DEFAULT_INVEST, step=1000)
    exposure = st.number_input("Exposure (x)", value=DEFAULT_EXPOSURE, step=1)
    target_price = st.number_input("Target Price (₹)", value=DEFAULT_TARGET, step=0.1)
    stop_price = st.number_input("Stoploss Price (₹)", value=DEFAULT_STOPLOSS, step=0.1)
    holding_days = st.number_input("Holding Days", value=DEFAULT_DAYS, step=1)
    interest_rate = st.number_input("Interest Rate % (annual)", value=DEFAULT_INTEREST, step=0.1)

    st.markdown("**Charges (%) on Turnover**")
    brokerage_pct = st.number_input("Brokerage %", value=DEFAULT_BROKERAGE, step=0.01)
    txn_charges_pct = st.number_input("Transaction Charges %", value=DEFAULT_TXN_CHARGES, step=0.01)
    other_charges_pct = st.number_input("Other Charges %", value=DEFAULT_OTHER_CHARGES, step=0.01)

# ----------------------
# Run Simulation
# ----------------------
res = simulate(ltp, invest, exposure, target_price, stop_price, holding_days,
               interest_rate, brokerage_pct, txn_charges_pct, other_charges_pct)

# ----------------------
# Results Summary
# ----------------------
st.title("📊 MTF Position Simulator")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Position (₹)", f"{res['total_position']:.0f}")
    st.metric("Quantity", f"{res['qty']:.2f}")
    st.metric("Broker Funded Margin (₹)", f"{res['broker_margin']:.0f}")
with col2:
    st.metric("Breakeven Price (₹)", f"{res['breakeven_mtf']:.2f}")
    st.metric("Total Charges CNC (₹)", f"{res['total_charges_cnc']:.2f}")
    st.metric("Total Charges MTF (₹)", f"{res['total_charges_mtf']:.2f}")

st.markdown("---")
st.subheader("Net P&L at Target Price")
st.write({
    "CNC Net P&L (₹)": round(res["cnc_net_pnl"], 2),
    "MTF Net P&L (₹)": round(res["mtf_net_pnl"], 2),
    "CNC ROI %": round(res["cnc_roi"], 2),
    "MTF ROI %": round(res["mtf_roi"], 2),
})

# ----------------------
# Charts: P&L and ROI vs Price
# ----------------------
prices = np.arange(ltp * 0.8, ltp * 1.21, ltp * 0.01)
cnc_pl = [(p - ltp) * res["qty"] - res["total_charges_cnc"] for p in prices]
mtf_pl = [(p - ltp) * res["qty"] - res["total_charges_mtf"] for p in prices]
cnc_roi = [(pl / res["total_position"]) * 100 for pl in cnc_pl]
mtf_roi = [(pl / invest) * 100 for pl in mtf_pl]

st.subheader("Profit & Loss vs Stock Price")
fig = go.Figure()
fig.add_trace(go.Scatter(x=prices, y=cnc_pl, name="CNC P&L"))
fig.add_trace(go.Scatter(x=prices, y=mtf_pl, name="MTF P&L"))
fig.update_layout(xaxis_title="Stock Price (₹)", yaxis_title="P&L (₹)")
st.plotly_chart(fig, use_container_width=True)

st.subheader("ROI % vs Stock Price")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=prices, y=cnc_roi, name="CNC ROI %"))
fig2.add_trace(go.Scatter(x=prices, y=mtf_roi, name="MTF ROI %"))
fig2.update_layout(xaxis_title="Stock Price (₹)", yaxis_title="ROI %")
st.plotly_chart(fig2, use_container_width=True)

# ----------------------
# Recommendation Logic
# ----------------------
st.subheader("🤖 AI-Style Recommendation")

if target_price <= res["breakeven_mtf"]:
    st.warning("💰 CNC recommended — target is below MTF breakeven, MTF won’t cover costs.")
elif holding_days > (res["ideal_days"] or 9999):
    st.info("⏳ CNC recommended — holding period too long, interest eats returns.")
elif res["mtf_roi"] > res["cnc_roi"] * 1.5:
    st.success("✅ MTF looks attractive — ROI is much higher after costs.")
else:
    st.info("💰 CNC is safer — ROI boost from MTF isn’t significant.")

st.caption(f"Ideal Holding Days to Breakeven: {res['ideal_days']}")
