# notªpad v0.1 – scheda singola 51 × 51 mm per NextPCB (Rev 0, PCBA)

NextPCB Rev 0 non accetta pannelli già fatti: si ordina una scheda singola da 51 × 51 mm (le guide le aggiungono loro). Il circuito notªpad (16,5 × 38 mm) sta nell'angolo in basso a sinistra del quadrato; il resto è FR4 nudo, senza rame.

## Parametri d'ordine
- **Single PCB** · dimensione **51 × 51 mm** · quantità **5** (tutte montate se possibile)
- Strati **4** · spessore **1,0 mm** · finitura **ENIG** · Tented vias · solder mask verde, serigrafia bianca
- Assemblaggio (PCBA): lato **Top**; stencil Top (F.Paste è nello ZIP)
- Pista/spazio 0,10/0,10 mm · via 0,25/0,45 mm · rame-bordo 0,25 mm

## File
- `notapad_v0.1_scheda_51x51_gerber_4strati.zip`: Gerber + drill Excellon (PTH e NPTH), con F.Paste. Un solo contorno Edge.Cuts: il quadrato 51 × 51
- `notapad_v0.1_BOM.csv` / `.xlsx`: BOM senza righe DNP (19 righe)
- `notapad_v0.1_centroid.csv`: posizioni mm con origine nell'angolo alto-sinistro del quadrato (come nei Gerber), Y come nei file pos di KiCad, solo Top; scheda solo traslata (nessuna rotazione), rotazioni invariate
- `scheda_51x51_sopra.png`: anteprima · `drc_scheda.rpt`: DRC (0 violazioni, rame-bordo compreso) · `progetto_scheda/`: file KiCad
- Script: `kicad/pannello/crea_scheda_51x51.py`

## Da fare dopo la consegna
Il lato antenna (corto, in basso) e un lato lungo (sinistro) della scheda coincidono con il bordo del quadrato. Gli altri due lati vanno **tagliati a mano lungo la linea tratteggiata in serigrafia** (fronte e retro, 0,3 mm fuori dal contorno, scritta CUT), poi **limati**: i tre angoli arrotondati interni sono segnati con un trattino in serigrafia. Il rame della scheda è a ≥ 0,25 mm dal contorno originale, quindi non c'è rame sulla linea.
Nessun rame nel materiale aggiunto, antenna compresa: il keepout resta libero.
