
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MTF vs CNC Demo", layout="centered")

st.title("📊 MTF vs Cash & Carry (CNC) Simulator - Demo")
st.caption("Mock data demo with ITC stock. No live API, only static calculations.")

# -----------------------------
# Mock Data
# -----------------------------
stock = "NSE:ITC"
ltp = 412.8         # Last traded price
investment = 200000 # Investor capital
exposure = 5        # MTF leverage
target_price = 495.36
stoploss_price = 380.0
holding_days = 30
interest_rate = 9.0 # Annual %

# Charges (% on turnover)
brokerage_pct = 0.05
txn_charges_pct = 0.02
other_charges_pct = 0.01
gst_rate = 0.18

# -----------------------------
# Calculations
# -----------------------------
total_position = investment * exposure
qty = total_position / ltp
broker_margin = total_position - investment
turnover = total_position * 2

brokerage = turnover * brokerage_pct/100
txn_charges = turnover * txn_charges_pct/100
other_charges = turnover * other_charges_pct/100
gst = (brokerage + txn_charges) * gst_rate

# Charges
cnc_charges = brokerage + txn_charges + other_charges + gst
mtf_interest = broker_margin * (interest_rate/100) * (holding_days/365)
mtf_charges = cnc_charges + mtf_interest

# Net P&L
cnc_net_pnl = (target_price - ltp) * qty - cnc_charges
mtf_net_pnl = (target_price - ltp) * qty - mtf_charges

# ROI
cnc_roi = (cnc_net_pnl / total_position) * 100
mtf_roi = (mtf_net_pnl / investment) * 100

# -----------------------------
# Display
# -----------------------------
st.subheader("Scenario Inputs")
st.write({
    "Stock": stock,
    "LTP": ltp,
    "Investment": investment,
    "Exposure": exposure,
    "Target Price": target_price,
    "Stoploss Price": stoploss_price,
    "Holding Days": holding_days
})

st.subheader("Results")
st.write({
    "Quantity": round(qty,2),
    "Total Position": round(total_position,2),
    "Broker Margin": round(broker_margin,2),
    "Breakeven Price (MTF)": round(ltp + mtf_charges/qty,2),
    "CNC Net P&L": round(cnc_net_pnl,2),
    "MTF Net P&L": round(mtf_net_pnl,2),
    "CNC ROI %": round(cnc_roi,2),
    "MTF ROI %": round(mtf_roi,2),
})

# -----------------------------
# ROI Curve (Mock for demo)
# -----------------------------
prices = [ltp*0.9, ltp, ltp*1.1, target_price]
cnc_roi_curve = [((p-ltp)*qty - cnc_charges)/total_position*100 for p in prices]
mtf_roi_curve = [((p-ltp)*qty - mtf_charges)/investment*100 for p in prices]

df = pd.DataFrame({
    "Stock Price": prices,
    "CNC ROI %": cnc_roi_curve,
    "MTF ROI %": mtf_roi_curve
})

st.subheader("ROI % vs Price (Mock Chart)")
st.line_chart(df.set_index("Stock Price"))

# -----------------------------
# Recommendation (Rule-based)
# -----------------------------
st.subheader("🤖 Recommendation")

if target_price <= (ltp + mtf_charges/qty):
    st.warning("💰 CNC recommended — target is below MTF breakeven.")
elif mtf_roi > cnc_roi * 1.5:
    st.success("✅ MTF looks attractive — ROI is much higher after costs.")
else:
    st.info("💰 CNC is safer — ROI boost from MTF isn’t significant.")
