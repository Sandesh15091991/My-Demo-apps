
import streamlit as st
import plotly.graph_objs as go

st.title("✅ Plotly Import Test")

# Simple Plotly chart
fig = go.Figure(data=[go.Bar(x=["A", "B", "C"], y=[1, 3, 2])])
st.plotly_chart(fig)
