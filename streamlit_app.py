import streamlit as st
import json
import os
from core import run_pipeline

st.markdown("## 🧠 SmartClaims AI")
st.markdown("Upload an insurance policy and enter a natural language query. Get intelligent claim decisions backed by policy clauses.")

# 📎 File uploader
uploaded_file = st.file_uploader("📄 Upload Policy Document (PDF)", type=["pdf"])

# 🔠 Query input
user_query = st.text_input("📝 Enter your claim query", placeholder="E.g., 46M, knee surgery in Pune, 3-month-old policy")

# 🚀 Submit
if st.button("🚀 Submit Claim"):
    if uploaded_file and user_query:
        with st.spinner("Analyzing your claim..."):
            # Save uploaded file temporarily
            with open("temp_policy.pdf", "wb") as f:
                f.write(uploaded_file.read())

            parsed_query, decision = run_pipeline(user_query, "temp_policy.pdf")

            st.success("✅ Claim analyzed successfully!")
            
            parsed_json = json.loads(parsed_query) if parsed_query is not None else {}
            result_json = json.loads(decision) if decision is not None else {}

            # Display Decision
            st.markdown("### 🔍 Decision Summary")
            st.markdown(f"""
                <div style='padding: 1rem; border-radius: 10px; background-color: #e8f5e9; border: 1px solid #4caf50;'>
                    <b>Decision:</b> {result_json['decision']}<br>
                    <b>Amount:</b> {result_json['amount']}
                </div>
            """, unsafe_allow_html=True)

            # Display Extracted Query Details
            st.markdown("### 🧾 Parsed Query")
            st.json(parsed_json)

            # Justification
            st.markdown("### 📜 Justification Based on Policy Clauses")
            for clause in result_json["justification"]:
                with st.expander(f"📘 {clause['clause']}"):
                    st.write(clause["explanation"])
    else:
        st.warning("Please upload a policy document and enter a query.")