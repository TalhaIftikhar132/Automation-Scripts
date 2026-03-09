import pandas as pd
import re

# =========================
# FILE NAMES (same folder)
# =========================
brand_file = "floorplan_data.xlsx"
client_file = "IE_clients_list.xlsx"
output_file = "brand_client_comparison.xlsx"

# =========================
# READ EXCEL FILES
# =========================
df_brand = pd.read_excel(brand_file)
df_client = pd.read_excel(client_file)

# =========================
# NORMALIZE COLUMN NAMES
# =========================
df_brand.columns = df_brand.columns.str.strip().str.lower()
df_client.columns = df_client.columns.str.strip().str.lower()

# =========================
# COLUMN NAMES (CONFIRMED)
# =========================
brand_col = "brand name"
booth_col = "booth number"
client_col = "client"

# =========================
# CLEAN TEXT DATA
# =========================
df_brand[brand_col] = (
    df_brand[brand_col]
    .astype(str)
    .str.lower()
    .str.strip()
)

df_client[client_col] = (
    df_client[client_col]
    .astype(str)
    .str.lower()
    .str.strip()
)

# =========================
# FULLY MATCHED (EXACT)
# =========================
fully_matched = df_brand.merge(
    df_client,
    left_on=brand_col,
    right_on=client_col,
    how="inner"
)[[brand_col, client_col, booth_col]]

# =========================
# PARTIALLY MATCHED (ONE WORD)
# =========================
partial_rows = []

for _, b in df_brand.iterrows():
    brand_words = set(re.findall(r"\w+", b[brand_col]))

    for _, c in df_client.iterrows():
        client_words = set(re.findall(r"\w+", c[client_col]))

        if (
            b[brand_col] != c[client_col]
            and brand_words.intersection(client_words)
        ):
            partial_rows.append({
                "brand name": b[brand_col],
                "client name": c[client_col],
                "booth number": b[booth_col]
            })

partially_matched = pd.DataFrame(partial_rows).drop_duplicates()

# =========================
# SAVE TO NEW EXCEL FILE
# =========================
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    fully_matched.to_excel(writer, sheet_name="Fully Matched", index=False)
    partially_matched.to_excel(writer, sheet_name="Partially Matched", index=False)

print("✅ SUCCESS!")
print("📁 Output file created:", output_file)
