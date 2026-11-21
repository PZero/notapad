# notªpad v0.1 – pannello 52 × 52 mm per NextPCB (PCBA)

Un pannello con UNA scheda al centro, fatto da noi: nel modulo d'ordine NextPCB si sceglie "Panel by Customer", 1 scheda per pannello.

## Parametri d'ordine
- Tipo: **Panel by Customer** (1 scheda per pannello, non "Single PCB") · dimensione **52 × 52 mm** (serve > 50 × 50 mm per l'assemblaggio)
- Strati: **4** · spessore **1,0 mm** · finitura **ENIG** · Tented vias · solder mask verde, serigrafia bianca
- Assemblaggio (PCBA): lato **Top**, stencil **Top** (F.Paste è nello ZIP)
- Pista/spazio 0,10/0,10 mm · via 0,25/0,45 mm · rame-bordo 0,25 mm
- NON montare (DNP, a mano): J1–J4, BT1P/BT1N, M1P/M1N, TPA/TPB

## File
- `notapad_v0.1_pannello_52x52_gerber_4strati.zip`: Gerber + drill Excellon (PTH e NPTH), con F.Paste
- `notapad_v0.1_BOM.csv` / `.xlsx`: BOM (identica alla scheda singola)
- `notapad_v0.1_centroid.csv`: posizioni nel pannello (mm, origine del pannello = origine dei Gerber, Y come nei file pos di KiCad), solo Top, rotazioni invariate (la scheda è solo traslata, non ruotata). J1–J4 e i pad DNP esclusi
- `pannello_52x52_sopra.png`: anteprima; `drc_pannello.rpt`: DRC (0 violazioni); `progetto_pannello/`: file KiCad del pannello
- Script: `kicad/pannello/crea_pannello_5x5.py`

## Disposizione
- Scheda centrata (angolo alto-sx a x 17,75 / y 7,00 mm), lati lunghi verticali: contatti dorati in alto, antenna in basso.
- Guide di trasporto: i lati sinistro e destro (15,75 mm ciascuna) con 3 fiducial (rame 1 mm, apertura maschera 2 mm, posizioni non simmetriche) e 4 fori di riferimento NPTH Ø2 mm. Guide alta e bassa da 5 mm; sotto l'antenna 5 mm di pannello senza rame.
- Fessura fresata da 2 mm tutto intorno alla scheda, con 4 linguette da 4 mm (2 per lato lungo, a 11 e 26 mm dal bordo alto della scheda), lontane da antenna e contatti.

## Linguette da staccare
Ogni linguetta ha 5 fori NPTH Ø0,5 mm (passo 0,85 mm, mouse bite) lungo il bordo della scheda. **A fine produzione spezzare a mano le 4 linguette** e limare l'eventuale sbavatura sul bordo. Niente V-cut.
Il rame della scheda è a 0,25–0,4 mm dal bordo (piano GND), quindi i fori sono a ≥ 0,25 mm dal rame.
