import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="SiPro Energy - Calcolatore Revamping", layout="centered")

def create_pdf(dati):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.image("logo.png", 10, 8, 33)
    except:
        pass
    
    pdf.set_font("Arial", 'B', 15)
    pdf.cell(0, 10, 'PREVENTIVO TECNICO ECONOMICO', 0, 1, 'C')
    pdf.ln(10)

    # Dati Cliente
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"SPETT.LE CLIENTE: {dati['cliente'].upper()}", 0, 1)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Sito: {dati['sito']}", 0, 1)
    pdf.ln(5)

    # Dettaglio Tecnico
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "DETTAGLIO INTERVENTO DI REVAMPING", 0, 1, 'L', True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Moduli rimossi: n. {dati['n_vecchi']}", 0, 1)
    pdf.cell(0, 7, f"Nuovi moduli previsti: n. {dati['n_nuovi']} da 460W", 0, 1)
    pdf.cell(0, 7, f"Nuova potenza installata: {dati['potenza_nuova_kw']} kWp", 0, 1)
    pdf.ln(8)

    # Tabella Costi Automatica
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "DESCRIZIONE PRESTAZIONE", 1, 0, 'C', True)
    pdf.cell(50, 10, "IMPORTO", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 10)
    for voce, importo in dati['voci']:
        pdf.cell(140, 10, voce, 1)
        pdf.cell(50, 10, f"Euro {importo:,.2f}", 1, 1, 'R')

    # Totali
    subtotale = dati['subtotale']
    totale_progetto = dati['totale_progetto']
    imponibile = dati['imponibile']
    iva = imponibile * 0.10
    
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 8, "Totale lavori", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {subtotale:,.2f}", 0, 1, 'R')
    pdf.cell(140, 8, "Progetto tecnico e gestione pratiche (4%)", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {totale_progetto:,.2f}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "TOTALE IMPONIBILE", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {imponibile:,.2f}", 0, 1, 'R')
    pdf.cell(140, 8, "IVA AGEVOLATA 10%", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {iva:,.2f}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(140, 10, "TOTALE CHIAVI IN MANO", 0, 0, 'R')
    pdf.cell(50, 10, f"Euro {imponibile + iva:,.2f}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

st.title("☀️ SiPro Energy - Automazione Revamping")

with st.form("calcolatore_form"):
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Spett.le Cliente")
        sito = st.text_input("Località Impianto")
    with col2:
        n_vecchi = st.number_input("Numero moduli da smontare", min_value=1, value=80)
        n_nuovi = st.number_input("Numero nuovi moduli da 460W", min_value=1, value=44)
    
    submit = st.form_submit_button("CALCOLA E GENERA PDF")

if submit:
    # --- LOGICA CALCOLI DAL TUO SCHEMA ---
    potenza_nuova_kw = (n_nuovi * 460) / 1000
    
    c_smontaggio = n_vecchi * 22
    c_smaltimento = n_vecchi * 10
    c_adeguamento = potenza_nuova_kw * 30
    c_moduli = n_nuovi * 150
    c_minuteria = potenza_nuova_kw * 12
    c_pratiche = 400.0
    
    subtotale = c_smontaggio + c_smaltimento + c_adeguamento + c_moduli + c_minuteria + c_pratiche
    totale_progetto = subtotale * 0.04
    imponibile = subtotale + totale_progetto
    
    voci = [
        (f"Smontaggio e movimentazione a terra n. {n_vecchi} moduli", c_smontaggio),
        (f"Smaltimento moduli presso azienda certificata GSE", c_smaltimento),
        (f"Fornitura e posa n. {n_nuovi} nuovi moduli 460W", c_moduli),
        (f"Adeguamento strutture di sostegno esistenti", c_adeguamento),
        (f"Minuteria, connettori e materiale elettrico", c_minuteria),
        (f"Oneri per pratiche amministrative e connessione", c_pratiche)
    ]
    
    dati_pdf = {
        "cliente": cliente, "sito": sito, "n_vecchi": n_vecchi,
        "n_nuovi": n_nuovi, "potenza_nuova_kw": potenza_nuova_kw,
        "voci": voci, "subtotale": subtotale, "totale_progetto": totale_progetto,
        "imponibile": imponibile
    }
    
    pdf_bytes = create_pdf(dati_pdf)
    st.success(f"Preventivo generato per {cliente}! Totale: € {imponibile*1.1:,.2f}")
    st.download_button("SCARICA PREVENTIVO PDF", data=pdf_bytes, file_name=f"Preventivo_{cliente}.pdf")