import json
import os
import sys
import math
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
from collections import defaultdict

import argparse



def flatten_json(y, parent_key='', sep='.'):
    items = {}
    if isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(flatten_json(v, new_key, sep=sep))
            else:
                items[new_key] = v
    else:
        items[parent_key] = y
    return items

def expand_item(item):
    new_item = {}
    for key, value in item.items():
        if isinstance(value, dict) and "Value" in value and "Symbol" in value:
            new_item[f"{key} Value"] = value["Value"]
            new_item[f"{key} Symbol"] = value["Symbol"]
        else:
            new_item[key] = value
    return new_item

def sqroot_of_lists(first_list, key_name1, second_list, key_name2):
    first_values = []
    second_values = []
    square_roots = []

    for i in first_list:
        for j in i:
            first_values.append(j[key_name1])

    for i in second_list:
        for j in i:
            second_values.append(j[key_name2])

    for i, element in enumerate(first_values):
        a = (first_values[i]*first_values[i] + second_values[i]*second_values[i])**0.5
        square_roots.append(a) 
    
    return(square_roots)
    

def create_excel_from_json(json_path):
    
    json_file = json_path
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    base_name = os.path.splitext(os.path.basename(json_path))[0]

    folder_path = os.path.dirname(json_file)
    excel_path = os.path.join(folder_path, f"{base_name}.xlsx")

    
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
       
        general = {k: data[k] for k in ['Analysis title', 'Analysis ID', 'Description'] if k in data}
        general_df = pd.DataFrame(list(general.items()), columns=['Parameter', 'Value'])
        general_df.to_excel(writer, sheet_name='General', index=False)
        
        inputs = data.get('Inputs', {})
        
        # Inputs_Parameters 
        inputs_params = {k: v for k, v in inputs.items() if not isinstance(v, (dict, list))}
        if inputs_params:
            inputs_params_df = pd.DataFrame(list(inputs_params.items()), columns=['Parameter', 'Value'])
            inputs_params_df.to_excel(writer, sheet_name='Inputs_Parameters', index=False)
        
        # Inputs_Soil_data
        soil_data = inputs.get('Soil data', {})
        if soil_data:
            soil_flat = flatten_json(soil_data)
            soil_df = pd.DataFrame(list(soil_flat.items()), columns=['Parameter', 'Value'])
            soil_df.to_excel(writer, sheet_name='Inputs_Soil_data', index=False)
        
        # Inputs_Pile_data
        pile_data = inputs.get('Pile data', {})
        if pile_data:
            pile_flat = flatten_json(pile_data)
            pile_df = pd.DataFrame(list(pile_flat.items()), columns=['Parameter', 'Value'])
            pile_df.to_excel(writer, sheet_name='Inputs_Pile_data', index=False)
        
        # Inputs_Load_cases
        load_cases = inputs.get('Load cases', [])
        if load_cases:
            expanded_load_cases = [expand_item(lc) for lc in load_cases]
            load_cases_df = pd.DataFrame(expanded_load_cases)
            load_cases_df.to_excel(writer, sheet_name='Inputs_Load_cases', index=False)
        
        # Inputs_Group_data
        group_data = inputs.get('Group data', [])
        if group_data:
            expanded_group_data = [expand_item(g) for g in group_data]
            group_data_df = pd.DataFrame(expanded_group_data)
            if 'Axial capacity limits' in group_data_df.columns:
                group_data_df.drop(columns=['Axial capacity limits'], inplace=True)

            sheet_name = 'Inputs_Group_data'
            group_data_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            axial_limits_rows = []
            for g in group_data:
                
                pile_no = g.get("Pile No.")
                pile_id = g.get("Pile ID")
                axial_limits = g.get("Axial capacity limits", [])
                for al in axial_limits:
                    al_expanded = expand_item(al)
                    al_expanded["Pile No."] = pile_no
                    al_expanded["Pile ID"] = pile_id
                    axial_limits_rows.append(al_expanded)
            if axial_limits_rows:
                axial_df = pd.DataFrame(axial_limits_rows)
                start_row = group_data_df.shape[0] + 3
                worksheet = writer.sheets[sheet_name]
                worksheet.write(start_row - 2, 0, "Axial capacity limits")
                axial_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
            
        
        # Sezione Outputs
        outputs = data.get('Outputs', {})
        
        # Outputs_Pile_group_behavior
        pile_group_behavior = outputs.get('Pile group behavior', {})
        if pile_group_behavior:
            pgb_flat = flatten_json(pile_group_behavior)
            pgb_df = pd.DataFrame(list(pgb_flat.items()), columns=['Parameter', 'Value'])
            pgb_df.to_excel(writer, sheet_name='Outputs_Pile_group_behavior', index=False)
        
        # Outputs_Stiffness_matrix
        stiffness_matrix = outputs.get('Stiffness matrix', {})
        if stiffness_matrix:
            stiffness_list = []
            for key, subdict in stiffness_matrix.items():
                sub_flat = flatten_json(subdict)
                sub_flat['Matrix Type'] = key
                stiffness_list.append(sub_flat)
            stiffness_df = pd.DataFrame(stiffness_list)
            cols = stiffness_df.columns.tolist()
            if 'Matrix Type' in cols:
                cols.insert(0, cols.pop(cols.index('Matrix Type')))
            stiffness_df = stiffness_df[cols]
            stiffness_df.to_excel(writer, sheet_name='Outputs_Stiffness_matrix', index=False)
        
        flexibility_matrix = outputs.get('Flexibility matrix', {})
        if flexibility_matrix:
            flexibility_list = []
            for key, subdict in flexibility_matrix.items():
                sub_flat = flatten_json(subdict)
                sub_flat['Matrix Type'] = key
                flexibility_list.append(sub_flat)
            flexibility_df = pd.DataFrame(flexibility_list)
            cols = flexibility_df.columns.tolist()
            if 'Matrix Type' in cols:
                cols.insert(0, cols.pop(cols.index('Matrix Type')))
            flexibility_df = flexibility_df[cols]
            flexibility_df.to_excel(writer, sheet_name='Outputs_Flexibility_matrix', index=False)
        
        pile_node_results = outputs.get('Pile node results', [])
        if pile_node_results:
            flattened_results = []
            for group_idx, subgroup in enumerate(pile_node_results, start=1):
                if isinstance(subgroup, list):
                    for item in subgroup:
                        if isinstance(item, list):
                            for dictns in item:
                                if isinstance(dictns, dict):
                                    flattened_results.append(dictns)
                        else:
                            print(f"Warning: expected dict but got {type(item)} in group {group_idx}")
                elif isinstance(subgroup, dict):
                    subgroup['Pile No.'] = group_idx
                    flattened_results.append(subgroup)
            

            if flattened_results:
                pn_results_df = pd.DataFrame(flattened_results)
                if 'Subgroup' in pn_results_df.columns:
                    pn_results_df = pn_results_df.drop(columns=['Subgroup'])
                cols = pn_results_df.columns.tolist()
                desired_order = []
                if "Load case No." in cols:
                    desired_order.append("Load case No.")
                    cols.remove("Load case No.")
                if "Pile No." in cols:
                    desired_order.append("Pile No.")
                    cols.remove("Pile No.")
                desired_order.extend(cols)
                pn_results_df = pn_results_df[desired_order]
                pn_results_df.to_excel(writer, sheet_name='Outputs_Pile_node_results', index=False)
        
        # Outputs_Pile_cap_response 
        pile_cap_response = outputs.get('Pile cap response', [])
        if pile_cap_response:
            pile_cap_df = pd.DataFrame(pile_cap_response)
            pile_cap_df.to_excel(writer, sheet_name='Outputs_Pile_cap_response', index=False)
        
        # Outputs_Pile_head_response
        pile_head_response = outputs.get('Pile head response', [])
        flattened_data = []

        if isinstance(pile_head_response, list):
            for item in pile_head_response:
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, dict):
                            flattened_data.append(flatten_json(sub_item))
                        else:
                            flattened_data.append({"Value": sub_item})
                elif isinstance(item, dict):
                    flattened_data.append(flatten_json(item))
                else:
                    flattened_data.append({"Value": item})
        else:
            flattened_data.append(flatten_json(pile_head_response))

        df_pile_head = pd.DataFrame(flattened_data)

        sheet_name = 'Outputs_Pile_head_response'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
            writer.sheets[sheet_name] = worksheet
        else:
            worksheet = writer.sheets[sheet_name]

        all_columns = sorted(df_pile_head.columns.tolist())

        if "Load case No." in df_pile_head.columns:
            grouped = df_pile_head.groupby("Load case No.")
        else:
            grouped = [(None, df_pile_head)]

        start_row = 0
        for load_case_no, group_df in grouped:
            group_df = group_df.reindex(columns=all_columns)
            
            title = f"Load case No.: {load_case_no}" if load_case_no is not None else "Load case No.: N/A"
            worksheet.write(start_row, 0, title)
            start_row += 1
            
            group_df.to_excel(writer, sheet_name=sheet_name, startrow=start_row, index=False)
            
            start_row += len(group_df) + 3
    

