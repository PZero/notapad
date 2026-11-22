"""notªpad v0.1 - definizione unica di componenti, reti e piazzamento.

Usato da genera_kicad.py (schema + scheda) e da genera_jlc.py (BOM/CPL).
Coordinate scheda in mm dall'angolo in alto a sinistra (y verso il basso, anello in alto).
Rotazione in gradi, antioraria (convenzione KiCad).
"""

import os as _os
W = 16.5
H = float(_os.environ.get("NOTAPAD_H", "38.0"))   # lunghezza scheda: 38 mm (decisione utente 21/11; 35 e 36,5 non usati)
STRATI = 4                                         # 4 strati, 1,0 mm (Economic PCBA JLC)
SPESSORE = 1.0
STRETCH = H - 35.0


def s(y):
    """piazzamento definito per 35 mm; con la scheda più lunga la zona B si allarga (metà sotto i LED, tutto sopra il modulo)"""
    return y + STRETCH if y >= 15.0 else (y + STRETCH / 2 if y >= 9.5 else y)
CORNER_R = 1.0

USE_DUAL_NMOS = True       # Q2 = 2N7002DW (latch + reset) invece di due 2N7002

# --- famiglie di componenti: simbolo, impronta, LCSC, valore leggibile ---
P = {
    "E73":   ("E73-2G4M08S1C", "WIRELM-SMD_E73-2G4M08S1C", "C356849", "E73-2G4M08S1C nRF52840"),
    "NAND":  ("W25N02KVZEIR", "WSON-8_L8.0-W6.0-P1.27-TL-EP-1", "C3010298", "W25N02KVZEIR 2Gbit NAND"),
    # caricatore condiviso con SwimTimer (un solo Extended in caso di pannello unico); pinout come il TP4054
    # MCP73832 (22/11): STAT open-drain; l'MCP73831 ha STAT tri-state alimentato dal 5V e porterebbe P0.07 a ~5 V.
    # Stessa piedinatura: il simbolo di libreria resta quello del 31.
    "CHG":   ("MCP73831T-2ACI_OT", "SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BL", "C38066", "MCP73832T-2ACI/OT"),
    "LDO":   ("XC6206P332MR", "SOT-23-3_L2.9-W1.6-P1.90-LS2.8-BR", "C5446", "XC6206P332MR 3.3V"),
    "TTP":   ("TTP223-BA6-TD", "SOT-23-6_L2.9-W1.6-P0.95-LS2.9-BL", "C42422127", "TTP223-BA6-TD"),
    "LED":   ("MHPA1010RGBDT", "LED-ARRAY-SMD_4P-L1.0-W1.0-TR-RD", "C404280", "MHPA1010RGBDT RGB anodo comune"),
    "PMOS":  ("AO3401A", "SOT-23_L2.9-W1.3-P1.90-LS2.4-BR", "C15127", "AO3401A"),
    "NMOS":  ("2N7002", "SOT-23-3_L2.9-W1.3-P1.90-LS2.4-BR", "C8545", "2N7002"),
    "NMOS2": ("2N7002DW-7-F", "SOT-363_L2.0-W1.3-P0.65-LS2.1-TL", "C83571", "2N7002DW doppio"),
    "NMOSM": ("AO3400A", "SOT-23-3_L2.9-W1.3-P1.90-LS2.4-BR", "C20917", "AO3400A"),
    "DIODE": ("1N4148WST4", "SOD-323_L1.8-W1.3-LS2.5-RD", "C2128", "1N4148WS"),
    "MIC":   ("MSM261DGT003", "MIC-SMD_6P-L4.0-W2.0_LMD4020T261-OC3", "C48227730", "MSM261DGT003 PDM top-port"),
    "R20k":  ("0402WGF2002TCE", "R0402", "C25765", "20k"),
    "R1M":   ("0402WGF1004TCE", "R0402", "C26083", "1M"),
    "R100k": ("0402WGF1003TCE", "R0402", "C25741", "100k"),
    "R470":  ("0402WGF4700TCE", "R0402", "C25117", "470R"),
    "C1u":   ("CL05A105KA5NQNC", "C0402", "C52923", "1uF 10V X5R"),
    "C4u7":  ("CL05A475MP5NRNC", "C0402", "C23733", "4.7uF 10V X5R 0402"),
    "C100n": ("CL05B104KO5NNNC", "C0402", "C1525", "100nF 16V X7R"),
    "C10p":  ("CL05C100JB5NNNC", "C0402", "C32949", "10pF C0G"),
    # montati a mano (fuori BOM/CPL JLC)
    "PIN":   ("PAD1", "PIN_THT_1.6", "", "pin dorato"),
    "WPAD":  ("PAD1", "PAD_BOT_1.2x1.6", "", "piazzola filo (retro)"),
}

