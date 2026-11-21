# Acquisti v0 – montaggio in casa (stato: 21/11/2026)

Tutti i prezzi sono STIME da snapshot web non datati o discordanti (le pagine LCSC non si lasciano leggere in automatico). Prima di pagare: carica `ordine_v0_3monoliti.csv` nello strumento BOM di LCSC, che mostra stock e prezzo reali. Colonne `Stato_dato` = quanto e' affidabile ogni riga.

## Incongruenze progetto/datasheet
Nessuna trovata sui pezzi controllati (vedi sotto). Punti da guardare:
- Verificati su fonti secondarie (non sul PDF, illeggibile da qui): MCP73831 SOT-23-5 (1 STAT, 2 VSS, 3 VBAT, 4 VDD, 5 PROG), XC6206P332MR Torex (1 VSS, 2 VOUT, 3 VIN), TTP223-BA6 (1 Q, 2 VSS, 3 I, 4 AHLB, 5 VDD, 6 TOG), 2N7002DW (1 S1, 2 G1, 3 D2, 4 S2, 5 G2, 6 D1), LED MHPA1010RGBDT (1 anodo, 2 R, 3 G, 4 B), MSM261DGT003 (1 VDD, 2 GND, 3 DATA, 4 CLK, 6 L/R; pin 5 GND come da `docs/DOMANDE-APERTE.md`).
- NON verificati: pinout WSON-8 della W25N02KV (1 CS, 2 DO, 3 WP/IO2, 4 GND, 5 DI, 6 CLK, 7 HOLD/IO3, 8 VCC e' il pinout standard, coerente col progetto) e il land pattern del microfono (pad da 0,57x0,64 mm a passo 0,94: confrontarlo con il disegno del datasheet MSM261DGT003).
- Il pezzo sul LED: la tacca di pin 1 va controllata col tester prima del reflow.
- Il TTP223-BA6-TD e' un clone TDSEMIC, non il Tontek originale.
- Spunto: IO2/IO3 della NAND (pin 3 e 7) non hanno pull-up; verificare se servono nel firmware (per questo nel kit c'e' il 10 k).
- Spunto: con 20 k la carica e' 50 mA (~0,8C su ~60 mAh): il kit contiene 33 k (30 mA).

## Cosa comprare dove
Tutto su LCSC in UN solo ordine (le uniche eccezioni sono batteria, motorino, pin: `altri_distributori.csv`). Mouser/DigiKey costano molto di piu' sui pezzi critici e non hanno l'E73.

| Ordine | Merce (stima) | Spedizione | IVA 22% | Totale stimato |
|---|---|---|---|---|
| 3 monoliti + scorte + kit (`ordine_v0_3monoliti.csv`) | ~98 USD (~86 EUR) | ~15-25 USD | su merce+spedizione | ~125-135 EUR |
| 10 monoliti (`stima_10monoliti.csv`) | ~261 USD (~230 EUR) | ~15-25 USD | idem | ~300-320 EUR |

Ipotesi: 1 USD = 0,88 EUR; spedizione LCSC verso l'Italia NON verificata (soglie gratuite e IVA non trovate: controllare nel carrello); IVA italiana 22% da pagare comunque; dal 1 luglio 2026 l'UE applica 3 EUR di dazio temporaneo per linea doganale sui pacchi sotto 150 EUR (fonte: JLCPCB, non e' chiaro se LCSC lo incassa al checkout: potrebbero servire altri 10-20 EUR). Tre pezzi costano oltre il 70% del totale: E73 (~28 USD per 4), NAND (~40 USD per 4), mentre i passivi tutti insieme meno di 12 USD.
Altri fornitori (soglie di spedizione gratuita): Mouser Italia ~75 EUR (non confermato, altre pagine dicono 50), DigiKey.it 50 EUR (sotto: 18 EUR di spedizione), TME non trovato. Non servono se basta LCSC.

## Perche' questi quantitativi
- E73 e NAND: 3 + 1 di scorta (i pezzi piu' cari e quelli che si rovinano riscaldando male). Con 10 monoliti: 12 a testa.
- Microfoni 10 per 6 usati, LED 30 per 9 (1x1 mm, si perdono con le pinzette), TTP223 12 per 6.
- Passivi 0402: minimo 100 pezzi (MOQ LCSC tipico), costano 0,2-1 USD la bustina.
- Kit valori vicini (20 righe, ~7 USD in totale): LED (100/220/330/1k al posto di 470), corrente di carica (15k-47k al posto di 20k), partitori e latch (470k/2,2M, 220k), C14 del latch (470 nF / 2,2 uF), impulso di reset C10 (47/220 nF), sensibilita' tocco C12/C13 (4,7/22/47 pF). Servono a correggere al banco senza un secondo ordine. Le righe senza codice C hanno solo l'MPN: cercalo su LCSC prima di ordinare (il codice C inventato e' il rischio da evitare).
- Il 10 k (C25744) risultava esaurito: l'alternativa e' qualunque 10 k 0402 1% UNI-ROYAL a stock.

## Alternative con la stessa impronta (da verificare sul datasheet prima di usarle)
- E73: nessuna. NAND: W25N01KVZEIR/W25N01GVZEIG (1 Gbit, 128 MB, stessa famiglia WSON-8 8x6) o GD5F2GQ5UEYIGR: firmware diverso (ECC, stato). Microfono: nessuno verificato. MCP73831: MCP73832 C38066 (STAT open-drain) o TP4054. LDO: solo dopo aver controllato la piedinatura. MOSFET/diodi: tanti cloni, stessa piedinatura da controllare.

## Strumenti per stencil e piastra (prezzi indicativi, non verificati)
- Piastra riscaldante: mini MHP30 (~60 EUR) oppure piastra 946 (~30-50 EUR). Termometro a sonda o termocoppia (~10 EUR).
- Pasta: Sn42Bi58 a bassa temperatura (fonde a 138 C; profilo: preriscaldo 90-120 C per ~90 s, picco 165-180 C per 30-60 s), siringa 10-35 g, ~15-25 EUR, conservata in frigo. Alternativa SAC305 (picco 235-245 C, giunti piu' robusti, piastra piu' potente). Con Sn-Bi i giunti sono piu' fragili: va bene per prototipi.
- Flussante gel no-clean (~10 EUR), treccia dissaldante, alcool isopropilico, nastro kapton.
- Pinzette antistatiche punta fine (~8 EUR), lente 10x o microscopio USB (~20-40 EUR), saldatore a punta fine (~35 EUR), multimetro.
- Stencil e un supporto: tieni la scheda fissa con nastro e due schede avanzate come spessori.
- Non fare il reflow con la batteria sulla scheda: la LiPo si monta dopo.

## Batteria e motorino
Fuori dall'ordine LCSC: LiPo 501520 o 501525 (5x15 mm, 3,7 V, PCM, fili) e motorino a moneta 0820. Vedi `altri_distributori.csv`.
