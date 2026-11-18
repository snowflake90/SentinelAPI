import httpx
import pandas as pd
import streamlit as st

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="SentinelAPI", page_icon="🛰️", layout="wide")
st.title("🛰️ SentinelAPI")

ICONS = {"healthy": "🟢 Healthy", "slow": "🟡 Slow", "down": "🔴 Alert"}

def get(path, **params):
    return httpx.get(API+path, params=params, timeout=10).json()

try:
    status=get("/status")
except httpx.HTTPError:
    st.error("Cannot reach the backend. Start it with: uvicorn api:app --reload")
    st.stop()

if st.button("Check all now"):
    with st.spinner("Checking all endpoints..."):
        httpx.post(API + "/check-now", timeout=120)
    st.rerun()

if not status:
    st.info("No endpoints registered yet. Add some at http://127.0.0.1:8000/docs")
    st.stop()

# ---- summary numbers ----
c1, c2, c3 = st.columns(3)
c1.metric("Healthy", sum(s["result"] == "healthy" for s in status))
c2.metric("Slow", sum(s["result"] == "slow" for s in status))
c3.metric("Down", sum(s["result"] == "down" for s in status))

# ---- status table ----
rows = []
for s in status:
    ms = s["response_ms"]
    rows.append({
        "API": s["url"],
        "Status": ICONS.get(s["result"], s["result"]),
        "Response time": f"{ms} ms" if ms is not None else (s["error"] or "-"),
        "Uptime": f'{s["uptime_pct"]}%',
        "Last checked": s["last_checked"],
    })
st.dataframe(pd.DataFrame(rows), hide_index=True)

# ---- response-time chart ----
st.subheader("Response-time history")
chosen = st.selectbox("Choose an API", [s["url"] for s in status])
history = get("/history", url=chosen, limit=100)
if history:
    df = pd.DataFrame(history)
    df["checked_at"] = pd.to_datetime(df["checked_at"])
    st.line_chart(df.set_index("checked_at")["response_ms"])

# ---- incidents ----
st.subheader("Incident history")
incidents = get("/incidents")
if incidents:
    idf = pd.DataFrame(incidents)[["url", "started_at", "resolved_at", "reason"]]
    idf["resolved_at"] = idf["resolved_at"].fillna("ONGOING")
    st.dataframe(idf, hide_index=True)
else:
    st.caption("No incidents recorded.")
