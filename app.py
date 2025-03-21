import streamlit as st 
import pandas as pd
import datetime
import numpy as np
import plotly.express as px

#st.set_page_config(layout="wide") 

# Streamlit App Title

st.markdown(f"#### SO Qty Projection: Understanding **:red[Qty SO]** vs. **:red[Qty SO Final]** 😊")  
#st.title("SO Quantity Estimation")

today = datetime.date.today()
st.sidebar.markdown(f"📅 Today’s Date: **{today}**")

# File Upload Section
so_file = st.sidebar.file_uploader("Upload SQL-estimated SO (after 9 PM best :) )", type=["xlsx"])
#stock_df = st.sidebar.file_uploader("Upload SOH WH)", type=["xlsx"])
stock_df = pd.read_excel("gab.xlsx")
st.markdown(
    """
    <style>
        /* Reduce space at the top of the page */
        .block-container {
            padding-top: 3rem;
        }
        /* Reduce overall font size */
        html, body, [class*="css"] {
            font-size: 12px !important;
        }

        /* Reduce dataframe font size */
        div[data-testid="stDataFrame"] * {
            font-size: 9px !important;
        }
        
        /* Reduce table font size */
        table {
            font-size: 9px !important;
        }

        /* EXCLUDE Plotly Charts from Font Size Reduction */
        .js-plotly-plot .plotly * {
            font-size: 11px !important;  /* Ensures default or larger font */
        }
        
    </style>
    """,
    unsafe_allow_html=True
)

with st.expander("View Description"):
    st.markdown("""
    
    | Concept  | qty_so (how much should be ordered) | qty_so_final (final approved SO quantity)|
    |----------|--------|-------------|
    | **Purpose** | Initial calculated order quantity | Final approved SO quantity after warehouse stock check |
    | **Based on** | hub_qty, reorder_point, total_allocation, multiplier | wh_qty and cumulative_so_qty |
    | **Triggers order?** | ✅ Yes, if hub_qty ≤ reorder_point | ❌ No, if warehouse stock is insufficient |
    | **Explanation** | If **hub_qty > reorder_point**, no order is triggered (**qty_so = NULL**) | If **wh_qty < cumulative_so_qty**, lower-priority hubs might not get stock (**qty_so_final = NULL**) |
    """)
    
    st.markdown("""
    - **Total Active Hubs**: 30  
    - **Total WH**: 4  
    - Predicted **SO Qty D + X** is based on Demand Forecast for **next day, before considering wh_qty** 
    - **The displayed Qty for CBN excludes Xdock (30% of total SO)**  
     
    """)

# Sidebar navigation
tab1, tab2 = st.tabs(["Next Day SO Prediction", "D+1 to D+6 SO Prediction"])
#page = st.sidebar.radio("Select Page", ["D+0 SO Prediction", "D+1 to D+6 SO Prediction"])
#dry_forecast_file = st.file_uploader("Upload Dry Demand Forecast CSV", type=["xlsx"])
#fresh_cbn_forecast_file = st.file_uploader("Upload Fresh CBN Demand Forecast CSV", type=["xlsx"])
#fresh_pgs_forecast_file = st.file_uploader("Upload Fresh PGS Demand Forecast CSV", type=["xlsx"])

dry_forecast_df = pd.read_excel("demand_dry_productid_march.xlsx")
dry_forecast_df['date_key'] = pd.to_datetime(dry_forecast_df['date_key'], errors='coerce', format='%Y-%m-%d')