#   ____ _   _    _    ____ _____ ____  
#  / ___| | | |  / \  |  _ \_   _/ ___| 
# | |   | |_| | / _ \ | |_) || | \___ \ 
# | |___|  _  |/ ___ \|  _ < | |  ___) |
#  \____|_| |_/_/   \_\_| \_\|_| |____/ 
# --------------------------------------
#           C  H  A  R  T  S           
# --------------------------------------

def flatten_nested_list(nested):
    result = []
    if isinstance(nested, list):
        for item in nested:
            if isinstance(item, list):
                result.extend(flatten_nested_list(item))
            else:
                result.append(item)
    else:
        result.append(nested)
    return result

def main(json_file, excel_file):

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df_reinf = pd.read_excel(excel_file, sheet_name="Reinforcement", header=None)

    col_pairs = [(1, 2), (4, 5), (7, 8), (10, 11), (13, 14), (16, 17)]
    reinforcement_tables = {}
    for c1, c2 in col_pairs:
        table_name = df_reinf.iat[1, c1]  
        if pd.isna(table_name):
            continue
        x_vals = df_reinf.iloc[3:, c1]    
        y_vals = df_reinf.iloc[3:, c2]
        df_xy = pd.DataFrame({"X": x_vals, "Y": y_vals}).dropna()
        if not df_xy.empty:
            reinforcement_tables[table_name] = df_xy

    load_cases = data.get("Inputs", {}).get("Load cases", [])
    df_load_cases_info = pd.json_normalize(load_cases)

    phr = data.get("Outputs", {}).get("Pile head response", [])

    phr_flat_list = flatten_nested_list(phr)
    if not phr_flat_list:
        print("Nessun dato in 'Pile head response'.")
        return

    df_phr = pd.json_normalize(phr_flat_list, sep="_")

    required_cols = ["Load case ID", "Moment x to z", "Moment y to z", "Axial load"]
    for col in required_cols:
        if col not in df_phr.columns:
            print(f"Colonna '{col}' non trovata in 'Pile head response'.")
            return

    df_phr["M"] = (df_phr["Moment x to z"]**2 + df_phr["Moment y to z"]**2).apply(math.sqrt)
    df_phr["N"] = df_phr["Axial load"]

    fig_a, ax = plt.subplots(figsize=(10, 6))

    for table_name, df_table in reinforcement_tables.items():
        ax.plot(df_table["X"], df_table["Y"], label=table_name)

    load_case_ids = df_phr["Load case ID"].unique()
    for lc_id in load_case_ids:
        df_lc = df_phr[df_phr["Load case ID"] == lc_id]
        ax.scatter(df_lc["M"], df_lc["N"], label=lc_id)

    ax.set_xlabel("Moment (kNm)")
    ax.set_ylabel("Axial Action (kN)")
    ax.set_title("MN domain", fontsize=12, fontweight='bold')

    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    ax.grid(True, which='both', linestyle='--', alpha=0.7)

    plt.subplots_adjust(right=0.7)

    ax.legend(bbox_to_anchor=(1.04, 1), loc='upper left', borderaxespad=0)

    out_folder = os.path.dirname(json_file)
    charts_folder = os.path.join(out_folder, "CHARTS")
    
    os.makedirs(charts_folder, exist_ok=True)
    
    out_path = os.path.join(charts_folder, "MN.png")
    plt.savefig(out_path, dpi=300)
    #plt.show()
    plt.close(fig_a)
    print("Grafico MN salvato in :", out_path)




    # 4) BUBBLE
    #    - x = "y coord.Value"
    #    - y = "x coord.Value"
    #    - dimension = "Axial load"

    group_data = data.get("Inputs", {}).get("Group data", [])
    df_group = pd.json_normalize(group_data, sep="_")

    if "Pile No." not in df_group.columns:
        print("Attenzione: 'Pile No.' non trovato in Group data.")
        return

    df_group.rename(columns={
        "Pile No.": "pile_no",
        "x coord_Value": "x_val",
        "y coord_Value": "y_val"
    }, inplace=True)

    if "Pile No." in df_phr.columns:
        df_phr.rename(columns={"Pile No.": "pile_no"}, inplace=True)

    df_bubble = pd.merge(df_phr, df_group, on="pile_no", how="left")

    if "Load case No." not in df_bubble.columns:
        print("Colonna 'Load case No.' non trovata in Pile head response.")
        return

    unique_load_case_nos = df_bubble["Load case No."].unique()

    for load_case_no in sorted(unique_load_case_nos):
        df_lc = df_bubble[df_bubble["Load case No."] == load_case_no]

        fig_b, ax_b = plt.subplots(figsize=(7, 5))
        ax_b.axhline(0, color='black', linewidth=1)
        ax_b.axvline(0, color='black', linewidth=1)
        ax_b.grid(True, linestyle='--', alpha=0.7)

        scale_factor = 2.0  
        x_data = df_lc["y_val"]
        y_data = df_lc["x_val"]
        bubble_size = df_lc["Axial load"].abs() * scale_factor  

        scatter = ax_b.scatter(
            x_data, y_data,
            s=bubble_size,
            alpha=0.6,
            c="orange",  
            edgecolors="black"
        )

        for i, row in df_lc.iterrows():
            x_pt = row["y_val"]
            y_pt = row["x_val"]
            n_val = row["Axial load"]
            ax_b.text(x_pt, y_pt, f"{int(n_val)}", ha='center', va='center', fontsize=9)

        ax_b.set_xlabel("y (m)")
        ax_b.set_ylabel("x (m)")
        ax_b.set_title(f"Combination {load_case_no} - Axial Action piles head (kN)", fontsize=12, fontweight='bold')

        x_min, x_max = ax_b.get_xlim()
        y_min, y_max = ax_b.get_ylim()

        margin_x = (x_max - x_min) * 0.1
        margin_y = (y_max - y_min) * 0.1

        ax_b.set_xlim(x_min - margin_x, x_max + margin_x)
        ax_b.set_ylim(y_min - margin_y, y_max + margin_y)

        bubble_filename = f"N_bubble_LC{load_case_no}.png"
        bubble_path = os.path.join(charts_folder, bubble_filename)
        plt.savefig(bubble_path, dpi=300)
        plt.close(fig_b)
        print(f"Grafico a bolle salvato: {bubble_path}")





    # "Piles Position" 
    fig_p, ax_p = plt.subplots(figsize=(7, 5))

    x_coords = df_group["y_val"]
    y_coords = df_group["x_val"]

    ax_p.scatter(x_coords, y_coords, s=200, c="blue", edgecolors="black", alpha=0.7)

    for i, row in df_group.iterrows():
        ax_p.text(row["y_val"], row["x_val"], str(row["pile_no"]), ha='center', va='center', fontsize=9, color="white")

    ax_p.set_xlabel("y (m)")
    ax_p.set_ylabel("x (m)")
    ax_p.set_title("Piles Position", fontsize=12, fontweight='bold')
    ax_p.axhline(0, color='black', linewidth=1)
    ax_p.axvline(0, color='black', linewidth=1)
    ax_p.grid(True, linestyle='--', alpha=0.7)

    x_min, x_max = ax_p.get_xlim()
    y_min, y_max = ax_p.get_ylim()
    margin_x = (x_max - x_min) * 0.1
    margin_y = (y_max - y_min) * 0.1
    ax_p.set_xlim(x_min - margin_x, x_max + margin_x)
    ax_p.set_ylim(y_min - margin_y, y_max + margin_y)

    piles_position_path = os.path.join(charts_folder, "Piles Position.png")
    plt.savefig(piles_position_path, dpi=300)
    #plt.show()
    plt.close(fig_p)
    print(f"Grafico 'Piles Position' salvato: {piles_position_path}")



    # 6) BAR CHART  "Axial load" 
    #    - y: Pile No.
    #    - Bars: Axial load

    df_phr_bar = df_phr[["pile_no", "Load case ID", "Axial load"]].copy()

    df_phr_bar.drop_duplicates(subset=["pile_no", "Load case ID"], keep="first", inplace=True)


    pivot_phr = df_phr_bar.pivot(
        index='pile_no',
        columns='Load case ID',
        values='Axial load'
    ).fillna(0) 

    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))

    pivot_phr.plot(kind='bar', ax=ax_bar)
    
    desc = data.get("Description", "")
    match = re.search(r"PilesOpt(\d+)", desc)
    if match:
        cur_pile_opt = int(match.group(1))
    else:
        cur_pile_opt = 1 

    col_map = {
        1: "I",
        2: "Y",
        3: "AM",
        4: "BA",
        5: "BO",
        6: "CC",
        7: "CQ",
        8: "DE",
        9: "DS",
        10: "EG"
    }
    col_letter = col_map.get(cur_pile_opt, "I")

    def col_letter_to_index(letter):
        index = 0
        for char in letter.upper():
            index = index * 26 + (ord(char) - ord('A') + 1)
        return index - 1

    col_index = col_letter_to_index(col_letter)

    df_pile_data = pd.read_excel(excel_file, sheet_name="Pile data", header=None)


    col_values = df_pile_data.iloc[8:, col_index].dropna().unique()
    col_values = np.sort(col_values)

    for val in col_values:
        ax_bar.axhline(val, color='red', linestyle='--', label=f'qult_comp: {val:.2f}')
    
    tensile_ratio = data.get("Inputs", {}).get("Pile data", {}).get("Tensile / compressive axial capacity ratio", {}).get("Value", 1)
    
    for val in col_values:
        ax_bar.axhline(-(val * tensile_ratio), color='blue', linestyle='--', label=f'qult_tens: {-(val*tensile_ratio):.2f}')


    ax_bar.set_ylabel("Axial Action (kN)")
    ax_bar.set_xlabel("Pile No.")
    ax_bar.set_title("Axial Action pile heads for each load combination", fontsize=12, fontweight='bold')

    ax_bar.legend(title="Load case ID", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    ax_bar.grid(True, which='both', linestyle='--', alpha=0.7)

    plt.tight_layout()
    bar_chart_path = os.path.join(charts_folder, "N.png") 
    plt.savefig(bar_chart_path, dpi=300)
    plt.close(fig_bar)
    print(f"Grafico a barre salvato: {bar_chart_path}")



    # 7) CREAZIONE BAR CHART DI "T" (Shear action)
#    -  y: V (kN) (radice quadrata di Horizontal load x^2 + Horizontal load y^2)
#    - Bars: V    

    if "Horizontal load x" not in df_phr.columns or "Horizontal load y" not in df_phr.columns:
        print("Non trovo 'Horizontal load x' o 'Horizontal load y' in Pile head response. Impossibile creare grafico T.")
    else:
        df_phr["T"] = (df_phr["Horizontal load x"]**2 + df_phr["Horizontal load y"]**2).apply(math.sqrt)

        df_phr_bar_T = df_phr[["pile_no", "Load case ID", "T"]].copy()

        df_phr_bar_T.drop_duplicates(subset=["pile_no", "Load case ID"], keep="first", inplace=True)

        pivot_phr_T = df_phr_bar_T.pivot(
            index='pile_no',
            columns='Load case ID',
            values='T'
        ).fillna(0)

        fig_bar_T, ax_bar_T = plt.subplots(figsize=(10, 6))

        pivot_phr_T.plot(kind='bar', ax=ax_bar_T)

        ax_bar_T.set_ylabel("Shear Action (kN)")
        ax_bar_T.set_xlabel("Pile No.")
        ax_bar_T.set_title("Shear Action pile heads for each load combination", fontsize=12, fontweight='bold')

        ax_bar_T.legend(title="Load case ID", bbox_to_anchor=(1.05, 1), loc='upper left')
        
        ax_bar_T.grid(True, which='both', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        t_chart_path = os.path.join(charts_folder, "V.png")
        plt.savefig(t_chart_path, dpi=300)
        plt.close(fig_bar_T)
        print(f"Grafico a barre (T) salvato: {t_chart_path}")

    
    # 9) "Bending_Moment_Depth"
   
    pile_node_results = data.get("Outputs", {}).get("Pile node results", [])
    pile_node_results_flat = flatten_nested_list(pile_node_results)

    temp_data = []
    for node_data in pile_node_results_flat:
        depth = node_data.get("Depth", None)
        if depth is None:
            continue
        mxz = node_data.get("Bending moment x to z", 0.0)
        myz = node_data.get("Bending moment y to z", 0.0)
        M = math.sqrt(mxz**2 + myz**2)
        temp_data.append((depth, M))

    raw_depths = sorted(set(d for (d, _) in temp_data))

    def cluster_depths(depth_list, tol=1e-1):
        if not depth_list:
            return []
        clusters = [[depth_list[0]]]
        for d in depth_list[1:]:
            if abs(d - clusters[-1][-1]) <= tol:
                clusters[-1].append(d)
            else:
                clusters.append([d])
        cluster_centers = [sum(c) / len(c) for c in clusters]
        return cluster_centers

    clustered_depths = cluster_depths(raw_depths, tol=1e-1)

    from collections import defaultdict
    depth_map = defaultdict(list)

    for (depth, M) in temp_data:
        best_center = min(clustered_depths, key=lambda c: abs(c - depth))
        depth_map[best_center].append(M)

    unique_depths = sorted(depth_map.keys())

    min_vals, avg_vals, max_vals = [], [], []
    for d in unique_depths:
        Ms = depth_map[d]
        min_vals.append(np.min(Ms))
        avg_vals.append(np.mean(Ms))
        max_vals.append(np.max(Ms))

    fig_bmd, ax_bmd = plt.subplots(figsize=(6, 8))
    ax_bmd.plot(min_vals, unique_depths, label='Min', color='blue', linewidth=2)
    ax_bmd.plot(avg_vals, unique_depths, label='Average', color='black', linewidth=2)
    ax_bmd.plot(max_vals, unique_depths, label='Max', color='red', linewidth=2)

    ax_bmd.invert_yaxis()
    ax_bmd.set_xlabel("Moment (kNm)")
    ax_bmd.set_ylabel("Depth (m)")
    ax_bmd.set_title("Moment trend related to Depth", fontsize=12, fontweight='bold')
    ax_bmd.legend()
    ax_bmd.grid(True, which='both', linestyle='--', alpha=0.7)

    ax_bmd.xaxis.tick_top()
    ax_bmd.xaxis.set_label_position("top")

    plt.tight_layout()

    bmd_chart_path = os.path.join(charts_folder, "Bending_Moment_Depth.png")
    plt.savefig(bmd_chart_path, dpi=300)
    plt.close(fig_bmd)
    print(f"Grafico Bending_Moment_Depth salvato: {bmd_chart_path}")



    # 10) "Shear_Depth"
   
    pile_node_results = data.get("Outputs", {}).get("Pile node results", [])
    pile_node_results_flat = flatten_nested_list(pile_node_results)

    temp_data = []
    for node_data in pile_node_results_flat:
        depth = node_data.get("Depth", None)
        if depth is None:
            continue
        mxz = node_data.get("Shear force x to z", 0.0)
        myz = node_data.get("Shear force y to z", 0.0)
        M = math.sqrt(mxz**2 + myz**2)
        temp_data.append((depth, M))

    raw_depths = sorted(set(d for (d, _) in temp_data))

    def cluster_depths(depth_list, tol=1e-1):
        if not depth_list:
            return []
        clusters = [[depth_list[0]]]
        for d in depth_list[1:]:
            if abs(d - clusters[-1][-1]) <= tol:
                clusters[-1].append(d)
            else:
                clusters.append([d])
        cluster_centers = [sum(c) / len(c) for c in clusters]
        return cluster_centers

    clustered_depths = cluster_depths(raw_depths, tol=1e-1)

    from collections import defaultdict
    depth_map = defaultdict(list)

    for (depth, M) in temp_data:
        best_center = min(clustered_depths, key=lambda c: abs(c - depth))
        depth_map[best_center].append(M)

    unique_depths = sorted(depth_map.keys())

    min_vals, avg_vals, max_vals = [], [], []
    for d in unique_depths:
        Ms = depth_map[d]
        min_vals.append(np.min(Ms))
        avg_vals.append(np.mean(Ms))
        max_vals.append(np.max(Ms))


    fig_shd, ax_shd = plt.subplots(figsize=(6, 8))
    ax_shd.plot(min_vals, unique_depths, label='Min', color='blue', linewidth=2)
    ax_shd.plot(avg_vals, unique_depths, label='Average', color='black', linewidth=2)
    ax_shd.plot(max_vals, unique_depths, label='Max', color='red', linewidth=2)

    ax_shd.invert_yaxis()
    ax_shd.set_xlabel("Shear (kNm)")
    ax_shd.set_ylabel("Depth (m)")
    ax_shd.set_title("Shear trend related to Depth", fontsize=12, fontweight='bold')
    ax_shd.legend()
    ax_shd.grid(True, which='both', linestyle='--', alpha=0.7)

    ax_shd.xaxis.tick_top()
    ax_shd.xaxis.set_label_position("top")


    plt.tight_layout()

    shd_chart_path = os.path.join(charts_folder, "Shear_Depth.png")
    plt.savefig(shd_chart_path, dpi=300)
    plt.close(fig_shd)
    print(f"Grafico Shear_Depth salvato: {shd_chart_path}")




    # 11)  "Deflection_Depth"
   
    pile_node_results = data.get("Outputs", {}).get("Pile node results", [])
    pile_node_results_flat = flatten_nested_list(pile_node_results)

    temp_data = []
    for node_data in pile_node_results_flat:
        depth = node_data.get("Depth", None)
        if depth is None:
            continue
        mxz = node_data.get("Deflection x to z", 0.0)
        myz = node_data.get("Deflection y to z", 0.0)
        M = math.sqrt(mxz**2 + myz**2)
        temp_data.append((depth, M))

    raw_depths = sorted(set(d for (d, _) in temp_data))

    def cluster_depths(depth_list, tol=1e-1):
        if not depth_list:
            return []
        clusters = [[depth_list[0]]]
        for d in depth_list[1:]:
            if abs(d - clusters[-1][-1]) <= tol:
                clusters[-1].append(d)
            else:
                clusters.append([d])
        cluster_centers = [sum(c) / len(c) for c in clusters]
        return cluster_centers

    clustered_depths = cluster_depths(raw_depths, tol=1e-1)

    from collections import defaultdict
    depth_map = defaultdict(list)

    for (depth, M) in temp_data:
        best_center = min(clustered_depths, key=lambda c: abs(c - depth))
        depth_map[best_center].append(M)

    unique_depths = sorted(depth_map.keys())

    min_vals, avg_vals, max_vals = [], [], []
    for d in unique_depths:
        Ms = depth_map[d]
        min_vals.append(np.min(Ms))
        avg_vals.append(np.mean(Ms))
        max_vals.append(np.max(Ms))

    fig_defd, ax_defd = plt.subplots(figsize=(6, 8))
    ax_defd.plot(min_vals, unique_depths, label='Min', color='blue', linewidth=2)
    ax_defd.plot(avg_vals, unique_depths, label='Average', color='black', linewidth=2)
    ax_defd.plot(max_vals, unique_depths, label='Max', color='red', linewidth=2)

    ax_defd.invert_yaxis()
    ax_defd.set_xlabel("Deflection (kNm)")
    ax_defd.set_ylabel("Depth (m)")
    ax_defd.set_title("Deflection trend related to Depth", fontsize=12, fontweight='bold')
    ax_defd.legend()
    ax_defd.grid(True, which='both', linestyle='--', alpha=0.7)


    ax_defd.xaxis.tick_top()
    ax_defd.xaxis.set_label_position("top")

    plt.tight_layout()

    defd_chart_path = os.path.join(charts_folder, "Deflection_Depth.png")
    plt.savefig(defd_chart_path, dpi=300)
    plt.close(fig_defd)
    print(f"Grafico Deflection_Depth salvato: {defd_chart_path}")



    # 12) CREAZIONE GRAFICO "TN"
    #     -  X: V (kN), sqrt(Hx^2 + Hy^2)
    #     - Y: N (kN),  "Axial load"

    if "T" not in df_phr.columns:
        df_phr["T"] = (df_phr["Horizontal load x"]**2 + df_phr["Horizontal load y"]**2).apply(math.sqrt)

    fig_tn, ax_tn = plt.subplots(figsize=(10, 6))

    load_case_ids = df_phr["Load case ID"].unique()

    for lc_id in load_case_ids:
        df_lc = df_phr[df_phr["Load case ID"] == lc_id]
        ax_tn.scatter(df_lc["T"], df_lc["Axial load"], label=lc_id)

    max_axial = df_phr["Axial load"].max()

    centinaia_superiore = ((int(max_axial) // 100) + 1) * 100

    nuova_lista = list(range(100, centinaia_superiore + 1, 100))

    x_line = [y_val * 0.2 for y_val in nuova_lista]
    y_line = nuova_lista

    ax_tn.plot(x_line, y_line, '--', color='black', label='Shear limit = 20% Axial Action')

    ax_tn.set_xlabel("Shear (kN)")
    ax_tn.set_ylabel("Axial Action (kN)")
    ax_tn.set_title("Ratio VN", fontsize=12, fontweight='bold')
    ax_tn.grid(True, linestyle='--', alpha=0.7)
    
    ax_tn.legend(title="Load case ID", bbox_to_anchor=(1.04, 1), loc='upper left', borderaxespad=0)

    plt.tight_layout()
    tn_chart_path = os.path.join(charts_folder, "VN.png")
    plt.savefig(tn_chart_path, dpi=300)
    plt.close(fig_tn)
    print(f"Grafico TN salvato: {tn_chart_path}")







if __name__ == '__main__':
     
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='Save input and work directory paths to a text file.')
    parser.add_argument('-i', '--input', metavar='', required=True, help='Path to the input directory')
    parser.add_argument('-w', '--work', metavar='', required=True, help='Path to the work directory')
    args = parser.parse_args()

    excel_file = None

    """
    for fname in os.listdir(script_dir):
        if fname.lower().endswith("pigro_input.xlsx"):
            excel_file = os.path.join(script_dir, fname)
            break
    """

    for fname in os.listdir(args.input):
        if fname.lower().endswith("pigro_input.xlsx"):
            excel_file = os.path.join(args.input, fname)
            break



    if not excel_file:
        print("ERRORE: Nessun file Excel trovato che termini con 'pigro_input.xlsx' nella cartella dello script.")
        sys.exit(1)

    pigro_output_dir = os.path.join(args.work, "PIGRO_Output")

    if not os.path.isdir(pigro_output_dir):
        print("ERRORE: Non esiste la cartella 'PIGRO_Output' nella stessa cartella dello script.")
        sys.exit(1)

    found_json = False
    for subfolder in os.listdir(pigro_output_dir):
        subfolder_path = os.path.join(pigro_output_dir, subfolder)

        if os.path.isdir(subfolder_path):
            for item in os.listdir(subfolder_path):
                if item.lower().endswith(".json"):
                    json_file = os.path.join(subfolder_path, item)
                    found_json = True
                    print(f"Elaborazione JSON: {json_file}")
                    
                    main(json_file, excel_file)
                    create_excel_from_json(json_file)

    if not found_json:
        print("ERRORE: Nessun file JSON trovato nelle sottocartelle di 'PIGRO_Output'.")
    