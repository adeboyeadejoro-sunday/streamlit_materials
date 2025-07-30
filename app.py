import streamlit as st
import pandas as pd
import json
from io import StringIO

from datetime import datetime

today_str = datetime.today().strftime("%d%m%Y")
supplier_sample_counter = 1


st.set_page_config(page_title="CSV to Nested JSON", layout="centered")

st.title("📄 → 🧱 CSV to Complex JSON Converter")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV into DataFrame
    data = pd.read_csv(uploaded_file, dtype='str').fillna('')
    st.success("CSV loaded successfully!")

    # Allow user to specify default location
    location = st.text_input("Enter default location for lots", value="Berlin")

    if st.button("Convert to JSON"):
        json_object_list = []

        for _, row in data.iterrows():
            if row.get("Odoo", "").strip().lower() != "item not in odoo":
                continue  # Skip rows already in Odoo
            sku = row.get("SKU", "")
            if sku.strip().lower() == "supplier sample":
                sku = f"SPS{today_str}-{supplier_sample_counter:02d}"
                supplier_sample_counter += 1

            json_object = {
                "prod_sku": row.get("SKU", ""),
                "prod_name": row.get("Name ↗️", ""),
                "prod_odoo_id": None,
                "category": "RMQ Sample",
                "consumption_time": None,
                "prod_lots": [
                    {
                        "lot_ldb_id": None,
                        "lot_odoo_id": None,
                        "lot_name": row.get("LOT", ""),
                        "best_before": None,
                        "expiration_date": None,
                        "location": location,
                        "mos": [],
                        "raw_materials": []
                    }
                ]
            }

            json_object_list.append(json_object)

        st.success(f"✅ {len(json_object_list)} new items prepared for JSON export.")
        if len(data) > len(json_object_list):
            st.warning(f"ℹ️ {len(data) - len(json_object_list)} rows were skipped because they are already in Odoo.")
        matching_rows = data[data["Odoo"].str.strip() == "Item Not in Odoo"]
        st.write(f"{len(matching_rows)} rows match 'Items Not in Odoo'")

        # Convert to JSON string
        json_str = json.dumps(json_object_list, indent=2, ensure_ascii=False)

        # Show preview
        st.subheader("Preview of Output JSON")
        st.code(json_str[:3000] + ("\n..." if len(json_str) > 3000 else ""), language="json")

        # Enable file download
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name="output.json",
            mime="application/json"
        )
