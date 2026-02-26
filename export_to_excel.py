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
        
        # Flattening the nested folders from your gg.html payload
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

    df = pd.DataFrame(data_list)
    file_name = f"Univation_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    # 2. Advanced Styling with XlsxWriter
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Applicants')
    
    workbook  = writer.book
    worksheet = writer.sheets['Applicants']

    # --- DEFINE STYLES ---
    header_format = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'vcenter', 'align': 'center',
        'fg_color': '#2D4BFF', 'font_color': 'white', 'border': 1
    })
    
    warning_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'}) # Red for flags
    clean_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})   # Green for trust
    
    # --- APPLY STYLING ---
    # 1. Format Headers
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # 2. Set Column Widths
    worksheet.set_column('A:B', 15) # ID and Name
    worksheet.set_column('C:C', 20) # Date
    worksheet.set_column('D:F', 25) # Contacts
    worksheet.set_column('G:I', 35) # Content/Vision
    worksheet.set_column('J:L', 15) # Security
    worksheet.set_column('M:P', 15) # Behavior

    # 3. Conditional Formatting: Highlight LOW_TRUST scores or Tamper=YES
    worksheet.conditional_format(1, 9, len(df), 9, {
        'type': 'cell', 'criteria': 'equal to', 'value': '"LOW_TRUST"', 'format': warning_format
    })
    worksheet.conditional_format(1, 10, len(df), 10, {
        'type': 'cell', 'criteria': 'equal to', 'value': '"YES"', 'format': warning_format
    })

    # 4. Freeze the top row & add filters
    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

    writer.close()
    print(f"✅ Professional Report Generated: {file_name}")

if __name__ == "__main__":
    export_styled_report()