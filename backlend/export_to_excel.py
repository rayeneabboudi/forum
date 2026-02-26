import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import datetime

# 1. Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

def export_styled_report():
    print("📋 Fetching applicant data...")
    docs = db.collection("applicants").stream()
    
    data_list = []
    for doc in docs:
        d = doc.to_dict()
        row = {
            # ZONE A: IDENTITY
            "ID": d.get("doc_meta", {}).get("id"),
            "Name": d.get("doc_meta", {}).get("name"),
            "Submitted At": d.get("doc_meta", {}).get("submitted"),
            "Discord/Email": d.get("content", {}).get("discord"),
            "Phone": d.get("content", {}).get("number"),
            "Academic": d.get("content", {}).get("academic"),
            
            # ZONE B: CONTENT
            "Skills": ", ".join(d.get("content", {}).get("skills", [])),
            "Proficiency": d.get("content", {}).get("proficiency"),
            "Vision Statement": d.get("content", {}).get("vision"),
            
            # ZONE C: SECURITY AUDIT
            "Integrity Score": d.get("security_audit", {}).get("integrity_score"),
            "Tamper Detected": "YES" if d.get("security_audit", {}).get("tamper_detected") else "No",
            "Is Bot": "YES" if d.get("security_audit", {}).get("is_bot") else "No",
            
            # ZONE D: BEHAVIORAL FORENSICS
            "Total Time (s)": d.get("behavioral_forensics", {}).get("session", {}).get("total_duration_sec"),
            "Tab Switches": d.get("behavioral_forensics", {}).get("session", {}).get("tab_switches"),
            "Away Time (s)": d.get("behavioral_forensics", {}).get("session", {}).get("away_duration_sec"),
            "Name Field Ghost Text": d.get("behavioral_forensics", {}).get("field_history", {}).get("entry_name", {}).get("ghost_text_summary")
        }
        data_list.append(row)

    if not data_list:
        print("❌ No data found to export.")
        return

    df = pd.DataFrame(data_list)
    file_name = f"Univation_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Applicants')
    
    workbook  = writer.book
    worksheet = writer.sheets['Applicants']

    # --- UPDATED STYLES ---
    # Header: Added dark blue theme with white text
    header_format = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center',
        'fg_color': '#1F4E78', 'font_color': 'white', 'border': 1
    })
    
    # Body: THIS IS THE FIX. 'text_wrap': True and 'valign': 'top' ensures long text shows fully.
    body_format = workbook.add_format({
        'text_wrap': True, 
        'valign': 'top',
        'border': 1
    })

    warning_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'text_wrap': True, 'valign': 'top', 'border': 1})
    
    # --- APPLY STYLING ---
    # 1. Apply Header Format
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # 2. Apply Body Format to all data cells (Fixes the "cut off" text)
    for row_num in range(1, len(df) + 1):
        for col_num in range(len(df.columns)):
            # We use worksheet.write to re-apply the body format to existing data
            val = df.iloc[row_num-1, col_num]
            worksheet.write(row_num, col_num, val, body_format)

    # 3. Optimized Column Widths
    worksheet.set_column('A:B', 18) # ID and Name
    worksheet.set_column('C:C', 20) # Date
    worksheet.set_column('D:F', 25) # Contacts
    worksheet.set_column('G:I', 50) # INCREASED: Content/Vision (Needs more space)
    worksheet.set_column('J:L', 15) # Security
    worksheet.set_column('M:P', 25) # INCREASED: Behavior/Ghost Text

    # 4. Conditional Formatting (Red flags)
    worksheet.conditional_format(1, 9, len(df), 9, {
        'type': 'cell', 'criteria': 'equal to', 'value': '"LOW_TRUST"', 'format': warning_format
    })
    worksheet.conditional_format(1, 10, len(df), 10, {
        'type': 'cell', 'criteria': 'equal to', 'value': '"YES"', 'format': warning_format
    })

    # 5. Freeze and Filter
    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    writer.close()
    print(f"✅ Professional Report Generated: {file_name}")
if __name__ == "__main__":
    export_styled_report()