# ref: (famiglia, {pad: rete}, (x, y, rot))
C = {}
def add(ref, fam, nets, pos):
    x, y, r = pos
    C[ref] = (fam, nets, (x, y if ref == "U1" else s(y), r))

# ---------------- U1 modulo E73 (antenna verso il bordo basso) ----------------
e73 = {
    "5": "GND", "21": "GND", "24": "GND",
    "19": "3V3", "23": "3V3",
    "26": "NRESET", "37": "SWDIO", "39": "SWCLK",
    "11": "QSPI_IO0", "13": "QSPI_SCK", "15": "QSPI_IO3", "18": "QSPI_IO1", "17": "QSPI_IO2", "20": "QSPI_CS",
    "12": "PDM_CLK", "14": "PDM_DATA",
    "16": "TOUCH_A", "9": "TOUCH_B",
    "10": "MOTOR_G", "8": "HOLD", "7": "VBAT_SENSE", "4": "VBUS_SENSE", "22": "STAT",
    "28": "D1_R", "30": "D1_G", "32": "D1_B",
    "33": "D2_R", "34": "D2_G", "35": "D2_B",
    "36": "D3_R", "38": "D3_G", "40": "D3_B",
}
add("U1", "E73", e73, (8.25, H - 10.98, 0))

# ---------------- memoria ----------------
add("U2", "NAND", {"1": "QSPI_CS", "2": "QSPI_IO1", "3": "QSPI_IO2", "4": "GND", "5": "QSPI_IO0",
                   "6": "QSPI_SCK", "7": "QSPI_IO3", "8": "3V3", "9": "GND"}, (8.25, 12.75, 0))
add("C7", "C100n", {"1": "3V3", "2": "GND"}, (13.05, 9.95, 90))

# ---------------- ricarica + latch + reset (zona A) ----------------
add("U3", "CHG", {"1": "STAT", "2": "GND", "3": "VBAT", "4": "VBUS", "5": "PROG"}, (2.2, 5.35, 90))
add("C1", "C1u", {"1": "VBUS", "2": "GND"}, (3.2, 2.5, 90))
add("C2", "C1u", {"1": "VBAT", "2": "GND"}, (4.35, 4.5, 90))
add("R1", "R20k", {"1": "PROG", "2": "GND"}, (1, 7.55, 270))
add("Q1", "PMOS", {"1": "LATCH_G", "2": "VBAT", "3": "VSYS"}, (6.8, 4.94, 180))
add("R2", "R1M", {"1": "VBAT", "2": "LATCH_G"}, (4.35, 6.3, 90))
add("D5", "DIODE", {"2": "VBUS", "1": "VBUS_D"}, (3.2, 0.8, 180))
add("R3", "R100k", {"1": "VBUS_D", "2": "LATCH_ON"}, (5.9, 1.4, 90))
add("D6", "DIODE", {"2": "HOLD", "1": "LATCH_ON"}, (11.95, 5.5, 90))
add("R4", "R1M", {"1": "LATCH_ON", "2": "GND"}, (9, 6.75, 0))
add("C14", "C1u", {"1": "LATCH_ON", "2": "GND"}, (10.55, 6.75, 0))
if USE_DUAL_NMOS:
    add("Q2", "NMOS2", {"1": "GND", "2": "LATCH_ON", "6": "LATCH_G",
                        "4": "GND", "5": "RST_G", "3": "NRESET"}, (9.87, 4.6, 180))
