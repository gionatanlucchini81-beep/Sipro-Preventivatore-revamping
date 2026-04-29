import streamlit as st
import os
from fpdf import FPDF

# --- CONFIGURAZIONE INTERFACCIA WEB ---
st.set_page_config(page_title="SiPro Energy - Preventivatore", layout="centered")

# Visualizzazione Logo nell'App
if os.path.exists("logo.png"):
    st.image("logo.png", width=250)

st.title("Generatore Preventivi Revamping")
st.write("Compila i campi sottostanti per generare il PDF professionale.")

# --- FASE 1: ACQUISIZIONE DATI TRAMITE FORM ---
with st.form("form_dati"):
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Nome e Cognome Cliente")
        indirizzo = st.text_input("Indirizzo Impianto")
    with col2:
        citta = st.text_input("Città e Provincia")
        n_vecchi = st.number_input("Numero moduli attuali", value=80, step=1)
    
    w_vecchio_singolo = st.number_input("Potenza vecchio modulo (W)", value=245, step=5)
    
    submit_button = st.form_submit_button("Calcola e Genera PDF")

# --- FASE 2: LOGICA E GENERAZIONE (Si attiva solo al click del tasto) ---
if submit_button:
    if not cliente:
        st.error("Per favore, inserisci almeno il nome del cliente.")
    else:
        # --- CALCOLI TECNICI ---
        w_nuovo_singolo = 460
        potenza_orig_kw = (n_vecchi * w_vecchio_singolo) / 1000
        potenza_max_gse = potenza_orig_kw * 1.05
        n_nuovi_moduli = int((potenza_max_gse * 1000) / w_nuovo_singolo)
        potenza_nuova_kw = (n_nuovi_moduli * w_nuovo_singolo) / 1000

        # --- CALCOLI ECONOMICI ---
        costo_smontaggio = n_vecchi * 22
        costo_smaltimento_gse = n_vecchi * 10
        costo_adeguamento_struttura = potenza_nuova_kw * 30
        costo_moduli_installati = n_nuovi_moduli * 150
        costo_minuteria = potenza_nuova_kw * 12
        costo_pratiche_fisso = 400

        subtotale_lavori = (costo_smontaggio + costo_smaltimento_gse + 
                            costo_adeguamento_struttura + costo_moduli_installati + 
                            costo_minuteria + costo_pratiche_fisso)
        
        totale_progetto = subtotale_lavori * 0.04
        imponibile = subtotale_lavori + totale_progetto
        iva = imponibile * 0.10
        totale_ivato = imponibile + iva

        # --- CREAZIONE PDF ---
        class PDF(FPDF):
            def header(self):
                if os.path.exists("logo.png"):
                    self.image("logo.png", 65, 10, 80)
                self.ln(45)
                self.set_font("Arial", "B", 15)
                self.cell(0, 10, "PREVENTIVO TECNICO ECONOMICO", 0, 1, "C")
                self.ln(5)

            def footer(self):
                self.set_y(-25)
                self.set_font("Arial", "", 7)
                info = "SiPro Energy S.r.l. - via Toscana 5, 26854 Cornegliano Laudense (LO) - info@siproenergy.com"
                self.multi_cell(0, 4, info, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        
        # Dati Cliente
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 7, f"CLIENTE: {cliente.upper()}", ln=True, fill=True, border=1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(190, 7, f"Sito: {indirizzo} - {citta}", ln=True, border=1)
        pdf.ln(10)

        # Tabella Costi (Con correzione sovrapposizione)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(140, 8, "DESCRIZIONE PRESTAZIONE", border=1, fill=True)
        pdf.cell(50, 8, "IMPORTO", border=1, ln=True, fill=True, align='C')
        pdf.set_font("Arial", "", 10)

        voci = [
            ("Smontaggio moduli esistenti e sistemazione", costo_smontaggio),
            ("Smaltimento moduli azienda cert. GSE", costo_smaltimento_gse),
            ("Fornitura e posa Solarwatt 460W", costo_moduli_installati),
            ("Adeguamento strutture esistenti", costo_adeguamento_struttura),
            ("Minuteria e materiale elettrico", costo_minuteria),
            ("Pratiche amministrative GSE", costo_pratiche_fisso),
            ("Progetto tecnico e direzione lavori ", totale_progetto)
        ]

        for desc, importo in voci:
            x, y = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(140, 8, desc, border=1)
            h = pdf.get_y() - y
            pdf.set_xy(x + 140, y)
            pdf.cell(50, h, f"Euro {importo:,.2f}", border=1, ln=True, align='R')

        # Totale
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(140, 10, "TOTALE CHIAVI IN MANO (IVA Incl.)", 0)
        pdf.cell(50, 10, f"Euro {totale_ivato:,.2f}", 0, 1, 'R')

        # Salvataggio temporaneo per il download
        nome_file = f"Preventivo_{cliente.replace(' ', '_')}.pdf"
        pdf.output(nome_file)

        # MOSTRA RISULTATO NELL'APP
        st.success(f"Preventivo per {cliente} generato!")
        
        with open(nome_file, "rb") as f:
            st.download_button(
                label="📥 Scarica il Preventivo PDF",
                data=f,
                file_name=nome_file,
                mime="application/pdf"
            )