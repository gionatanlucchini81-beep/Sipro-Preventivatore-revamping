import streamlit as st
from fpdf import FPDF
import math

st.set_page_config(page_title="SiPro Energy - Preventivatore", layout="centered")

def format_euro(valore):
    """Formatta il numero come intero con separatore delle migliaia."""
    return f"{int(round(valore)):,}".replace(",", ".")

class PDF(FPDF):
    def footer(self):
        # Posizionamento a 1.5 cm dal basso
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100)
        # Linea sottile sopra il piè di pagina
        self.set_draw_color(0, 51, 102)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        # Dati Aziendali
        self.cell(0, 4, 'SiPro Energy S.r.l. - Sede legale e operativa: via Toscana 5, 26854 Cornegliano Laudense (LO)', 0, 1, 'C')
        self.cell(0, 4, 'CF e P.IVA 06759690966 - Tel. +39 0371 483329 - info@siproenergy.com - www.siproenergy.com', 0, 1, 'C')

def create_pdf(dati):
    pdf = PDF()
    pdf.add_page()
    
    # 1. LOGO CENTRALE E PIU' GRANDE
    try:
        # Posizionamento centrale: (210mm larghezza pagina - 60mm larghezza logo) / 2 = 75mm
        pdf.image("logo.png", x=75, y=10, w=60)
    except:
        pass
    
    pdf.ln(35) # Spazio dopo il logo

    # 2. TITOLO PIU' IN VISTA
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(0, 51, 102) # Blu istituzionale
    pdf.cell(0, 12, 'PREVENTIVO TECNICO ECONOMICO', 0, 1, 'C')
    pdf.set_draw_color(0, 51, 102)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y()) # Linea estetica sotto il titolo
    pdf.ln(10)

    # 3. BLOCCO CLIENTE (Elegante a sinistra)
    pdf.set_text_color(0)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, f"SPETT.LE CLIENTE: {dati['cliente'].upper()}", 0, 1)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 7, f"Sito d'installazione: {dati['sito']}", 0, 1)
    pdf.ln(8)

    # 4. DETTAGLIO TECNICO (Box Colorato)
    pdf.set_fill_color(240, 245, 250) # Blu molto chiaro
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "  DETTAGLIO INTERVENTO DI REVAMPING", 0, 1, 'L', True)
    pdf.set_font("Arial", '', 10)
    pdf.ln(2)
    pdf.cell(0, 6, f"   • Impianto originale: n. {dati['n_vecchi']} moduli da {dati['w_vecchi']}W ({dati['potenza_vecchia_kw']:.2f} kWp)", 0, 1)
    pdf.cell(0, 6, f"   • Nuova configurazione: n. {dati['n_nuovi']} moduli Solarwatt 460W (Vetro-Vetro)", 0, 1)
    pdf.cell(0, 6, f"   • Nuova potenza totale: {dati['potenza_nuova_kw']:.2f} kWp", 0, 1)
    pdf.ln(10)

    # 5. TABELLA PRESTAZIONI
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(0, 51, 102) # Blu scuro per intestazione
    pdf.set_text_color(255) # Testo bianco
    pdf.cell(145, 10, " DESCRIZIONE PRESTAZIONE", 1, 0, 'L', True)
    pdf.cell(45, 10, "IMPORTO ", 1, 1, 'R', True)
    
    pdf.set_text_color(0)
    pdf.set_font("Arial", '', 10)
    for i, (voce, importo) in enumerate(dati['voci']):
        # Colore alternato per le righe (Zebra)
        fill = (i % 2 == 0)
        if fill: pdf.set_fill_color(250, 250, 250)
        else: pdf.set_fill_color(255, 255, 255)
        
        pdf.cell(145, 10, f" {voce}", 1, 0, 'L', fill)
        pdf.cell(45, 10, f"Euro {format_euro(importo)} ", 1, 1, 'R', fill)

    # 6. TOTALI (Evidenziati)
    pdf.ln(5)
    pdf.set_font("Arial", '', 11)
    pdf.cell(145, 8, "TOTALE NETTO LAVORI ", 0, 0, 'R')
    pdf.cell(45, 8, f"Euro {format_euro(dati['subtotale'])} ", 0, 1, 'R')
    
    pdf.cell(145, 8, "PROGETTAZIONE E GESTIONE TECNICA (4%) ", 0, 0, 'R')
    pdf.cell(45, 8, f"Euro {format_euro(dati['totale_progetto'])} ", 0, 1, 'R')
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(145, 8, "TOTALE IMPONIBILE ", 0, 0, 'R')
    pdf.cell(45, 8, f"Euro {format_euro(dati['imponibile'])} ", 0, 1, 'R')
    
    iva = dati['imponibile'] * 0.10
    pdf.cell(145, 8, "IVA AGEVOLATA 10% ", 0, 0, 'R')
    pdf.cell(45, 8, f"Euro {format_euro(iva)} ", 0, 1, 'R')
    
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 13)
    pdf.set_text_color(0, 51, 102)
    pdf.set_draw_color(0, 51, 102)
    pdf.cell(145, 12, "TOTALE CHIAVI IN MANO (IVA Inclusa) ", 'T', 0, 'R')
    pdf.cell(45, 12, f"Euro {format_euro(dati['imponibile'] + iva)} ", 'T', 1, 'R')
    
    # 7. NOTA SOPRALLUOGO
    pdf.ln(5)
    pdf.set_text_color(0)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, 'Nota: Per i costi inerenti alla messa in sicurezza della copertura sarà valutata a parte successivamente al sopralluogo effettuato.', 0, 'L')
    
    return pdf.output()

st.title("☀️ SiPro Energy - Preventivatore")

with st.form("main_form"):
    cliente = st.text_input("Spett.le Cliente")
    sito = st.text_input("Località Impianto")
    col1, col2 = st.columns(2)
    with col1:
        n_vecchi = st.number_input("N. vecchi moduli", min_value=1, value=150)
    with col2:
        w_vecchi = st.number_input("Watt vecchio modulo", min_value=1, value=245)
    submit = st.form_submit_button("CALCOLA E GENERA PDF PROFESSIONALE")

if submit:
    # Calcoli economici SiPro Energy[cite: 1, 2]
    potenza_vecchia_kw = (n_vecchi * w_vecchi) / 1000
    n_nuovi = math.ceil(potenza_vecchia_kw / 0.460)
    potenza_nuova_kw = (n_nuovi * 460) / 1000
    
    c_smontaggio = round(n_vecchi * 22)[cite: 1, 2]
    c_smaltimento = round(n_vecchi * 10)[cite: 1, 2]
    c_adeguamento = round(potenza_nuova_kw * 30)[cite: 1, 2]
    c_moduli = round(n_nuovi * 150)[cite: 1, 2]
    c_minuteria = round(potenza_nuova_kw * 12)[cite: 1, 2]
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
    
    pdf_output = create_pdf(dati_pdf)
    st.success(f"✅ Preventivo per {cliente} generato con successo!")
    st.download_button(
        label="📥 SCARICA PREVENTIVO PDF",
        data=bytes(pdf_output),
        file_name=f"Preventivo_{cliente}.pdf",
        mime="application/pdf"
    )