if so_file:
    # Load Data
    final_so_df = pd.read_excel(so_file)

    #ospo sit multiplier sebar rata
    # Get forecast dates D+1 to D+6

    forecast_dates = [(today + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6)]
    
    # Filter forecast data for D+1 to D+6
    dry_forecast_df = dry_forecast_df[dry_forecast_df["date_key"].isin(forecast_dates)]

    # Convert IDs to integer type
    final_so_df[['wh_id','product_id', 'hub_id']] = final_so_df[['wh_id','product_id', 'hub_id']].apply(pd.to_numeric)

    # Exclude specific hubs
    final_so_df["hub_id"] = final_so_df["hub_id"].astype(int)
    final_so_df = final_so_df[~final_so_df['hub_id'].isin([537, 758])]
    final_so_df = final_so_df[~final_so_df['wh_id'].isin([583])]

    

    # Merge the stock data with the final SO data on 'product_id'
    #final_so_df = final_so_df.merge(stock_df, on=['product_id','wh_id'], how='left')
    # karena berat exclude ospo dan sit sementara
    
     # Hub ID to Hub Name mapping
    hub_name_mapping = {
        98: "MTG - Menteng",
        121: "BS9 - Bintaro Sektor 9",
        125: "PPN - Pos Pengumben",
        152: "LBB - Lebak Bulus",
        189: "SRP - Serpong Utara",
        201: "MSB - Medan Satria Bekasi",
        206: "JTB - Jatibening",
        207: "GWB - Grand Wisata Bekasi",
        223: "CT2 - Citra 2",
        261: "CNR - Cinere",
        288: "MRG - Margonda",
        517: "FTW - Fatmawati",
        523: "JLB - Jelambar",
        529: "BSX - New BSD",
        538: "KJT - Kramat Jati",  # Excluded
        591: "MRY - Meruya",
        615: "GPL - Gudang Peluru",
        619: "TSY - Transyogi",
        626: "DST - Duren Sawit",
        634: "PPL - Panglima Polim",
        648: "DNS - Danau Sunter",
        654: "TGX - New TGC",
        657: "APR - Ampera",
        669: "BRY - Buncit Raya",
        672: "KPM - Kapuk Muara",
        759: "CWG - Cawang",  # Excluded
        763: "PSG - Pisangan",
        767: "PKC - Pondok Kacang",
        773: "PGD - Pulo Gadung",
        776: "BGS - Boulevard Gading Serpong"
    }

    # WH ID to WH Name mapping
    wh_name_mapping = {
        40: "KOS - WH Kosambi",
        772: "STL - Sentul",
        160: "PGS - Pegangsaan",
        661: "CBN - WH Cibinong"
    }

    
    with tab1:
        #st.subheader("Next Day SO Prediction")
    
         # Compute Predicted SO Qty D+0
        final_so_df['Predicted SO Qty D+0'] = ((final_so_df['Sum of maxqty'] - final_so_df['Sum of hub_qty']) / 
                                               final_so_df['Sum of multiplier']) * final_so_df['Sum of multiplier']
        final_so_df['Predicted SO Qty D+0'] = final_so_df['Predicted SO Qty D+0'].clip(lower=0).astype(int)
    
        final_so_df["WH Name"] = final_so_df["wh_id"].map(wh_name_mapping)
        final_so_df["Hub Name"] = final_so_df["hub_id"].map(hub_name_mapping)
        final_so_df = final_so_df.rename(columns={"wh_id": "WH ID"})

        #def highlight_final_so(s):
            #return ['background-color: #FFFACD' if s.name == 'Sum of qty_so_final' else '' for _ in s]

        # Create a WH-level aggregated DataFrame
        wh_summary_df = final_so_df.groupby("WH Name").agg({
        #'Sum of qty_so': 'sum',
        'Predicted SO Qty D+0': 'sum'
        #'Sum of qty_so_final': 'sum'
        }).reset_index()
        
        # Apply styling
        #styled_wh_summary = wh_summary_df.style.apply(highlight_final_so, subset=["Sum of qty_so_final"])
        
        # Display WH-level summary with highlight
        st.markdown('<h4 style="color: maroon;">Summary by WH</h4>', unsafe_allow_html=True)
        st.dataframe(wh_summary_df, use_container_width=True)
        
        # Select WH dropdown
        st.markdown('<h4 style="color: maroon;">Summary by Hub</h4>', unsafe_allow_html=True)
        wh_options = final_so_df["WH Name"].unique().tolist()
        selected_wh = st.selectbox("Select WH", wh_options)
        
        # Filter DataFrame by selected WH
        filtered_so_df = final_so_df[final_so_df["WH Name"] == selected_wh]
        
        # Apply styling to filtered DataFrame
        #styled_filtered_so = filtered_so_df[["Hub Name", "Sum of qty_so", "Sum of qty_so_final", "Predicted SO Qty D+0"]].style.apply(
          #  highlight_final_so, subset=["Sum of qty_so_final"]
        #)

        selected_columns = ["Hub Name", "Predicted SO Qty D+0"]
        filtered_so_df_selected = filtered_so_df[selected_columns]
        
        # Display the filtered DataFrame with selected columns
        st.dataframe(filtered_so_df_selected, use_container_width=True)
        #st.dataframe(filtered_so_df[["Hub Name", "Sum of qty_so", "Sum of qty_so_final", "Predicted SO Qty D+0"]])

        csv1 = final_so_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Next Day SO Prediction", csv1, "next_day_so_prediction.csv", "text/csv")
   
    
    with tab2:
            
        # Initialize result DataFrame
        results = []
        prev_day_predicted_so = pd.Series(0, index=final_so_df.index)
        #temporary
        #split_product_ids_df = pd.read_csv("splitadd.csv")
        #split_product_ids = set(split_product_ids_df["product_id"].tolist())
        #split_product_ids = pd.to_numeric(split_product_ids_df['product_id'], errors='coerce')
        
        dry_forecast_df['product_id'] = pd.to_numeric(dry_forecast_df['product_id'], errors='coerce')
        merged_df = final_so_df[['product_id', 'WH ID']].merge(dry_forecast_df[['product_id', 'Forecast Step 3','date_key']], on='product_id', how='left')
        
        #st.write(merged_df.head())
        #st.write(f"Forecast Dates: {merged_df["date_key"].unique()}")
        for day, forecast_date in enumerate(forecast_dates, start=1):
            for product_id in merged_df["product_id"].unique():
                # Get the daily dry forecast for the given date and product ID
                daily_dry_forecast = merged_df[
                    (merged_df["date_key"] == forecast_date) & 
                    (merged_df["product_id"] == product_id)
                ]["Forecast Step 3"].sum()
                
                wh_40_products = set(merged_df.loc[merged_df["WH ID"] == 40, "product_id"])
                wh_772_products = set(merged_df.loc[merged_df["WH ID"] == 772, "product_id"])
                
                # Determine common products and merge with split_product_ids
                common_products = wh_40_products.intersection(wh_772_products)#.union(split_product_ids)
                
                # Display a few common products for debugging
                #st.write(f"Number of common products: {len(common_products)}")
                
                # Allocate Demand Forecast to WHs
                if product_id in common_products:
                    dry_demand_allocation_split = {
                        772: int(daily_dry_forecast * 0.62),
                        40: int(daily_dry_forecast * 0.38)
                    }
                elif product_id in wh_40_products:
                    dry_demand_allocation_split = {40: int(daily_dry_forecast)}
                elif product_id in wh_772_products:
                    dry_demand_allocation_split = {772: int(daily_dry_forecast)}
                else:
                    dry_demand_allocation_split = {772: daily_dry_forecast}
            
            #print(f"Product ID: {product_id}, Dry Demand Allocation Split:", dry_demand_allocation_split)
             
            daily_result = final_so_df.copy()
            daily_result[f'Updated Hub Qty D+{day}'] = daily_result['Sum of hub_qty']
            dry_demand_allocation_split = {}
            # Iterate through each WH ID and Hub ID
            for wh_id in final_so_df['WH ID'].unique():
                total_maxqty = final_so_df.loc[(final_so_df['WH ID'] == wh_id) & (final_so_df['product_id'] == product_id),'Sum of maxqty'].sum()
                for hub_id in final_so_df.loc[final_so_df['WH ID'] == wh_id, 'hub_id'].unique():
                    hub_mask = (daily_result['WH ID'] == wh_id) & (daily_result['hub_id'] == hub_id)
                    
                    if total_maxqty > 0:
                        hub_forecast = ((final_so_df.loc[hub_mask, 'Sum of maxqty'] / total_maxqty) * 
                                        (dry_demand_allocation_split.get(wh_id, 0)))

                        upload_time = pd.Timestamp.now()
                        upload_hour = upload_time.hour
                        hourly_percentages = [
                            1.45, 0.88, 0.57, 0.62, 0.68, 1.15, 2.10, 3.60, 4.80, 5.49, 5.77, 5.85,
                            5.42, 5.71, 5.75, 7.17, 7.53, 6.33, 5.46, 6.06, 5.83, 5.07, 4.02, 2.70
                        ]
                        
                        # Convert to a DataFrame for easier handling
                        hourly_df = pd.DataFrame(hourly_percentages, columns=['percentage'])
                        
                        # Normalize the percentages to sum up to 1
                        hourly_df['normalized'] = hourly_df['percentage'] / hourly_df['percentage'].sum()
                        
                        # Calculate the remaining percentage after the upload hour
                        remaining_percentage = hourly_df.loc[upload_hour:, 'normalized'].sum()
                        
                        # Adjust the hub forecast based on the remaining percentage
                        adjusted_hub_forecast = hub_forecast * remaining_percentage
                    
                    else:
                        adjusted_hub_forecast = 0
                    
                    daily_result.loc[hub_mask, f'Updated Hub Qty D+{day}'] -= adjusted_hub_forecast
                    daily_result.loc[hub_mask, f'Updated Hub Qty D+{day}'] = daily_result.loc[hub_mask, f'Updated Hub Qty D+{day}'].clip(lower=0)
                    
            # Compute Predicted SO Quantity
            daily_result[f'Predicted SO Qty D+{day}'] = (
                (daily_result['Sum of maxqty'] - daily_result[f'Updated Hub Qty D+{day}']) / daily_result['Sum of multiplier']) * daily_result['Sum of multiplier']
            daily_result[f'Predicted SO Qty D+{day}'] = daily_result[f'Predicted SO Qty D+{day}'].clip(lower=0)
            
            # Adjust Predicted SO Quantity based on stock availability
            # Merge daily_result with stock_df to add the 'stock' column

            daily_result = daily_result.merge(stock_df[['product_id', 'WH ID', 'stock']], on=['WH ID','product_id'], how='left')
            
            # Set Predicted SO Qty to NaN if stock is less than the predicted quantity
            total_predicted_so = (daily_result.groupby(['product_id', 'WH ID'])[f'Predicted SO Qty D+{day}'].transform('sum'))
        
            # Set Predicted SO Qty to NaN if stock is less than the predicted SO Qty
            daily_result.loc[ daily_result['stock'] < total_predicted_so, f'Predicted SO Qty D+{day}'] = np.nan
            
            #daily_result.loc[daily_result['stock'] < daily_result[f'Predicted SO Qty D+{day}'], f'Predicted SO Qty D+{day}'] = np.nan

            #print(daily_result[[f'Predicted SO Qty D+{day}', 'stock']])
            
            #daily_result.loc[daily_result['WH ID'] == 40, f'Predicted SO Qty D+{day}'] *= 0.71
            #daily_result.loc[daily_result['WH ID'] == 772, f'Predicted SO Qty D+{day}'] *= 0.535
            
            #daily_result[f'Predicted SO Qty D+{day}'] = daily_result[f'Predicted SO Qty D+{day}'].fillna(0)
            
            #daily_result[f'Predicted SO Qty D+{day}'] = daily_result[f'Predicted SO Qty D+{day}'].clip(lower=0).astype(int)
            
            daily_result = daily_result.rename(columns={"wh_id": "WH ID", "hub_id": "Hub ID"})
            results.append(daily_result[["WH ID", "Hub ID", "product_id", "Sum of maxqty", f"Updated Hub Qty D+{day}", f"Predicted SO Qty D+{day}","stock"]])
            prev_day_predicted_so = daily_result[f'Predicted SO Qty D+{day}'].copy()
        # Merge results into a single DataFrame
        final_results_df = results[0]
        for df in results[1:]:
            final_results_df = final_results_df.merge(df, on=["WH ID", "Hub ID","product_id", "Sum of maxqty","stock"], how="left")
        final_results_df2 = final_results_df.drop_duplicates()
        #final_results_df["WH Name"] = final_results_df["wh_id"].map(wh_name_mapping)
        
        # Display Results
        #st.subheader("D+1 to D+6 SO Prediction")
        
        def highlight_triggered(val):
            color = 'background-color: lightgreen' if val == "Triggered" else 'background-color: lightcoral'
            return color
    
        #final_results_df = final_results_df.rename(columns={"wh_id": "WH ID", "hub_id": "Hub ID"})

         # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        # Place the select boxes in separate columns
        with col2:
            selected_day = st.selectbox("Select D+X day(s)", [f"D+{i}" for i in range(1, 7)])
        
        with col1:
            wh_options = final_results_df["WH ID"].unique().tolist()
            selected_wh = st.selectbox("Select WH ID", wh_options)
        
        # Filter the dataframe based on selected WH
        
        final_results_df2 = final_results_df2.rename(columns={"Sum of maxqty": "Max Total Allocation"})
        filtered_df = final_results_df2[final_results_df["WH ID"] == selected_wh]
        
        # Select relevant columns dynamically based on the chosen day
        selected_columns = ["WH ID","Hub ID","product_id", f"Updated Hub Qty {selected_day}", f"Predicted SO Qty {selected_day}", "Max Total Allocation","stock"]
        
        # Apply selection and styling
        filtered_df = filtered_df[selected_columns]
        filtered_df = filtered_df.dropna(how='any')
        filtered_df = filtered_df.drop_duplicates(subset=["product_id", "Hub ID"])
        #styled_df = final_results_df.style.applymap(highlight_triggered, subset=[col for col in final_results_df.columns if "SO vs Reorder Point" in col])

        #styled_df = styled_df.hide(axis="index")
        st.markdown('<h4 style="color: maroon;">Summary by WH by Day</h4>', unsafe_allow_html=True)
        st.dataframe(filtered_df, use_container_width=True)

        if 40 in filtered_df["WH ID"].values:
            predicted_so_sum = filtered_df.loc[filtered_df["WH ID"] == 40, f"Predicted SO Qty {selected_day}"].sum()
        elif 772 in filtered_df["WH ID"].values:
            predicted_so_sum = filtered_df.loc[filtered_df["WH ID"] == 772, f"Predicted SO Qty {selected_day}"].sum()
        else:
            predicted_so_sum = 0  # Default value if no matching WH ID is found
        
        st.metric(label="Total Predicted SO Qty", value=f"{predicted_so_sum:,.0f}")
        
        csv = final_results_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download D+1 to D+6 SO Prediction", csv, "d1_d6_so_prediction.csv", "text/csv")
