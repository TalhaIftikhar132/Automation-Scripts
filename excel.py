# import pandas as pd

# # Load both Excel files
# sheet1 = pd.read_excel("IE_clients_list.xlsx")
# sheet2 = pd.read_excel("floorplan_data.xlsx")

# # Clean column names (remove weird spaces)
# sheet1.columns = sheet1.columns.str.replace('\xa0', ' ', regex=False).str.strip()
# sheet2.columns = sheet2.columns.str.replace('\xa0', ' ', regex=False).str.strip()

# # Clean the relevant text columns (strip spaces + lowercase for comparison)
# sheet1['Client_clean'] = sheet1['Client'].astype(str).str.strip().str.lower()
# sheet2['Company_clean'] = sheet2['Company Name'].astype(str).str.strip().str.lower()

# # --- OPTION 1: Exact match (case-insensitive) ---
# common_exact = pd.merge(sheet1, sheet2, left_on='Client_clean', right_on='Company_clean')

# # --- OPTION 2: Partial match (if you want "Apple" to match "Apple Inc") ---
# matches = []
# for i, client in enumerate(sheet1['Client_clean']):
#     for j, company in enumerate(sheet2['Company_clean']):
#         if client in company or company in client:  # partial match logic
#             matches.append((i, j))

# # Create dataframe of all matches
# matched_rows = pd.DataFrame([
#     {**sheet1.iloc[i].to_dict(), **sheet2.iloc[j].to_dict()}
#     for i, j in matches
# ])

# # Save to Excel
# matched_rows.to_excel("all_matching_clients.xlsx", index=False)

# print(f"✅ Found {len(matched_rows)} matches and saved to 'all_matching_clients.xlsx'")


# import pandas as pd

# # File paths
# file1 = "floorplan_data.xlsx"
# file2 = "IE_clients_list.xlsx"

# # Read Excel files
# df_booths = pd.read_excel(file1)
# df_clients = pd.read_excel(file2)

# # FIX: Use rename instead of direct assignment to avoid length mismatch
# # Replace 'Old Column Name' with the actual name currently in your Excel files
# df_booths = df_booths.rename(columns={
#     df_booths.columns[0]: "Brand Name", 
#     df_booths.columns[1]: "Booth Number"
# })

# df_clients = df_clients.rename(columns={
#     df_clients.columns[0]: "Client Name", 
#     df_clients.columns[1]: "Brand Name"
# })

# # Merge on Brand Name
# merged_df = pd.merge(
#     df_clients,
#     df_booths,
#     on="Brand Name",
#     how="left"
# )

# # Add Match Status
# merged_df["Match Status"] = merged_df["Booth Number"].apply(
#     lambda x: "Matched" if pd.notna(x) else "Not Matched"
# )

# # Save output Excel file
# output_file = "client_brand_booth_match_results.xlsx"
# merged_df.to_excel(output_file, index=False)

# print("Comparison completed successfully.")
# print(f"Results saved to: {output_file}")
import pandas as pd

# File paths
file1 = "floorplan_data.xlsx"
file2 = "IE_clients_list.xlsx"

# Read Excel files
df_booths = pd.read_excel(file1)
df_clients = pd.read_excel(file2)

# --- ROBUST RENAMING ---
# We force the first two columns to be what we need, 
# no matter what they are named in Excel.
df_booths.columns.values[0] = "Brand Name"
df_booths.columns.values[1] = "Booth Number"

df_clients.columns.values[0] = "Client Name"
df_clients.columns.values[1] = "Brand Name"

# --- SELECT ONLY WHAT WE NEED ---
# This matches your line 89 but uses the names we just forced above
df1 = df_clients[["Brand Name", "Client Name"]] 
df2 = df_booths[["Brand Name", "Booth Number"]]

# Merge on Brand Name
merged_df = pd.merge(df1, df2, on="Brand Name", how="left")

# Add Match Status
merged_df["Match Status"] = merged_df["Booth Number"].apply(
    lambda x: "Matched" if pd.notna(x) else "Not Matched"
)

# Save
merged_df.to_excel("matching_results.xlsx", index=False)
print("Done! Check matching_results.xlsx")