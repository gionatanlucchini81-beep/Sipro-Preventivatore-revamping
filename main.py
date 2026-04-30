import streamlit as st
from fpdf import FPDF
import math

st.set_page_config(page_title="SiPro Energy - Preventivatore Smart", layout="centered")

def format_euro(valore):
    """Formatta il numero come intero con separatore delle migliaia."""
    return f"{int(round(valore)):,}".replace(",", ".")

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
    pdf.cell(0, 7, f"Impianto originale: n. {dati['n_vecchi']} moduli da {dati['w_vecchi']}W (Totale: {dati['potenza_vecchia_kw']:.2f} kWp)", 0, 1)
    pdf.cell(0, 7, f"Nuova installazione: n. {dati['n_nuovi']} moduli Solarwatt da 460W", 0, 1)
    pdf.cell(0, 7, f"Nuova potenza installata: {dati['potenza_nuova_kw']:.2f} kWp", 0, 1)
    pdf.ln(8)

    # Tabella Costi - Senza Decimali
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 10, "DESCRIZIONE PRESTAZIONE", 1, 0, 'C', True)
    pdf.cell(50, 10, "IMPORTO", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 10)
    for voce, importo in dati['voci']:
        pdf.cell(140, 10, voce, 1)
        pdf.cell(50, 10, f"Euro {format_euro(importo)}", 1, 1, 'R')

    # Totali - Senza Decimali
    pdf.ln(5)
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 8, "Totale lavori", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {format_euro(dati['subtotale'])}", 0, 1, 'R')
    pdf.cell(140, 8, "Progetto tecnico e gestione pratiche (4%)", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {format_euro(dati['totale_progetto'])}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "TOTALE IMPONIBILE", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {format_euro(dati['imponibile'])}", 0, 1, 'R')
    
    iva = dati['imponibile'] * 0.10
    pdf.cell(140, 8, "IVA AGEVOLATA 10%", 0, 0, 'R')
    pdf.cell(50, 8, f"Euro {format_euro(iva)}", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(140, 10, "TOTALE CHIAVI IN MANO", 0, 0, 'R')
    pdf.cell(50, 10, f"Euro {format_euro(dati['imponibile'] + iva)}", 0, 1, 'R')
    
    return pdf.output(dest='S').encode('latin-1')

st.title("☀️ SiPro Energy - Preventivatore Professionale")

with st.form("clean_form"):
    cliente = st.text_input("Spett.le Cliente")
    sito = st.text_input("Località Impianto")
    
    col1, col2 = st.columns(2)
    with col1:
        n_vecchi = st.number_input("N. vecchi moduli", min_value=1, value=80)
    with col2:
        w_vecchi = st.number_input("Watt vecchio modulo", min_value=1, value=245)
    
    submit = st.form_submit_button("CALCOLA E GENERA PDF")

if submit:
    # --- LOGICA CALCOLI CON ARROTONDAMENTI ---
    potenza_vecchia_kw = (n_vecchi * w_vecchi) / 1000
    n_nuovi = math.ceil(potenza_vecchia_kw / 0.460)
    potenza_nuova_kw = (n_nuovi * 460) / 1000
    
    # Valori arrotondati
    c_smontaggio = round(n_vecchi * 22)
    c_smaltimento = round(n_vecchi * 10)
    c_adeguamento = round(potenza_nuova_kw * 30)
    c_moduli = round(n_nuovi * 150)
    c_minuteria = round(potenza_nuova_kw * 12)
    c_pratiche = 400
    
    subtotale = c_smontaggio + c_smaltimento + c_adeguamento + c_moduli + c_minuteria + c_pratiche
    totale_progetto = round(subtotale * 0.04)
    imponibile = subtotale + totale_progetto
    
    voci = [
        (f"Smontaggio e movimentazione a terra n. {n_vecchi} moduli", c_smontaggio),
        (f"Smaltimento moduli presso azienda certificata GSE", c_smaltimento),
        (f"Fornitura e posa n. {n_nuovi} nuovi moduli Solarwatt 460W", c_moduli),
        (f"Adeguamento strutture di sostegno esistenti", c_adeguamento),
        (f"Minuteria, connettori e materiale elettrico", c_minuteria),
        (f"Oneri per pratiche amministrative e connessione", c_pratiche)
    ]
    
    dati_pdf = {
        "cliente": cliente, "sito": sito, "n_vecchi": n_vecchi, "w_vecchi": w_vecchi,
        "potenza_vecchia_kw": potenza_vecchia_kw, "n_nuovi": n_nuovi, 
        "potenza_nuova_kw": potenza_nuova_kw, "voci": voci, 
        "subtotale": subtotale, "totale_progetto": totale_progetto, "imponibile": imponibile
    }
    
    st.success(f"✅ Calcolo completato per {cliente}")
    pdf_bytes = create_pdf(dati_pdf)
    st.download_button("SCARICA PREVENTIVO PDF", data=pdf_bytes, file_name=f"Preventivo_{cliente}.pdf")