else:
    add("Q2", "NMOS", {"1": "LATCH_ON", "2": "GND", "3": "LATCH_G"}, (9.87, 4.6, 180))
    add("Q3", "NMOS", {"1": "RST_G", "2": "GND", "3": "NRESET"}, (12.6, 6, 0))
add("C10", "C100n", {"1": "VBUS", "2": "RST_G"}, (10.6, 1.4, 90))
add("R5", "R100k", {"1": "RST_G", "2": "GND"}, (6.6, 2.95, 180))
add("R6", "R100k", {"1": "VBUS", "2": "VBUS_SENSE"}, (5.9, 6.75, 0))
add("R7", "R100k", {"1": "VBUS_SENSE", "2": "GND"}, (7.45, 6.75, 0))

# ---------------- motore (zona A destra) ----------------
add("Q4", "NMOSM", {"1": "MOTOR_G", "2": "GND", "3": "MOTOR_N"}, (14.45, 5.5, 0))
add("R10", "R100k", {"1": "MOTOR_G", "2": "GND"}, (15.25, 7.6, 0))
add("D4", "DIODE", {"1": "VSYS", "2": "MOTOR_N"}, (14.45, 8.6, 0))

# ---------------- microfoni ----------------
add("MK2", "MIC", {"1": "3V3", "2": "GND", "3": "PDM_DATA", "4": "PDM_CLK", "5": "GND", "6": "3V3"}, (8.25, 1.35, 90))
add("C9", "C100n", {"1": "3V3", "2": "GND"}, (8.6, 2.95, 180))
add("MK1", "MIC", {"1": "3V3", "2": "GND", "3": "PDM_DATA", "4": "PDM_CLK", "5": "GND", "6": "GND"}, (14.6, 14.88, 0))
add("C8", "C100n", {"1": "3V3", "2": "GND"}, (13.1, 14.5, 90))

# ---------------- LED sotto la fessura (zona B alta) ----------------
for i, x in enumerate((5.25, 8.25, 11.25), start=1):
    add(f"D{i}", "LED", {"1": f"LED{i}_A", "2": f"D{i}_R", "3": f"D{i}_G", "4": f"D{i}_B"}, (x, 8.5, 0))
    add(f"R{10+i}", "R470", {"1": "VSYS", "2": f"LED{i}_A"}, (x + 1.15, 8.5, 90))

# ---------------- tocco ----------------
add("U5", "TTP", {"1": "TOUCH_A", "2": "GND", "3": "TOUCH_A_PAD", "4": "GND", "5": "3V3", "6": "GND"}, (1.95, 10.4, 0))
add("C12", "C10p", {"1": "TOUCH_A_PAD", "2": "GND"}, (2.4, 7.9, 0))
add("U6", "TTP", {"1": "TOUCH_B", "2": "GND", "3": "TOUCH_B_PAD", "4": "GND", "5": "3V3", "6": "GND"}, (14.76, 11.1, 0))
add("C13", "C10p", {"1": "TOUCH_B_PAD", "2": "GND"}, (13.6, 7.6, 0))

