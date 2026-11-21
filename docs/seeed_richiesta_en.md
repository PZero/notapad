# Richiesta a Seeed Fusion (bozza da inviare a fusion@seeed.io)

Bozza del 21/11/2026. Variante ipotizzata: scheda portante con **XIAO nRF52840 Plus**. Il progetto con questa variante non esiste ancora: le misure sono stime.

---

**Subject:** XIAO nRF52840 Plus carrier board – eligibility for the 30% XIAO PCBA offer and sponsorship

Hello Seeed Fusion team,

We are two hobbyists building **notªpad**, an open-hardware wearable voice recorder (public repository: https://github.com/PZero/notapad, project page: https://pzero.github.io/notapad/). It is a small resin-cast pendant that records all day and syncs over Bluetooth.

Our current v0.1 board uses a bare nRF52840 module. We are considering a version built around the **XIAO nRF52840 Plus** and would like to manufacture it with Seeed Fusion PCBA. Before we redesign the board, could you please confirm a few points?

**Planned board (estimate)**
- Carrier PCB about 18.5 × 34 mm, 4 layers, 1.0 mm (2 layers if routing allows), components on the top side only.
- XIAO nRF52840 Plus mounted flat (SMD, castellated edge pins **and** the back-side pads), antenna at the board edge with no copper below.
- Other parts on the carrier: 2 PDM MEMS microphones (MSM261DGT003), SPI NAND 2 Gbit WSON-8 (W25N02KVZEIR or equivalent), 3 RGB LEDs 1×1 mm (MHPA1010RGBDT), 2 TTP223 touch ICs, P-MOSFET power latch (AO3401A + 2N7002DW), vibration motor driver (AO3400A), about 15 0402 passives. LiPo cell and coin motor are hand-soldered by us.
- Quantity: 5 assembled boards for the first run, then 10–50.

**Questions**
1. Is the **XIAO nRF52840 Plus** eligible for the 30% XIAO PCBA discount, or only the standard XIAO nRF52840?
2. Can you reflow the XIAO Plus including its **back-side pads** (we need about 20 GPIOs)? Is a pre-soldered option available?
3. Which of the parts listed above are in your **OPL**? For the others, can you source them (they are all available at LCSC)?
4. Is there a minimum quantity for the XIAO offer, and can it be combined with a sponsorship coupon for an open-source project?
5. Would our project qualify for the **Fusion sponsorship program**? We document everything publicly (schematics, board files, firmware) and would credit Seeed Fusion on the project page.

Thank you very much,
the notªpad team
