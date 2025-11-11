import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    return client.open("MobilitePB_Groupes").sheet1

def sauvegarder_donnees(code_groupe, data):
    sheet = get_sheet()
    # Chercher ligne du groupe ou créer
    row = [code_groupe, data['population'], data['km_voiture'], ...]
    sheet.append_row(row)

def charger_donnees(code_groupe):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for rec in records:
        if rec['groupe'] == code_groupe:
            return rec
    return None