# ---------------- regolatore + misura batteria (zona B sinistra) ----------------
add("U4", "LDO", {"1": "GND", "2": "3V3", "3": "VSYS"}, (1.9, 14, 90))
add("C3", "C1u", {"1": "VSYS", "2": "GND"}, (3.95, 8.4, 0))
add("C4", "C1u", {"1": "3V3", "2": "GND"}, (1.05, 17.95, 90))
add("C5", "C4u7", {"1": "3V3", "2": "GND"}, (1.9, 16.45, 180))
add("R8", "R1M", {"1": "VSYS", "2": "VBAT_SENSE"}, (10.17, 2.95, 0))
add("R9", "R1M", {"1": "VBAT_SENSE", "2": "GND"}, (13.3, 2.5, 90))
add("C11", "C100n", {"1": "VBAT_SENSE", "2": "GND"}, (15.45, 17.95, 90))

# ---------------- montati a mano ----------------
add("J1", "PIN", {"1": "VBUS"}, (1.8, 2.5, 0))
add("J2", "PIN", {"1": "GND"}, (4.6, 2.5, 0))
add("J3", "PIN", {"1": "SWDIO"}, (11.9, 2.5, 0))
add("J4", "PIN", {"1": "SWCLK"}, (14.7, 2.5, 0))
add("BT1P", "WPAD", {"1": "VBAT"}, (5, 12, 0))      # BT+  (retro, inizio batteria)
add("BT1N", "WPAD", {"1": "GND"}, (11.5, 12, 0))      # BT-
add("M1P", "WPAD", {"1": "VSYS"}, (2.2, 7, 0))        # M+  (retro, accanto al motorino)
add("M1N", "WPAD", {"1": "MOTOR_N"}, (14.3, 7, 0))    # M-
add("TPA", "WPAD", {"1": "TOUCH_A_PAD"}, (1, 10.5, 0))   # filo verso listello sinistro
add("TPB", "WPAD", {"1": "TOUCH_B_PAD"}, (15.5, 10.5, 0))  # filo verso listello destro

HAND = {"PIN", "WPAD"}

# Collegamenti GND brevi tracciati prima dello sbroglio (pad -> pad, lato superiore, 0,2 mm):
# punti dove il piano non arriva e Freerouting non trova spazio.
PREROUTE = [
    ("GND", ("C4", "2"), ("C5", "2")),
    ("GND", ("C9", "2"), ("MK2", "5")),
    ("GND", ("R5", "2"), ("J2", "1")),
    ("GND", ("Q2", "1"), ("C14", "2")),
    ("GND", ("MK1", "2"), ("MK1", "5")),
    ("GND", ("R1", "2"), ("U5", "6")),
    ("GND", ("U1", "21"), ("U1", "24"), [(6.35, 18.33), (4.44, 18.33)]),   # a L tra i pad 22 e 23 del modulo
    # pad -> via in un punto (x, y): due via accanto al pad termico della NAND (sotto il corpo, non nel pad)
    ("GND", ("U2", "9"), (8.25, 10.35)),
    ("GND", ("U2", "9"), (8.25, 15.15)),
]

# Pad GND che ricevono una via propria accanto, cercata in automatico dal generatore prima dello sbroglio
# Fanout: ogni pad GND superiore riceve una via propria (esclusi i pin del modulo e il pad termico della NAND)
PREVIA_TUTTI_GND = True    # fanout: ogni pad GND superiore ha la sua via; a 4 strati arriva sul piano In1 continuo
PREVIA = [("C2", "2"), ("C3", "2"), ("C7", "2"), ("C13", "2"), ("R4", "2"), ("Q2", "4"), ("BT1N", "1"), ("U5", "2"), ("U6", "2")]


def nets():
    """rete -> lista di (ref, pad)"""
    out = {}
    for ref, (fam, pads, _) in C.items():
        for pad, net in pads.items():
            out.setdefault(net, []).append((ref, pad))
    return out


if __name__ == "__main__":
    n = nets()
    for k in sorted(n):
        flag = "  <-- UN SOLO PIN" if len(n[k]) < 2 else ""
        print(f"{k:12s} {len(n[k]):2d} {n[k]}{flag}")
    print(len(C), "componenti,", len(n), "reti")
