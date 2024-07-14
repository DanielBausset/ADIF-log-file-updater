import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def read_adif(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    content_lower = content.lower()
    header_end_index = content_lower.index('<eoh>') + len('<eoh>')
    header = content[:header_end_index]
    records = re.split(r'<eor>', content[header_end_index:], flags=re.IGNORECASE)
    return header, records

def parse_record(record):
    fields = {}
    while '<' in record:
        record = record.split('<', 1)[1]
        if '>' in record:
            key_val = record.split('>', 1)
            key_size = key_val[0].split(':')
            key = key_size[0].strip().upper()
            if len(key_size) == 2:
                size = int(key_size[1].strip())
                value = key_val[1][:size].strip()
                record = key_val[1][size:]
            else:
                value = key_val[1].split('<', 1)[0].strip()
                record = '<' + key_val[1].split('<', 1)[1] if '<' in key_val[1] else ''
            fields[key] = value
    return fields

def update_log(path_log_Grids, path_log_WSJT, path_output):
    headerA, recordsA = read_adif(path_log_Grids)
    headerB, recordsB = read_adif(path_log_WSJT)

    # Parse records into dictionaries
    parsed_recordsA = [parse_record(record) for record in recordsA if record.strip()]
    parsed_recordsB = [parse_record(record) for record in recordsB if record.strip()]

    # Convert to DataFrame for easier processing
    dfA = pd.DataFrame(parsed_recordsA)
    dfB = pd.DataFrame(parsed_recordsB)

    # Convert column names to uppercase to ignore case
    dfA.columns = dfA.columns.str.upper()
    dfB.columns = dfB.columns.str.upper()

    # Check for required columns
    required_columns = ['CALL', 'QSO_DATE', 'TIME_ON', 'GRIDSQUARE']
    optional_columns = ['TX_PWR', 'OPERATOR']
    missing_columns_A = [col for col in required_columns if col not in dfA.columns]
    missing_columns_B = [col for col in required_columns if col not in dfB.columns]

    if missing_columns_A:
        raise KeyError(f"Missing columns in log file containing grids: {missing_columns_A}")
    if missing_columns_B:
        raise KeyError(f"Missing columns in WSJT log file: {missing_columns_B}")

    # Merge DataFrames on CALL, QSO_DATE, TIME_ON
    merge_columns = required_columns + [col for col in optional_columns if col in dfA.columns]
    dfA_subset = dfA[merge_columns]
    merged_df = pd.merge(dfB, dfA_subset, on=['CALL', 'QSO_DATE', 'TIME_ON'], how='left', suffixes=('', '_A'))

    # Update GRIDSQUARE, TX_PWR, and OPERATOR in dfB with values from dfA (truncate GRIDSQUARE to 4 characters)
    merged_df['GRIDSQUARE'] = merged_df['GRIDSQUARE_A'].str[:4].combine_first(merged_df['GRIDSQUARE'])
    for col in optional_columns:
        if f"{col}_A" in merged_df.columns:
            merged_df[col] = merged_df[f"{col}_A"].combine_first(merged_df[col])

    # Drop the auxiliary columns
    merged_df.drop(columns=[f"{col}_A" for col in optional_columns if f"{col}_A" in merged_df.columns], inplace=True)
    merged_df.drop(columns=['GRIDSQUARE_A'], inplace=True)

    # Convert DataFrame back to list of records
    updated_recordsB = []
    for _, row in merged_df.iterrows():
        record = ' '.join([f'<{col.lower()}:{len(str(val))}>{val}' for col, val in row.items() if pd.notna(val)])
        updated_recordsB.append(record + ' <eor>')

    # Write the updated records to the output file
    with open(path_output, 'w') as f:
        f.write(headerB + '\n')
        for record in updated_recordsB:
            f.write(record + '\n')

    print(f"Done. Total number of QSOs processed: {len(merged_df)}")

def select_files_and_run():
    root = tk.Tk()
    root.withdraw()

    default_dir_in = "/Users/Danny/Downloads"
    default_dir_out = "/Users/Danny/Library/Application Support/WSJT-X/logs"
    default_file_out = "wsjtx_log updated.adi"

    path_log_Grids = filedialog.askopenfilename(title="Select log file containing grids", initialdir=default_dir_in, filetypes=[("ADIF files", "*.adi")])
    path_log_WSJT = filedialog.askopenfilename(title="Select WSJT log file to update", initialdir=default_dir_out, filetypes=[("ADIF files", "*.adi")])
    path_output = filedialog.asksaveasfilename(title="Save WSJT log file as", initialfile=default_file_out, initialdir=default_dir_out, defaultextension=".adi", filetypes=[("ADIF files", "*.adi")])

    if path_log_Grids and path_log_WSJT and path_output:
        update_log(path_log_Grids, path_log_WSJT, path_output)
    else:
        print("Files selection was cancelled.")

if __name__ == "__main__":
    select_files_and_run()
