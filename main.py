import streamlit as st
from fpdf import FPDF

# Configurazione pagina
st.set_page_config(page_title="SiPro Energy - Preventivatore", layout="wide")

LOGO_PATH = "logo.png"

def create_pdf(dati):
    pdf = FPDF()
    pdf.add_page()
    
    # Intestazione con Logo
    try:
        pdf.image(LOGO_PATH, 10, 8, 33)
    except:
        pass
    
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 10, 'PREVENTIVO TECNICO ECONOMICO', 0, 1, 'C')
    pdf.ln(15)

    # Dati Cliente
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"SPETT.LE CLIENTE: {dati['cliente'].upper()}", 0, 1)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Sito: {dati['sito']}", 0, 1)
    pdf.ln(5)

    # DETTAGLIO TECNICO
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "DETTAGLIO INTERVENTO DI REVAMPING", 0, 1, 'L', True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Potenza impianto attuale: {dati['potenza_v']} kWp", 0, 1)
    pdf.cell(0, 7, f"Nuova potenza installata: {dati['potenza_n']} kWp", 0, 1)
    pdf.cell(0, 7, f"Moduli previsti: {dati['moduli_d']}", 0, 1)
    pdf.ln(8)

    # Tabella Costi
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "DESCRIZIONE PRESTAZIONE", 1, 0, 'C', True)
    pdf.cell(50, 10, "IMPORTO", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 10)
    imponibile = 0
    for riga in dati['voci']:
        if riga['desc'] and riga['prezzo'] > 0:
            pdf.cell(140, 10, riga['desc'], 1)
            pdf.cell(50, 10, f"Euro {riga['prezzo']:,.2f}", 1, 1, 'R')
            imponibile += riga['prezzo']

    # Totali
    iva = imponibile * 0.10
    totale = imponibile + iva
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "TOTALE IMPONIBILE", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {imponibile:,.2f}", 0, 1, 'R')
    pdf.cell(140, 8, "IVA AGEVOLATA 10%", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {iva:,.2f}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(140, 10, "TOTALE CHIAVI IN MANO", 0, 0, 'R')
    pdf.cell(50, 10, f"Euro {totale:,.2f}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

# INTERFACCIA STREAMLIT
st.title("Preventivatore SiPro Energy")

with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Spett.le Cliente")
        sito = st.text_input("Sito (Indirizzo/Città)")
    with col2:
        pot_v = st.text_input("Potenza impianto attuale (kWp)")
        pot_n = st.text_input("Nuova potenza installata (kWp)")
    
    mod_d = st.text_input("Moduli previsti (es. n. 44 Solarwatt 460W)")
    
    st.write("---")
    st.subheader("Tabella Costi (come da tuo screenshot)")
    
    voci_list = []
    for i in range(7):
        c_desc, c_prezzo = st.columns([3, 1])
        desc = c_desc.text_input(f"Descrizione {i+1}", key=f"d{i}")
        prezzo = c_prezzo.number_input(f"Prezzo {i+1}", min_value=0.0, step=100.0, key=f"p{i}")
        voci_list.append({"desc": desc, "prezzo": prezzo})
    
    submit = st.form_submit_button("Genera Preventivo PDF")

if submit:
    dati_finali = {
        "cliente": cliente, "sito": sito, "potenza_v": pot_v,
        "potenza_n": pot_n, "moduli_d": mod_d, "voci": voci_list
    }
    pdf_out = create_pdf(dati_finali)
    st.download_button("Scarica Preventivo PDF", data=pdf_out, file_name=f"Preventivo_{cliente}.pdf", mime="application/pdf")