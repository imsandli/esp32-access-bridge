"""AccessBridge C6 (HW-1.1 / Rev B; Rev A = HW-1.0 without J6/USB-C power): single source of truth used to bootstrap
the KiCad schematic and PCB.

After bootstrap the KiCad files in hardware/kicad/ are the editable sources;
this file documents the original intent and is used by the generators only.

Coordinates:
  sch: schematic position in mm (A3 sheet), rotation in degrees.
  PCB_POS: PCB position in mm (board origin top-left, y down), rotation.
"""

PROJECT = "accessbridge"
TITLE = "AccessBridge C6"
HW_VERSION = "HW-1.1"
PCB_REV = "B"
DATE = "2026-10-18"

# --- part catalogue -------------------------------------------------------
# key -> (lib_id, value, footprint, manufacturer, mpn, lcsc, lcsc_status)
# lcsc_status: "confirmed" = C-number seen on an LCSC/JLCPCB part page during
# research, "secondary" = C-number from a third-party list, "unverified" = no
# C-number confirmed -> buyer must select; "manual" = not assembled by JLCPCB.
P = {
    "R1k": ("Device:R", "1k", "Resistor_SMD:R_0603_1608Metric", "UNI-ROYAL", "0603WAF1001T5E", "C21190", "confirmed"),
    "R10k": ("Device:R", "10k", "Resistor_SMD:R_0603_1608Metric", "UNI-ROYAL", "0603WAF1002T5E", "C25804", "confirmed"),
    "R4k7": ("Device:R", "4.7k", "Resistor_SMD:R_0603_1608Metric", "UNI-ROYAL", "0603WAF4701T5E", "C23162", "confirmed"),
    "R2k2": ("Device:R", "2.2k", "Resistor_SMD:R_0603_1608Metric", "UNI-ROYAL", "0603WAF2201T5E", "C4190", "secondary"),
    "R100": ("Device:R", "100", "Resistor_SMD:R_0603_1608Metric", "UNI-ROYAL", "0603WAF1000T5E", "C22775", "secondary"),
    "R470": ("Device:R", "470", "Resistor_SMD:R_0603_1608Metric", "generic", "0603 470R 1% thick film", "", "unverified"),
    "C100n": ("Device:C", "100n", "Capacitor_SMD:C_0603_1608Metric", "YAGEO", "CC0603KRX7R9BB104", "C14663", "confirmed"),
    "C10n": ("Device:C", "10n", "Capacitor_SMD:C_0603_1608Metric", "FH", "0603B103K500NT", "C57112", "confirmed"),
    "C10u50": ("Device:C", "10u/50V", "Capacitor_SMD:C_1206_3216Metric", "Samsung", "CL31A106KBHNNNE", "C13585", "secondary"),
    "C10u25": ("Device:C", "10u/25V", "Capacitor_SMD:C_0805_2012Metric", "Samsung", "CL21A106KAYNNNE", "C15850", "secondary"),
    "C22u25": ("Device:C", "22u/25V", "Capacitor_SMD:C_0805_2012Metric", "Samsung", "CL21A226MAQNNNE", "C45783", "secondary"),
    "L4u7": ("Device:L", "4.7u", "Inductor_SMD:L_Changjiang_FNR4030S", "Sunlord", "SWPA4030S4R7MT", "C57269", "confirmed"),
    "F200": ("Device:Polyfuse", "200mA/30V", "Fuse:Fuse_1206_3216Metric", "BHFUSE", "BSMD1206-020-30V", "C883118", "confirmed"),
    "TVS15": ("Diode:SMAJ15A", "SMAJ15A", "Diode_SMD:D_SMA", "Littelfuse", "SMAJ15A", "C148216", "confirmed"),
    "TVS15C": ("Diode:SMAJ15CA", "SMAJ15CA", "Diode_SMD:D_SMA", "MDD", "SMAJ15CA", "C110044", "confirmed"),
    "SS14": ("Device:D_Schottky", "SS14", "Diode_SMD:D_SMA", "MDD", "SS14", "C2480", "confirmed"),
    "1N4148W": ("Diode:1N4148W", "1N4148W", "Diode_SMD:D_SOD-123", "ST(Semtech)", "1N4148W", "C81598", "confirmed"),
    "LEDG": ("Device:LED", "green", "LED_SMD:LED_0603_1608Metric", "Hubei KENTO", "KT-0603G (emerald)", "C72043", "secondary"),
    "LEDR": ("Device:LED", "red", "LED_SMD:LED_0603_1608Metric", "Hubei KENTO", "KT-0603R", "C2286", "secondary"),
    "BUCK": ("Regulator_Switching:AP63205WU", "AP63205WU-7", "Package_TO_SOT_SMD:TSOT-23-6", "Diodes Inc.", "AP63205WU-7", "C2071056", "confirmed"),
    "OPTO": ("Isolator:LTV-357T", "EL357N(C)(TA)-G", "Package_SO:SO-4_4.4x3.6mm_P2.54mm", "Everlight", "EL357N(C)(TA)-G", "C29981", "confirmed"),
    "SSR": ("Relay_SolidState:CPC1014N", "CPC1014NTR", "Package_SO:SOP-4_3.8x4.1mm_P2.54mm", "Littelfuse/IXYS", "CPC1014NTR", "C2760365", "confirmed"),
    "NMOS": ("Transistor_FET:AO3400A", "AO3400A", "Package_TO_SOT_SMD:SOT-23", "AOS", "AO3400A", "C20917", "confirmed"),
    "TACT": ("Switch:SW_Push", "PAIR", "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", "XKB", "TS-1187A-B-A-B", "C318884", "confirmed"),
    "TB4": ("Connector:Screw_Terminal_01x04", "Screw_Terminal_01x04", "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-4-5.08_1x04_P5.08mm_Horizontal", "Phoenix Contact", "MKDS 1,5/ 4-5,08 (1715747) or 5.08 mm equivalent", "", "manual"),
    "TB2": ("Connector:Screw_Terminal_01x02", "Screw_Terminal_01x02", "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal", "Phoenix Contact", "MKDS 1,5/ 2-5,08 (1715721) or 5.08 mm equivalent", "", "manual"),
    "QWIIC": ("Connector_Generic_MountingPin:Conn_01x04_MountingPin", "Qwiic", "Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal", "JST", "SM04B-SRSS-TB(LF)(SN)", "C160404", "confirmed"),
    "HDR4": ("Connector_Generic:Conn_01x04", "EXP", "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "generic", "2.54 mm 1x4 pin header", "", "manual"),
    "XIAO": ("AccessBridge:XIAO_ESP32C6", "XIAO_ESP32C6", "AccessBridge:XIAO_ESP32C6_Socketed", "Seeed Studio", "113991254 (module) + 2x female header 1x7 2.54 mm", "", "manual"),
    "SJ3": ("Jumper:SolderJumper_3_Bridged12", "SolderJumper_3_Bridged12", "Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm_NumberLabels", "-", "PCB solder jumper", "", "pcb"),
    "USBC": ("Connector:USB_C_Receptacle_PowerOnly_6P", "USB-C 5V", "Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal", "GCT", "USB4125-GF-A", "C3151650", "confirmed"),
    "R5k1": ("Device:R", "5.1k", "Resistor_SMD:R_0603_1608Metric", "UNI-ROYAL", "0603WAF5101T5E", "C23186", "confirmed"),
    "F500": ("Device:Polyfuse", "500mA/30V", "Fuse:Fuse_1206_3216Metric", "BHFUSE", "BSMD1206-050-30V", "C883126", "confirmed"),
    "TVS5": ("Diode:SMAJ5.0A", "SMAJ5.0A", "Diode_SMD:D_SMA", "Littelfuse", "SMAJ5.0A", "C83329", "confirmed"),
    "MH": ("Mechanical:MountingHole", "M3", "MountingHole:MountingHole_3.2mm_M3", "-", "M3 mounting hole", "", "pcb"),
}

# --- components -----------------------------------------------------------
# ref: (part key, {pin: net}, sch(x, y, rot), extra); PCB placement is in PCB_POS
G = "GND"


def comp(part, pins, sch, value=None, dnp=False, note=""):
    return dict(part=part, pins=pins, sch=sch, value=value, dnp=dnp, note=note)


C = {}

# Connectors ---------------------------------------------------------------
C["J1"] = comp("TB4", {"1": "+12V_IN", "2": G, "3": "IN1_COM", "4": "IN1_NO"},
               (30.48, 45.72, 0), value="PWR+RELAY",
               note="1 +12V | 2 GND | 3 RELAY COM | 4 RELAY NO")
C["J2"] = comp("TB4", {"1": "IN2_COM", "2": "IN2_NO", "3": "DPS_A", "4": "DPS_B"},
               (30.48, 81.28, 0), value="BELL+DPS",
               note="1 BELL COM | 2 BELL NO | 3 DPS A | 4 DPS B")
C["J4"] = comp("TB2", {"1": "+12V", "2": "OUT_SW"},
               (30.48, 111.76, 0), value="OUT",
               note="1 OUT +12V | 2 OUT SW (low side)")
C["J3"] = comp("QWIIC", {"1": G, "2": "+3V3", "3": "SDA", "4": "SCL", "MP": G},
               (30.48, 139.7, 0))
C["J5"] = comp("HDR4", {"1": "+3V3", "2": "EXP_GPIO20", "3": "EXP_GPIO18", "4": G},
               (30.48, 167.64, 0), dnp=True)

# Power --------------------------------------------------------------------
C["F1"] = comp("F200", {"1": "+12V_IN", "2": "+12V_F"}, (91.44, 50.8, 0))
C["D1"] = comp("TVS15", {"1": "+12V_F", "2": G}, (106.68, 58.42, 90))
C["D2"] = comp("SS14", {"2": "+12V_F", "1": "+12V"}, (124.46, 45.72, 0))
C["C1"] = comp("C10u50", {"1": "+12V", "2": G}, (142.24, 55.88, 0))
C["C2"] = comp("C100n", {"1": "+12V", "2": G}, (152.4, 55.88, 0))
C["U1"] = comp("BUCK", {"3": "+12V", "2": "+12V", "4": G, "5": "SW", "6": "BST", "1": "+5V"},
               (175.26, 55.88, 0))
C["C3"] = comp("C100n", {"1": "BST", "2": "SW"}, (205.74, 50.8, 0))
C["L1"] = comp("L4u7", {"1": "SW", "2": "+5V"}, (220.98, 50.8, 0))
C["C4"] = comp("C22u25", {"1": "+5V", "2": G}, (236.22, 55.88, 0))
C["C5"] = comp("C22u25", {"1": "+5V", "2": G}, (246.38, 55.88, 0))
C["D3"] = comp("SS14", {"2": "+5V", "1": "+5V_XIAO"}, (264.16, 45.72, 0),
               note="Seeed: external 5 V into XIAO 5V pin through a diode (anode = supply)")
C["C6"] = comp("C10u25", {"1": "+5V_XIAO", "2": G}, (281.94, 55.88, 0))
C["R1"] = comp("R1k", {"1": "+5V", "2": "LED_PWR"}, (297.18, 50.8, 0))
C["D4"] = comp("LEDG", {"2": "LED_PWR", "1": G}, (297.18, 66.04, 90))

# MCU ----------------------------------------------------------------------
C["U2"] = comp("XIAO", {"1": "IN1_SIG", "2": "IN2_SIG", "3": "IN3_SIG", "4": "DPS_DRV",
                        "5": "SDA", "6": "SCL", "7": "LED_STAT_DRV",
                        "8": "BTN_PAIR", "9": "OUT_DRV", "10": "EXP_GPIO20", "11": "EXP_GPIO18",
                        "12": "+3V3", "13": G, "14": "+5V_XIAO"},
               (353.06, 101.6, 0))
C["C7"] = comp("C100n", {"1": "+3V3", "2": G}, (391.16, 147.32, 0))
C["R2"] = comp("R1k", {"1": "LED_STAT_DRV", "2": "LED_STAT"}, (330.2, 147.32, 0))
C["D5"] = comp("LEDR", {"2": "LED_STAT", "1": G}, (330.2, 165.1, 90))
C["SW1"] = comp("TACT", {"1": "BTN_PAIR", "2": G}, (355.6, 165.1, 0))
C["R3"] = comp("R10k", {"1": "+3V3", "2": "BTN_PAIR"}, (345.44, 147.32, 0))
C["R4"] = comp("R4k7", {"1": "+3V3", "2": "SDA"}, (370.84, 147.32, 0))
C["R5"] = comp("R4k7", {"1": "+3V3", "2": "SCL"}, (381.0, 147.32, 0))

# Contact inputs (3x identical optocoupler channels) ------------------------
IN_SCH_Y = {1: 203.2, 2: 231.14, 3: 259.08}
IN_REFS = {1: (3, 6, 9, 8, 10), 2: (4, 7, 10, 9, 14), 3: (5, 8, 11, 10, 18)}
for n in (1, 2, 3):
    u, dr, dt, cf, r0 = IN_REFS[n]
    y = IN_SCH_Y[n]
    k = f"IN{n}_COM" if n < 3 else "IN3_K"
    C[f"R{r0}"] = comp("R2k2", {"1": "V_LOOP", "2": f"IN{n}_A"}, (91.44, y - 5.08, 0))
    C[f"U{u}"] = comp("OPTO", {"1": f"IN{n}_A", "2": k, "3": G, "4": f"IN{n}_C"},
                      (124.46, y, 0))
    C[f"D{dr}"] = comp("1N4148W", {"1": f"IN{n}_A", "2": k}, (106.68, y + 10.16, 90))
    C[f"D{dt}"] = comp("TVS15C", {"1": k, "2": G}, (68.58, y + 7.62, 90))
    C[f"R{r0 + 1}"] = comp("R1k", {"1": f"IN{n}_NO", "2": G}, (78.74, y + 12.7, 0))
    C[f"R{r0 + 2}"] = comp("R10k", {"1": "+3V3", "2": f"IN{n}_C"}, (149.86, y - 5.08, 0))
    C[f"C{cf}"] = comp("C10n", {"1": f"IN{n}_C", "2": G}, (160.02, y + 7.62, 0))
    C[f"R{r0 + 3}"] = comp("R1k", {"1": f"IN{n}_C", "2": f"IN{n}_SIG"}, (175.26, y + 2.54, 90))

# DPS port mode selection + solid-state relay ------------------------------
C["JP1"] = comp("SJ3", {"1": "IN3_K", "2": "DPS_A", "3": "SSR_A"}, (215.9, 205.74, 0),
                note="1-2 bridged = DPS input (default); cut 1-2 and bridge 2-3 = DPS output")
C["JP2"] = comp("SJ3", {"1": "IN3_NO", "2": "DPS_B", "3": "SSR_B"}, (215.9, 226.06, 0))
C["U6"] = comp("SSR", {"1": "SSR_LED", "2": G, "4": "SSR_A", "3": "SSR_B"}, (269.24, 210.82, 0))
C["R8"] = comp("R470", {"1": "DPS_DRV", "2": "SSR_LED"}, (243.84, 200.66, 90))
C["R9"] = comp("R10k", {"1": "DPS_DRV", "2": G}, (231.14, 228.6, 0))

# Open-drain output ---------------------------------------------------------
C["Q1"] = comp("NMOS", {"1": "OUT_G", "3": "OUT_SW", "2": G}, (365.76, 215.9, 0))
C["R6"] = comp("R100", {"1": "OUT_DRV", "2": "OUT_G"}, (340.36, 210.82, 90))
C["R7"] = comp("R10k", {"1": "OUT_G", "2": G}, (350.52, 228.6, 0))
C["D12"] = comp("SS14", {"2": "OUT_SW", "1": "+12V"}, (381.0, 200.66, 90))

# USB-C power input (Rev B) ---------------------------------------------------
# Power only: the XIAO does not route USB D+/D- to its pins, so firmware is
# flashed through the XIAO's own USB-C. VBUS feeds +5V_XIAO and the contact
# loops (V_LOOP) through diodes; J4 OUT+ stays on +12V only.
C["J6"] = comp("USBC", {"A9": "VBUS", "B9": "VBUS", "A5": "CC1", "B5": "CC2", "A12": G, "B12": G, "S1": G},
               (220.98, 259.08, 0), value="USB-C 5V", note="USB-C power input 5 V (sink, no data)")
C["R22"] = comp("R5k1", {"1": "CC1", "2": G}, (247.65, 271.78, 0))
C["R23"] = comp("R5k1", {"1": "CC2", "2": G}, (257.81, 271.78, 0))
C["F2"] = comp("F500", {"1": "VBUS", "2": "VBUS_F"}, (247.65, 255.27, 0))
C["D14"] = comp("TVS5", {"1": "VBUS_F", "2": G}, (257.81, 255.27, 90))
C["C11"] = comp("C10u25", {"1": "VBUS_F", "2": G}, (283.21, 260.35, 0))
C["D13"] = comp("SS14", {"2": "VBUS_F", "1": "+5V_XIAO"}, (270.51, 254.0, 0),
                note="USB 5 V into the XIAO 5V pin through a diode (Seeed), OR-ed with D3")
C["D16"] = comp("SS14", {"2": "VBUS_F", "1": "V_LOOP"}, (270.51, 266.7, 0))
C["D15"] = comp("SS14", {"2": "+12V", "1": "V_LOOP"}, (270.51, 279.4, 0))

# Mechanical ----------------------------------------------------------------
for i in range(1, 5):
    C[f"H{i}"] = comp("MH", {}, (393.7, 30.48 + 7.62 * i, 0))

# PWR_FLAGs (schematic only): net -> sch position
PWR_FLAGS = {
    "+12V_IN": (76.2, 40.64),
    "+12V": (137.16, 38.1),
    "+5V": (231.14, 38.1),
    "+5V_XIAO": (276.86, 38.1),
    "GND": (76.2, 63.5),
}

# Nets that use KiCad power symbols instead of local labels
POWER_SYMBOLS = {"GND": "power:GND", "+12V": "power:+12V", "+5V": "power:+5V", "+3V3": "power:+3V3"}

# Schematic frames: (title, x1, y1, x2, y2)
FRAMES = [
    ("CONNECTORS (field side)", 12.7, 25.4, 63.5, 182.88),
    ("POWER: 12 V input protection, 5 V buck, XIAO 5 V feed", 66.04, 25.4, 309.88, 81.28),
    ("MCU: XIAO ESP32C6 (socketed)", 312.42, 25.4, 406.4, 182.88),
    ("CONTACT INPUTS: opto loops powered from V_LOOP (+12 V or USB 5 V)", 12.7, 185.42, 200.66, 281.94),
    ("DPS PORT: input (default) or isolated SSR output", 203.2, 185.42, 309.88, 240.03),
    ("OPEN-DRAIN OUTPUT (<=12 V / 100 mA)", 312.42, 185.42, 406.4, 248.92),
    ("USB-C POWER INPUT 5 V (power only, Rev B)", 203.2, 241.3, 288.29, 285.75),
]

NOTES = [
    ((68.58, 88.9), "Power budget: UA-Hub LINE output 12 V / 0.33 A max. F1 holds 200 mA."),
    ((68.58, 93.98), "D2 = reverse-polarity protection; D1 + F1 clamp surges / reversed input."),
    ((68.58, 99.06), "D3: Seeed requires a diode (anode = supply) when feeding the XIAO 5V pin."),
    ((68.58, 104.14), "Field loops: V_LOOP -> 2.2k -> opto LED -> COM ... contact ... NO -> 1k -> GND (~3.3 mA at 12 V, ~1.1 mA on USB)."),
    ((68.58, 109.22), "Contact closed -> opto ON -> INx_SIG LOW (active low). RC 1k/10n + firmware debounce."),
    ((68.58, 114.3), "J2.3/J2.4 (DPS): JP1/JP2 1-2 = input (reed contact); 2-3 = SSR output to UA-Hub DPS input."),
    ((68.58, 119.38), "Never wire DPS input in parallel with a reed that already feeds the UA-Hub DPS input."),
    ((68.58, 124.46), "No mains voltage on this PCB. 230 V doorbells: use a certified coupling relay (electrician)."),
    ((68.58, 129.54), "J6 USB-C (Rev B): 5 V power only, no data. Firmware upload uses the XIAO's own USB-C."),
    ((68.58, 134.62), "VBUS -> F2 -> D13 -> +5V_XIAO (OR with D3) and D16 -> V_LOOP (OR with D15 from +12V). J4 OUT+ is 12 V only."),
]


# --- PCB placement (mm, rotation deg), front side only ----------------------
# Board placed on the A4 drawing sheet at this offset; aux origin = board corner
SHEET_ORIGIN = (40.0, 40.0)
BOARD_W = 96.0
BOARD_H = 56.0
PCB_POS = {
    # Rev B additions (right-hand strip, board widened from 86 to 96 mm)
    "J6": (83.0, 3.4, 180),
    "R22": (83.0, 9.6, 90),
    "R23": (86.5, 9.6, 90),
    "F2": (86.0, 15.0, 90),
    "D14": (91.0, 18.0, 90),
    "D13": (86.0, 22.0, 90),
    "D16": (91.0, 30.0, 90),
    "D15": (86.0, 34.0, 90),
    "C11": (91.0, 38.0, 90),
    "C1": (16.8, 8.0, 90),
    "C2": (19.3, 8.0, 90),
    "C3": (26.0, 9.0, 90),
    "C4": (33.0, 11.0, 90),
    "C5": (35.5, 11.0, 90),
    "C6": (79.0, 12.0, 90),
    "C7": (79.0, 16.5, 90),
    "C8": (19.5, 29.0, 90),
    "C9": (35.5, 29.0, 90),
    "C10": (51.5, 29.0, 90),
    "D1": (5.5, 14.0, 90),
    "D2": (11.5, 8.5, 180),
    "D3": (40.0, 14.0, 180),
    "D4": (40.0, 18.0, 180),
    "D5": (47.5, 18.0, 180),
    "D6": (10.0, 34.0, 0),
    "D7": (26.0, 34.0, 0),
    "D8": (42.0, 34.0, 0),
    "D9": (11.0, 38.5, 0),
    "D10": (27.0, 38.5, 0),
    "D11": (43.0, 38.5, 0),
    "D12": (77.0, 41.0, 90),
    "F1": (5.5, 21.0, 90),
    "H1": (4.0, 4.0, 0),
    "H2": (92.0, 4.0, 0),
    "H3": (4.0, 52.0, 0),
    "H4": (92.0, 52.0, 0),
    "J1": (11.0, 50.5, 0),
    "J2": (33.0, 50.5, 0),
    "J3": (43.0, 4.0, 180),
    "J4": (67.0, 50.5, 0),
    "J5": (56.5, 6.0, 0),
    "JP1": (46.5, 42.0, 0),
    "JP2": (51.5, 42.0, 0),
    "L1": (29.0, 13.5, 90),
    "Q1": (70.5, 41.0, 0),
    "R1": (36.5, 18.0, 0),
    "R2": (44.0, 18.0, 0),
    "R3": (80.5, 33.5, 0),
    "R4": (48.5, 4.0, 90),
    "R5": (50.5, 4.0, 90),
    "R6": (67.5, 37.0, 90),
    "R7": (70.5, 37.0, 90),
    "R8": (61.2, 37.0, 90),
    "R9": (61.2, 41.0, 90),
    "R10": (7.0, 26.0, 90),
    "R11": (17.0, 34.0, 0),
    "R12": (19.5, 25.0, 90),
    "R13": (19.5, 33.0, 90),
    "R14": (23.0, 26.0, 90),
    "R15": (33.0, 34.0, 0),
    "R16": (35.5, 25.0, 90),
    "R17": (35.5, 33.0, 90),
    "R18": (39.0, 26.0, 90),
    "R19": (49.0, 34.0, 0),
    "R20": (51.5, 25.0, 90),
    "R21": (51.5, 33.0, 90),
    "SW1": (80.5, 28.0, 90),
    "U1": (22.0, 12.0, 0),
    "U2": (68.0, 13.5, 90),
    "U3": (13.0, 29.0, 0),
    "U4": (29.0, 29.0, 0),
    "U5": (45.0, 29.0, 0),
    "U6": (56.0, 38.0, 0),
}

# Additional antenna keep-out below the XIAO antenna end (both copper layers)
ANTENNA_KEEPOUT = (58.8, 24.0, 77.2, 33.0)
# No copper pour (tracks allowed) over the module's antenna end, added after routing
ANTENNA_NO_POUR = (58.8, 19.0, 77.2, 24.0)

# Silkscreen texts: (text, x, y, size, rotation, layer)
SILK = [
    ("AccessBridge C6  HW-1.1  Rev B", 24.0, 2.2, 1.0, 0, "F.SilkS"),
    ("USB 5V", 90.5, 9.6, 0.8, 90, "F.SilkS"),
    ("+12V", 11.0, 44.0, 0.9, 0, "F.SilkS"),
    ("GND", 16.08, 44.0, 0.9, 0, "F.SilkS"),
    ("COM", 21.16, 44.0, 0.9, 0, "F.SilkS"),
    ("NO", 26.24, 44.0, 0.9, 0, "F.SilkS"),
    ("POWER", 13.54, 42.4, 0.9, 0, "F.SilkS"),
    ("RELAY", 23.7, 42.4, 0.9, 0, "F.SilkS"),
    ("COM", 33.0, 44.0, 0.9, 0, "F.SilkS"),
    ("NO", 38.08, 44.0, 0.9, 0, "F.SilkS"),
    ("DPS-A", 43.16, 44.2, 0.8, 0, "F.SilkS"),
    ("DPS-B", 48.24, 44.2, 0.8, 0, "F.SilkS"),
    ("BELL", 35.54, 42.4, 0.9, 0, "F.SilkS"),
    ("OUT+", 67.0, 44.2, 0.8, 0, "F.SilkS"),
    ("OUT-", 72.08, 44.2, 0.8, 0, "F.SilkS"),
    ("PAIR", 80.5, 22.9, 0.8, 0, "F.SilkS"),
    ("PWR", 40.0, 19.9, 0.8, 0, "F.SilkS"),
    ("STAT", 47.5, 19.9, 0.8, 0, "F.SilkS"),
    ("QWIIC 3V3", 43.0, 8.2, 0.8, 0, "F.SilkS"),
    ("NO COPPER - ANTENNA", 68.0, 28.5, 0.8, 0, "F.SilkS"),
    ("JP1/JP2: 1-2 = DPS IN, 2-3 = DPS OUT (SSR)", 43.0, 43.0, 1.0, 0, "B.SilkS"),
    ("AccessBridge C6 HW-1.1 Rev B - CERN-OHL-S-2.0", 43.0, 30.0, 1.2, 0, "B.SilkS"),
    ("J6 USB-C: 5V power only (no data)", 43.0, 45.5, 1.0, 0, "B.SilkS"),
    ("J1: 1 +12V  2 GND  3 RELAY COM  4 RELAY NO", 43.0, 33.0, 1.0, 0, "B.SilkS"),
    ("J2: 1 BELL COM  2 BELL NO  3 DPS A  4 DPS B", 43.0, 35.5, 1.0, 0, "B.SilkS"),
    ("J4: 1 OUT +12V  2 OUT SW (low side)", 43.0, 38.0, 1.0, 0, "B.SilkS"),
    ("Supply: UA-Hub LINE 12V or USB-C 5V - no mains", 43.0, 40.5, 1.0, 0, "B.SilkS"),
]
