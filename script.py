import os
import subprocess 
import sys
CELL_DESCRIPTIONS = {
    "inv": "Inverter",
    "buffer": "Buffer",
    "nand2": "2-Input NAND Gate",
    "nand3": "3-Input NAND Gate",
    "nand4": "4-Input NAND Gate",
    "nor2": "2-Input NOR Gate",
    "nor3": "3-Input NOR Gate",
    "and2": "2-Input AND Gate",
    "or2": "2-Input OR Gate",
    "xor2": "2-Input XOR Gate",
    "mux2": "2-to-1 Multiplexer",
    "fulladder": "Full Adder",
    "halfadder": "Half Adder",
    "rdtype": "D-Type Flip-Flop with Reset",
    "scandtype": "Scan D-Type Flip-Flop",
    "scanreg": "Scan Register",
    "smux": "Scan Multiplexer",
    "smux2": "Scan Multiplexer Type 2",
    "smux3": "Scan Multiplexer Type 3",
    "trisbuf": "Tri-State Buffer",
    "tiehigh": "Tie High Cell",
    "tielow": "Tie Low Cell",
    "leftbuf": "Left Buffer",
    "rightend": "Right End Cap",
    "rowcrosser": "Row Crosser",
}
MAIN_DATABOOK_CELLS = [
    "scandtype",
    "scanreg", 
    "fulladder",
    "halfadder",
    "mux2",
    "nand",
    "xor",
    "inv",
    "buffer",
    "trisbuf"
]
def log_message(message, is_error=False):
    """Log message to logs.txt"""
    with open("logs.txt", "a") as f:
        f.write(message + "\n")
PORT_DIRECTIONS = {
    "rdtype": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Test"),
        "Input": ("D", "Clock", "nReset"),
        "Output": ("Q", "nQ"),
    },
    "inv": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A",),
        "Output": ("Y",),
    },
    "buffer": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A",),
        "Output": ("Y",),
    },
    "nand": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B", "C", "D"),
        "Output": ("Y",),
    },
    "nor": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B", "C", "D"),
        "Output": ("Y",),
    },
    "and": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B", "C", "D"),
        "Output": ("Y",),
    },
    "or": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B", "C", "D"),
        "Output": ("Y",),
    },
    "xor": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B"),
        "Output": ("Y",),
    },
    "mux": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("I0", "I1", "S"),
        "Output": ("Y",),
    },
    "mux2": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("I0", "I1", "S"),
        "Output": ("Y",),
    },
    "smux": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Clock", "nReset"),
        "Input": ("D", "Load", "Test", "SDI"),
        "Output": ("M", "Q"),
    },
    "smux2": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Clock", "nReset"),
        "Input": ("D", "Test", "SDI"),
        "Output": ("M",),
    },
    "fulladder": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B", "Cin"),
        "Output": ("S", "Cout"),
    },
    "halfadder": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "B"),
        "Output": ("S", "C"),
    },
    "scandtype": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn",),
        "Input": ("D", "SDI", "Clock", "nReset", "Test"),
        "Output": ("Q", "nQ"),
    },
    "scanreg": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn",),
        "Input": ("D", "SDI", "Clock", "nReset", "Load", "Test"),
        "Output": ("Q", "nQ"),
    },
    "trisbuf": {
        "Power": ("Vdd!", "GND!"),
        "Not connected": ("ScanReturn", "Scan", "Test", "Clock", "nReset"),
        "Input": ("A", "Enable"),
        "Output": ("Y",),
    },
}
CELL_TEST_CONFIG = {
    "scandtype": {
        "is_sequential": True,
        "sim_time": "2ns",
        "clock_signal": "Clock",
        "control_configs": {
            "D": {"SDI": "0", "Test": "0", "Clock": "PULSE", "nReset": "vd"},
            "SDI": {"D": "0", "Test": "vd", "Clock": "PULSE", "nReset": "vd"},
            "Clock": {"D": "PULSE", "SDI": "0", "Test": "0", "nReset": "vd"},
            "Test": {"D": "vd", "SDI": "0", "Clock": "PULSE", "nReset": "vd"},
            "nReset": {"D": "0", "SDI": "0", "Test": "0", "Clock": "PULSE"},
        }
    },
    "scanreg": {
        "is_sequential": True,
        "sim_time": "2ns",
        "clock_signal": "Clock",
        "control_configs": {
            "D": {"SDI": "0", "Load": "vd", "Test": "0", "Clock": "PULSE", "nReset": "vd"},
            "SDI": {"D": "0", "Load": "0", "Test": "vd", "Clock": "PULSE", "nReset": "vd"},
            "Load": {"D": "vd", "SDI": "0", "Test": "0", "Clock": "PULSE", "nReset": "vd"},
            "Test": {"D": "vd", "SDI": "0", "Load": "vd", "Clock": "PULSE", "nReset": "vd"},
            "Clock": {"D": "PULSE", "SDI": "0", "Load": "vd", "Test": "0", "nReset": "vd"},
            "nReset": {"D": "0", "SDI": "0", "Load": "vd", "Test": "0", "Clock": "PULSE"},
        }
    },
    "mux2": {
        "is_sequential": False,
        "sim_time": "1ns",
        "control_configs": {
            "I0": {"I1": "0", "S": "0"},
            "I1": {"I0": "0", "S": "0"},
            "S": {"I0": "vd", "I1": "0"},
        }
    },
    "nand": {
        "is_sequential": False,
        "sim_time": "1ns",
        "control_configs": {
            "A": {"B": "0", "C": "0", "D": "0"},
            "B": {"A": "0", "C": "0", "D": "0"},
            "C": {"A": "0", "B": "0", "D": "0"},
            "D": {"A": "0", "B": "0", "C": "0"},
        }
    },
    "xor": {
        "is_sequential": False,
        "sim_time": "2ns",
        "control_configs": {
            "A": {"B": "0"},
            "B": {"A": "0"},
        }
    },
    "fulladder": {
        "is_sequential": False,
        "sim_time": "2ns",
        "control_configs": {
            "A": {"B": "0", "Cin": "0"},
            "B": {"A": "0", "Cin": "0"},
            "Cin": {"A": "0", "B": "0"},
        }
    },
    "halfadder": {
        "is_sequential": False,
        "sim_time": "2ns",
        "control_configs": {
            "A": {"B": "0"},
            "B": {"A": "0"},
        }
    },
    "inv": {
        "is_sequential": False,
        "sim_time": "1ns",
        "control_configs": {
            "A": {},
        }
    },
    "buffer": {
        "is_sequential": False,
        "sim_time": "1ns",
        "control_configs": {
            "A": {},
        }
    },
    "trisbuf": {
        "is_sequential": False,
        "sim_time": "1ns",
        "control_configs": {
            "A": {"Enable": "vd"},
            "Enable": {"A": "vd"},
        }
    },
}
#  solution for propagation delay - will do for the time being 
REFERENCE_SPICE_PATTERNS = {
    "inv": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 1.8V 60NS 1.8V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1",
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1"
        ],
        "sim_time": "60NS",
        "cin_value": "2.2f"
    },
    "buffer": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 1.8V 60NS 1.8V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1"
        ],
        "sim_time": "60NS",
        "cin_value": "2.2f"
    },
    "nand2": {
        "pwl": {
            "A": "0NS 0V  5NS 0V  5.1NS 1.8V  15NS 1.8V  15.1NS 0V  25NS 0V  25.1NS 1.8V 60NS 1.8V",
            "B": "0NS 1.8V 35NS 1.8V 35.1NS 0V 40NS 0V 40.1NS 1.8V 50NS 1.8V 50.1NS 0V 60NS 0V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1  TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1",
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1  TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            "",
            ".measure tran tpd_B_Y_f TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=30NS",
            ".measure tran tpd_B_Y_r TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=30NS"
        ],
        "sim_time": "60NS",
        "cin_value": "2.2f",
        "scale": True
    },
    "nand3": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 1.8V 90NS 1.8V",
            "B": "0NS 1.8V 35NS 1.8V 35.1NS 0V 40NS 0V 40.1NS 1.8V 50NS 1.8V 50.1NS 0V 55NS 0V 55.1NS 1.8V 90NS 1.8V",
            "C": "0NS 1.8V 65NS 1.8V 65.1NS 0V 70NS 0V 70.1NS 1.8V 80NS 1.8V 80.1NS 0V 90NS 0V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1",
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            "",
            ".measure tran tpd_B_Y_f TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=30NS",
            ".measure tran tpd_B_Y_r TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=30NS",
            "",
            ".measure tran tpd_C_Y_f TRIG v(C) VAL='0.5*1.8' RISE=1 FROM=60NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=60NS",
            ".measure tran tpd_C_Y_r TRIG v(C) VAL='0.5*1.8' FALL=1 FROM=60NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=60NS"
        ],
        "sim_time": "90NS",
        "cin_value": "2.2f"
    },
    "nand4": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 1.8V 120NS 1.8V",
            "B": "0NS 1.8V 35NS 1.8V 35.1NS 0V 40NS 0V 40.1NS 1.8V 50NS 1.8V 50.1NS 0V 55NS 0V 55.1NS 1.8V 120NS 1.8V",
            "C": "0NS 1.8V 65NS 1.8V 65.1NS 0V 70NS 0V 70.1NS 1.8V 80NS 1.8V 80.1NS 0V 85NS 0V 85.1NS 1.8V 120NS 1.8V",
            "D": "0NS 1.8V 95NS 1.8V 95.1NS 0V 100NS 0V 100.1NS 1.8V 110NS 1.8V 110.1NS 0V 120NS 0V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1",
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            "",
            ".measure tran tpd_B_Y_f TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=30NS",
            ".measure tran tpd_B_Y_r TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=30NS",
            "",
            ".measure tran tpd_C_Y_f TRIG v(C) VAL='0.5*1.8' RISE=1 FROM=60NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=60NS",
            ".measure tran tpd_C_Y_r TRIG v(C) VAL='0.5*1.8' FALL=1 FROM=60NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=60NS",
            "",
            ".measure tran tpd_D_Y_f TRIG v(D) VAL='0.5*1.8' RISE=1 FROM=90NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=90NS",
            ".measure tran tpd_D_Y_r TRIG v(D) VAL='0.5*1.8' FALL=1 FROM=90NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=90NS"
        ],
        "sim_time": "120NS",
        "cin_value": "2.2f"
    },
    "xor2": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 0V 60NS 0V",
            "B": "0NS 0V 35NS 0V 35.1NS 1.8V 45NS 1.8V 45.1NS 0V 60NS 0V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1",
            "",
            ".measure tran tpd_B_Y_r TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=30NS",
            ".measure tran tpd_B_Y_f TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=30NS"
        ],
        "sim_time": "60NS",
        "cin_value": "2.2f"
    },
    "xor": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 0V 60NS 0V",
            "B": "0NS 0V 35NS 0V 35.1NS 1.8V 45NS 1.8V 45.1NS 0V 60NS 0V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1",
            "",
            ".measure tran tpd_B_Y_r TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' RISE=1 FROM=30NS",
            ".measure tran tpd_B_Y_f TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(Y) VAL='0.5*1.8' FALL=1 FROM=30NS"
        ],
        "sim_time": "60NS",
        "cin_value": "2.2f"
    },
    "fulladder": {
        "pwl": {
            "A": "0NS 0V  5NS 0V  5.1NS 1.8V  15NS 1.8V  15.1NS 0V  25NS 0V  30NS 1.8V  90NS 1.8V",
            "B": "0NS 1.8V  30NS 1.8V  30.1NS 0V  35NS 0V  35.1NS 1.8V  45NS 1.8V  45.1NS 0V  60NS 0V  90NS 0V",
            "Cin": "0NS 0V  60NS 0V  65NS 0V  65.1NS 1.8V  75NS 1.8V  75.1NS 0V  90NS 0V"
        },
        "measurements": [
            ".measure tran tpd_A_S_r TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(S) VAL='0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_A_S_f TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(S) VAL='0.5*1.8' TD=0NS FALL=1",
            "",
            ".measure tran tpd_B_S_r TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(S) VAL='0.5*1.8' RISE=1 FROM=30NS",
            ".measure tran tpd_B_S_f TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(S) VAL='0.5*1.8' FALL=1 FROM=30NS",
            "",
            ".measure tran tpd_Cin_S_r TRIG v(Cin) VAL='0.5*1.8' RISE=1 FROM=60NS TARG v(S) VAL='0.5*1.8' RISE=1 FROM=60NS",
            ".measure tran tpd_Cin_S_f TRIG v(Cin) VAL='0.5*1.8' FALL=1 FROM=60NS TARG v(S) VAL='0.5*1.8' FALL=1 FROM=60NS",
            "",
            ".measure tran tpd_A_Cout_r TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Cout) VAL='0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_A_Cout_f TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Cout) VAL='0.5*1.8' TD=0NS FALL=1",
            "",
            ".measure tran tpd_B_Cout_r TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(Cout) VAL='0.5*1.8' RISE=1 FROM=30NS",
            ".measure tran tpd_B_Cout_f TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(Cout) VAL='0.5*1.8' FALL=1 FROM=30NS",
            "",
            ".measure tran tpd_Cin_Cout_r TRIG v(Cin) VAL='0.5*1.8' RISE=1 FROM=60NS TARG v(Cout) VAL='0.5*1.8' RISE=1 FROM=60NS",
            ".measure tran tpd_Cin_Cout_f TRIG v(Cin) VAL='0.5*1.8' FALL=1 FROM=60NS TARG v(Cout) VAL='0.5*1.8' FALL=1 FROM=60NS"
        ],
        "sim_time": "90NS",
        "cin_value": "2.215f"
    },
    "halfadder": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 65NS 0V 65.1NS 1.8V 75NS 1.8V 75.1NS 0V 85NS 0V 90NS 1.8V 120NS 1.8V",
            "B": "0NS 0V 35NS 0V 35.1NS 1.8V 45NS 1.8V 45.1NS 0V 55NS 0V 60NS 1.8V 95NS 1.8V 95.1NS 0V 105NS 0V 105.1NS 1.8V 120NS 1.8V"
        },
        "measurements": [
            ".measure tran tpd_A_S_r TRIG v(A) VAL='0.5*1.8' RISE=1 TARG v(S) VAL='0.5*1.8' RISE=1",
            ".measure tran tpd_A_S_f TRIG v(A) VAL='0.5*1.8' FALL=1 TARG v(S) VAL='0.5*1.8' FALL=1",
            "",
            ".measure tran tpd_B_S_r TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=30NS TARG v(S) VAL='0.5*1.8' RISE=1 FROM=30NS",
            ".measure tran tpd_B_S_f TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=30NS TARG v(S) VAL='0.5*1.8' FALL=1 FROM=30NS",
            "",
            ".measure tran tpd_A_S_inv_f TRIG v(A) VAL='0.5*1.8' RISE=1 FROM=60NS TARG v(S) VAL='0.5*1.8' FALL=1 FROM=60NS",
            "",
            ".measure tran tpd_A_C_r TRIG v(A) VAL='0.5*1.8' RISE=1 FROM=60NS TARG v(C) VAL='0.5*1.8' RISE=1 FROM=60NS",
            ".measure tran tpd_A_C_f TRIG v(A) VAL='0.5*1.8' FALL=1 FROM=60NS TARG v(C) VAL='0.5*1.8' FALL=1 FROM=60NS",
            "",
            ".measure tran tpd_B_C_f TRIG v(B) VAL='0.5*1.8' FALL=1 FROM=90NS TARG v(C) VAL='0.5*1.8' FALL=1 FROM=90NS",
            ".measure tran tpd_B_C_r TRIG v(B) VAL='0.5*1.8' RISE=1 FROM=90NS TARG v(C) VAL='0.5*1.8' RISE=1 FROM=90NS"
        ],
        "sim_time": "120NS",
        "cin_value": "2.2f"
    },
    "mux2": {
        "pwl": {
            "I0": "0NS 0V  2NS 0V  2.1NS 1.8V  6NS 1.8V  6.1NS 0V  90NS 0V",
            "I1": "0NS 0V  10NS 0V  12NS 0V  12.1NS 1.8V  16NS 1.8V  16.1NS 0V  20NS 0V  20.1NS 1.8V  90NS 1.8V",
            "S": "0NS 0V  10NS 0V  10.1NS 1.8V  20NS 1.8V  24NS 1.8V  24.1NS 0V  28NS 0V  28.1NS 1.8V  90NS 1.8V"
        },
        "measurements": [
            ".measure tran tpd_I0_Y_r TRIG v(I0) VAL= '0.5*1.8' TD=0NS RISE=1  TARG v(Y) VAL= '0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_I0_Y_f TRIG v(I0) VAL= '0.5*1.8' TD=0NS FALL=1  TARG v(Y) VAL= '0.5*1.8' TD=0NS FALL=1",
            "",
            ".measure tran tpd_I1_Y_r TRIG v(I1) VAL= '0.5*1.8' TD=10NS RISE=1  TARG v(Y) VAL= '0.5*1.8' TD=10NS RISE=1",
            ".measure tran tpd_I1_Y_f TRIG v(I1) VAL= '0.5*1.8' TD=10NS FALL=1  TARG v(Y) VAL= '0.5*1.8' TD=10NS FALL=1",
            "",
            ".measure tran tpd_S_Y_f  TRIG v(S)  VAL= '0.5*1.8' TD=20NS FALL=1  TARG v(Y) VAL= '0.5*1.8' TD=20NS FALL=1",
            ".measure tran tpd_S_Y_r  TRIG v(S)  VAL= '0.5*1.8' TD=20NS RISE=1  TARG v(Y) VAL= '0.5*1.8' TD=20NS RISE=1"
        ],
        "sim_time": "90NS",
        "cin_value": "2.215f",
        "scale": True
    },
    "trisbuf": {
        "pwl": {
            "A": "0NS 0V 5NS 0V 5.1NS 1.8V 15NS 1.8V 15.1NS 0V 25NS 0V 25.1NS 1.8V 60NS 1.8V",
            "Enable": "DC 1.8V"
        },
        "measurements": [
            ".measure tran tpd_A_Y_r TRIG v(A) VAL='0.5*1.8' TD=0NS RISE=1 TARG v(Y) VAL='0.5*1.8' TD=0NS RISE=1",
            ".measure tran tpd_A_Y_f TRIG v(A) VAL='0.5*1.8' TD=0NS FALL=1 TARG v(Y) VAL='0.5*1.8' TD=0NS FALL=1"
        ],
        "sim_time": "60NS",
        "cin_value": "2.2f"
    },
    "scandtype": {
        "pwl": {
            "D": "0NS 0V 10NS 0V 10.1NS 1.8V 35NS 1.8V 35.1NS 0V 120NS 0V",
            "SDI": "0NS 0V 70NS 0V 70.1NS 1.8V 95NS 1.8V 95.1NS 0V 120NS 0V",
            "Clock": "0NS 0V 15NS 0V 15.1NS 1.8V 25NS 1.8V 25.1NS 0V 45NS 0V 45.1NS 1.8V 55NS 1.8V 55.1NS 0V 75NS 0V 75.1NS 1.8V 85NS 1.8V 85.1NS 0V 105NS 0V 105.1NS 1.8V 115NS 1.8V 115.1NS 0V",
            "nReset": "0NS 0V 5NS 0V 5.1NS 1.8V 120NS 1.8V",
            "Test": "0NS 0V 60NS 0V 60.1NS 1.8V 120NS 1.8V"
        },
        "measurements": [
            ".measure tran tcq_D_r TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=10NS TARG v(Q) VAL='0.5*1.8' RISE=1 FROM=10NS",
            "",
            ".measure tran tcq_D_f TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=40NS TARG v(Q) VAL='0.5*1.8' FALL=1 FROM=40NS",
            "",
            ".measure tran tcq_Scan_r TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=70NS TARG v(Q) VAL='0.5*1.8' RISE=1 FROM=70NS",
            "",
            ".measure tran tcq_Scan_f TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=100NS TARG v(Q) VAL='0.5*1.8' FALL=1 FROM=100NS"
        ],
        "sim_time": "120NS",
        "cin_value": "2.2f",
        "instance": "X1 D SDI Clock nReset Test Q nQ Vdd GND scandtype"
    },
    "scanreg": {
        "pwl": {
            "D": "0NS 0V 10NS 0V 10.1NS 1.8V 35NS 1.8V 35.1NS 0V 120NS 0V",
            "SDI": "0NS 0V 70NS 0V 70.1NS 1.8V 95NS 1.8V 95.1NS 0V 120NS 0V",
            "Clock": "0NS 0V 15NS 0V 15.1NS 1.8V 25NS 1.8V 25.1NS 0V 45NS 0V 45.1NS 1.8V 55NS 1.8V 55.1NS 0V 75NS 0V 75.1NS 1.8V 85NS 1.8V 85.1NS 0V 105NS 0V 105.1NS 1.8V 115NS 1.8V 115.1NS 0V",
            "nReset": "0NS 0V 5NS 0V 5.1NS 1.8V 120NS 1.8V",
            "Test": "0NS 0V 60NS 0V 60.1NS 1.8V 120NS 1.8V",
            "Load": "DC 1.8V"
        },
        "measurements": [
            ".measure tran tcq_Load_r TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=10NS TARG v(Q) VAL='0.5*1.8' RISE=1 FROM=10NS",
            "",
            ".measure tran tcq_Load_f TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=40NS TARG v(Q) VAL='0.5*1.8' FALL=1 FROM=40NS",
            "",
            ".measure tran tcq_Scan_r TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=70NS TARG v(Q) VAL='0.5*1.8' RISE=1 FROM=70NS",
            "",
            ".measure tran tcq_Scan_f TRIG v(Clock) VAL='0.5*1.8' RISE=1 FROM=100NS TARG v(Q) VAL='0.5*1.8' FALL=1 FROM=100NS"
        ],
        "sim_time": "120NS",
        "cin_value": "2.2f",
        "instance": "X1 D SDI Clock nReset Test Load Q nQ Vdd GND scanreg"
    }
}
def clean_generated_files():
    """Removes old test .sp files to ensure a clean slate."""
    print(f"\n{'='*60}")
    print("CLEANUP: Removing old test files...")
    print(f"{'='*60}")
    removed_count = 0
    for filename in os.listdir('.'):
        if filename.endswith('.sp') and '_' in filename:
            try:
                os.remove(filename)
                removed_count += 1
            except OSError as e:
                print(f"  Error deleting {filename}: {e}")
    print(f"Cleanup complete. Removed {removed_count} test files.\n")
def generate_input_cap_spice(cellname, input_pin, all_inputs, all_outputs, base_cellname):
    """
    Generate a SPICE input capacitance measurement file for a specific input pin.
    """
    filename = f"{cellname}_{input_pin}.sp"
    if base_cellname not in CELL_TEST_CONFIG:
        log_message(f"  :( No test config for '{base_cellname}', skipping {filename}", is_error=True)
        return None
    config = CELL_TEST_CONFIG[base_cellname]
    is_sequential = config.get("is_sequential", False)
    sim_time = config.get("sim_time", "1ns")
    if input_pin not in config["control_configs"]:
        log_message(f"  :( No control config for pin '{input_pin}' in {base_cellname}", is_error=True)
        return None
    control_signals = config["control_configs"][input_pin]
    spice_file = f"{cellname}.spice"
    subckt_lines = []
    in_subckt = False
    found_subckt = False
    try:
        with open(spice_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line_lower = line.strip().lower()
            if line_lower.startswith('.subckt') and cellname.lower() in line_lower:
                in_subckt = True
                found_subckt = True
            if in_subckt:
                subckt_lines.append(line)
            if in_subckt and line_lower == '.ends':
                break
        if not found_subckt:
            log_message(f"    Wrapping flat netlist in .subckt definition")
            all_nodes = set()
            internal_nodes = set()
            for line in lines:
                stripped = line.strip()
                if stripped and stripped.startswith('M'):
                    parts = stripped.split()
                    if len(parts) >= 5:
                        for node in parts[1:5]:
                            all_nodes.add(node)
                            if node.startswith('active_') or node.endswith('#'):
                                internal_nodes.add(node)
            detected_ports = all_nodes - internal_nodes - {'Vdd', 'GND'}
            valid_ports = detected_ports & (set(all_inputs) | set(all_outputs))
            final_inputs = [inp for inp in all_inputs if inp in valid_ports]
            final_outputs = [out for out in all_outputs if out in valid_ports]
            port_list = final_inputs + final_outputs + ['Vdd', 'GND']
            port_str = ' '.join(port_list)
            print(f"    Detected ports: inputs={final_inputs}, outputs={final_outputs}")
            scale_factor = 0.02
            for line in lines:
                if line.strip().startswith('.option scale'):
                    parts = line.split('=')
                    if len(parts) > 1:
                        scale_str = parts[1].strip().lower()
                        if scale_str.endswith('u'):
                            scale_factor = float(scale_str[:-1])
                    break
            subckt_lines = []
            subckt_lines.append(f".subckt {cellname} {port_str}\n")
            for line in lines:
                stripped = line.strip()
                if stripped and stripped.startswith('M'):
                    import re
                    w_match = re.search(r'\bw=(\d+\.?\d*)', line, re.IGNORECASE)
                    l_match = re.search(r'\bl=(\d+\.?\d*)', line, re.IGNORECASE)
                    if w_match and l_match:
                        w_val = float(w_match.group(1))
                        l_val = float(l_match.group(1))
                        W_abs = w_val * scale_factor
                        L_abs = l_val * scale_factor
                        new_line = re.sub(r'\bw=\d+\.?\d*', f'W={W_abs}u', line, flags=re.IGNORECASE)
                        new_line = re.sub(r'\bl=\d+\.?\d*', f'L={L_abs}u', new_line, flags=re.IGNORECASE)
                        subckt_lines.append(new_line)
                    else:
                        subckt_lines.append(line)
            subckt_lines.append(".ends\n")
    except FileNotFoundError:
        log_message(f"  :( Could not find {spice_file}", is_error=True)
        return None
    if not subckt_lines:
        log_message(f"  :( Could not extract subcircuit from {spice_file}", is_error=True)
        return None
    sp_content = []
    sp_content.append(f"*{cellname} {input_pin} input capacitance measurement")
    sp_content.append(f"*Input: {', '.join(all_inputs)}")
    sp_content.append(f"*Output: {', '.join(all_outputs)}")
    sp_content.append("")
    sp_content.append(".param par1fn_mc=0")
    sp_content.append(".param par2fn_mc=0  ")
    sp_content.append(".param par3fn_mc=0")
    sp_content.append("   ")
    sp_content.append(".option redefsub=1")
    sp_content.append("")
    sp_content.append("*TSMC180 model")
    sp_content.append('.lib "/opt/cad/designkits/ecs/hspice/tsmc180.lib" TT')
    sp_content.append(".temp 25")
    sp_content.append("")
    sp_content.append(".param vd=1.8V")
    sp_content.append(".param L=0.18u")
    sp_content.append(".param WP=0.98u")
    sp_content.append(".param WN=0.54u")
    sp_content.append(".param CLOAD=OPTC(1fF, 0.0001fF, 10fF)")
    sp_content.append("")
    sp_content.append("*power supply")
    sp_content.append("Vvdd Vdd 0 dc vd")
    sp_content.append("Vgnd GND 0 dc 0")
    sp_content.append("")
    sp_content.append("*input waveform")
    sp_content.append("Vin in 0 PULSE 0 vd 100ps 80ps 80ps 500ps 1u ")
    sp_content.append("")
    sp_content.append("*control signals for testing")
    for signal, value in control_signals.items():
        if signal == input_pin:
            continue  
        if signal not in all_inputs:
            continue  
        if value == "PULSE":
            sp_content.append(f"V{signal}\t{signal}  0 PULSE 0 vd 100ps 80ps 80ps 500ps 1u ")
        elif value == "vd":
            sp_content.append(f"V{signal}\t{signal}  0 dc vd")
        elif value == "0":
            sp_content.append(f"V{signal}\t{signal}  0 dc 0")
    sp_content.append(" ")
    sp_content.append("*circuit 1")
    sp_content.append("Xinv_driver  mid0 in Vdd GND inv")
    port_list = []
    for inp in all_inputs:
        if inp == input_pin:
            port_list.append("mid0")
        else:
            port_list.append(inp)
    port_list.extend(all_outputs)
    port_list.extend(["Vdd", "GND"])
    sp_content.append(f"Xdut_{cellname} {' '.join(port_list)} {cellname}")
    sp_content.append("")
    sp_content.append("*circuit 2")
    sp_content.append("Xinv_model   mid1 in Vdd GND inv")
    sp_content.append("Cload mid1 GND CLOAD")
    sp_content.append("")
    sp_content.append("*measurements")
    sp_content.append(".measure TRAN tdr   TRIG v(in) VAL='0.5*vd' FALL=1 TARG v(mid0) VAL='0.5*vd' RISE=1")
    sp_content.append(".measure TRAN tdf   TRIG v(in) VAL='0.5*vd' RISE=1 TARG v(mid0) VAL='0.5*vd' FALL=1")
    sp_content.append(".measure TRAN tdavg PARAM='(tdr+tdf)/2'")
    sp_content.append("")
    sp_content.append(".measure TRAN tdrc  TRIG v(in) VAL='0.5*vd' FALL=1 TARG v(mid1) VAL='0.5*vd' RISE=1")
    sp_content.append(".measure TRAN tdfc  TRIG v(in) VAL='0.5*vd' RISE=1 TARG v(mid1) VAL='0.5*vd' FALL=1")
    sp_content.append(".measure TRAN tdavgc PARAM='(tdrc+tdfc)/2'\tGOAL=tdavg")
    sp_content.append("")
    sp_content.append(".model OPT1 opt")
    sp_content.append("")
    sp_content.append(f".tran 1ps {sim_time} SWEEP OPTIMIZE=optc RESULTS=tdavgc MODEL=OPT1 ")
    sp_content.append("")
    sp_content.append("*inverter")
    sp_content.append(".subckt inv out in Vdd GND")
    sp_content.append("mn out in GND GND nch W=WN L=L")
    sp_content.append("mp out in Vdd Vdd pch W=WP L=L  ")
    sp_content.append(".ends")
    sp_content.append("")
    sp_content.append(f"*{cellname}")
    for line in subckt_lines:
        sp_content.append(line.rstrip())
    sp_content.append("")
    sp_content.append(".probe v(*)")
    sp_content.append("")
    sp_content.append(".end")
    sp_content.append("")
    sp_content.append("")
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(sp_content))
        print(f"  :D Generated {filename}")
        return filename
    except Exception as e:
        log_message(f"  :( Error writing {filename}: {e}", is_error=True)
        return None
def run_hspice(sp_filename):
    """
    Run HSPICE on a .sp file.
    Returns (success, mt0_filename)
    """
    try:
        result = subprocess.run(
            ['hspice', sp_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=60
        )
        base_name = sp_filename.replace('.sp', '')
        mt0_file = f"{base_name}.mt0"
        if os.path.exists(mt0_file):
            return (True, mt0_file)
        else:
            log_message(f"  :( HSPICE ran but no .mt0 file created for {sp_filename}", is_error=True)
            if result.stderr:
                log_message(f"  HSPICE stderr: {result.stderr[:200]}", is_error=True)
            return (False, None)
    except subprocess.TimeoutExpired:
        log_message(f"  :( HSPICE timeout for {sp_filename}", is_error=True)
        return (False, None)
    except FileNotFoundError:
        log_message(f"  :( HSPICE not found in PATH", is_error=True)
        return (False, None)
    except Exception as e:
        log_message(f"  :( HSPICE error for {sp_filename}: {e}", is_error=True)
        return (False, None)
def parse_mt0_file(mt0_filename):
    """
    Parse .mt0 file to extract capacitance measurement.
    MT0 files have headers and values spread across multiple lines.
    Returns dict with measurements or None if failed.
    """
    try:
        with open(mt0_filename, 'r') as f:
            lines = f.readlines()
        header_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('.TITLE'):
                header_start = i + 1
                break
        if header_start == -1:
            return None
        headers = []
        value_start = header_start
        for i in range(header_start, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            tokens = line.split()
            if tokens and (tokens[0].replace('.', '').replace('-', '').replace('+', '').replace('e', '').isdigit() or 
                          tokens[0][0].isdigit()):
                value_start = i
                break
            headers.extend(tokens)
        try:
            cload_idx = headers.index('cload')
        except ValueError:
            return None
        values = []
        for i in range(value_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('$') or line.startswith('.'):
                continue
            values.extend(line.split())
        if cload_idx < len(values):
            cap_value = float(values[cload_idx])
            cap_ff = cap_value * 1e15
            return {'capacitance_fF': cap_ff}
        else:
            return None
    except Exception as e:
        log_message(f"  :( Error parsing {mt0_filename}: {e}", is_error=True)
        return None
def ensure_netlist_wrapped(cellname, netlist_file, pattern):
    """
    Checks if the netlist file is flat (missing .subckt).
    If so, wraps it in .subckt {cellname} ... .ends to make it a valid subcircuit.
    """
    try:
        with open(netlist_file, 'r') as f:
            content = f.read()
        if ".subckt" not in content.lower():
            log_message(f"  Note: Wrapping flat netlist {netlist_file} in .subckt", is_error=False)
            if "instance" in pattern:
                parts = pattern["instance"].split()
                ports = parts[1:-1]
                port_str = " ".join(ports)
            else:
                return False
            new_content = []
            lines = content.splitlines()
            header = []
            options = []
            body = []
            for line in lines:
                stripped = line.strip()
                if stripped.lower().startswith('.option'):
                    options.append(line)
                elif stripped.startswith('*') or not stripped:
                    if not body and not options:
                        header.append(line)
                    else:
                        body.append(line)
                else:
                    body.append(line)
            new_content.extend(header)
            new_content.extend(options)
            new_content.append(f".subckt {cellname} {port_str}")
            new_content.extend(body)
            new_content.append(".ends")
            with open(netlist_file, 'w') as f:
                f.write('\n'.join(new_content))
            return True
    except Exception as e:
        log_message(f"  :( Error checking/wrapping netlist {netlist_file}: {e}", is_error=True)
    return False
def generate_propagation_delay_spice(cellname, all_inputs, all_outputs, base_cellname):
    """
    Generate SPICE propagation delay file using hardcoded reference patterns.
    """
    filename = f"{cellname}_pd.sp"
    if cellname in REFERENCE_SPICE_PATTERNS:
        pattern = REFERENCE_SPICE_PATTERNS[cellname]
    elif base_cellname in REFERENCE_SPICE_PATTERNS:
        pattern = REFERENCE_SPICE_PATTERNS[base_cellname]
    else:
        log_message(f"  :( No reference pattern for '{cellname}' or '{base_cellname}', skipping {filename}", is_error=True)
        return None
    netlist_file = f"{cellname}.spice"
    if not os.path.exists(netlist_file):
        log_message(f"  :( Netlist file {netlist_file} not found", is_error=True)
        return None
    ensure_netlist_wrapped(cellname, netlist_file, pattern)
    sp_content = []
    sp_content.append(f"** HSPICE file for {cellname}")
    sp_content.append(f"**   - generated by ext2sp v9.0")
    sp_content.append("")
    sp_content.append("** Include transistor models for tsmc180")
    sp_content.append(".include /opt/cad/designkits/ecs/hspice/tsmc180.mod")
    sp_content.append("")
    sp_content.append(f"** Include netlist file for {cellname}")
    sp_content.append(f".include {netlist_file}")
    if pattern.get("scale", False):
        sp_content.append(".option scale=0.02u")
    sp_content.append("")
    sp_content.append("** Default 1.8V Power Supply")
    sp_content.append("Vsupply Vdd GND 1.8V")
    if "instance" in pattern:
        sp_content.append(pattern["instance"])
    else:
        instance_ports = all_inputs + all_outputs + ['Vdd', 'GND']
        instance_port_str = ' '.join(instance_ports)
        sp_content.append(f"X1 {instance_port_str} {cellname}")
    sp_content.append("** " + "-"*87)
    cin_value = pattern.get("cin_value", "2.2f")
    sp_content.append(f".param Cin_per_inv = {cin_value}")
    sp_content.append(".param FanOut = 1")
    sp_content.append("         ")
    sp_content.append("** " + "-"*87)
    sp_content.append("** Add load capacitances")
    for output in all_outputs:
        sp_content.append(f"CL_{output} {output} GND 'FanOut * Cin_per_inv' ")
    sp_content.append(" ")
    sp_content.append("** " + "-"*87)
    sp_content.append("** Specify input signals here")
    pwl_dict = pattern["pwl"]
    for inp in all_inputs:
        if inp in pwl_dict:
            pwl_value = pwl_dict[inp]
            if pwl_value.startswith("DC"):
                sp_content.append(f"V{inp} {inp} GND {pwl_value}")
            else:
                sp_content.append(f"V{inp} {inp} GND PWL ({pwl_value})")
        else:
            sp_content.append(f"V{inp} {inp} GND DC 0V")
    sp_content.append("")
    sim_time = pattern.get("sim_time", "60NS")
    sp_content.append("** Default Simulation")
    sp_content.append(f".TRAN 10PS {sim_time} SWEEP FanOut 1 5 4")
    sp_content.append("")
    for measurement in pattern["measurements"]:
        sp_content.append(measurement)
    sp_content.append("")
    sp_content.append(".OPTIONS POST")
    sp_content.append(".END")
    sp_content.append("")
    try:
        with open(filename, 'w') as f:
            f.write('\n'.join(sp_content))
        log_message(f"  :) Generated {filename}")
        return filename
    except Exception as e:
        log_message(f"  :( Error writing {filename}: {e}", is_error=True)
        return None
def parse_propagation_delay_mt0(mt0_filename, cellname, base_cellname):
    """
    Parse .mt0 file to extract propagation delay measurements.
    Returns dict with measurements like {'tpd_A_Y_r': [values], 'tpd_A_Y_f': [values], ...}
    """
    try:
        with open(mt0_filename, 'r') as f:
            lines = f.readlines()
        header_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('.TITLE'):
                header_start = i + 1
                break
        if header_start == -1:
            return None
        headers = []
        value_start = header_start
        for i in range(header_start, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            tokens = line.split()
            if tokens and (tokens[0].replace('.', '').replace('-', '').replace('+', '').replace('e', '').isdigit() or 
                          tokens[0][0].isdigit()):
                value_start = i
                break
            headers.extend(tokens)
        if cellname in REFERENCE_SPICE_PATTERNS:
            pattern = REFERENCE_SPICE_PATTERNS[cellname]
        elif base_cellname in REFERENCE_SPICE_PATTERNS:
            pattern = REFERENCE_SPICE_PATTERNS[base_cellname]
        else:
            return None
        expected_measurements = []
        for meas_line in pattern["measurements"]:
            if meas_line.strip() and meas_line.startswith(".measure"):
                parts = meas_line.split()
                if len(parts) >= 3:
                    meas_name = parts[2]
                    expected_measurements.append(meas_name)
        headers_lower = [h.lower() for h in headers]
        measurement_indices = {}
        for meas_name in expected_measurements:
            try:
                idx = headers_lower.index(meas_name.lower())
                measurement_indices[meas_name] = idx
            except ValueError:
                pass
        if not measurement_indices:
            log_message(f"  :( No measurements found in headers", is_error=True)
            log_message(f"    Expected: {expected_measurements}", is_error=True)
            log_message(f"    Headers: {headers[:10]}", is_error=True)  
            return None
        values = []
        for i in range(value_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('$') or line.startswith('.'):
                continue
            values.extend(line.split())
        measurements = {}
        for meas_name, idx in measurement_indices.items():
            if idx < len(values):
                value_str = values[idx].strip()
                if value_str.lower() == 'failed':
                    log_message(f"    Measurement {meas_name} failed.", is_error=True)
                    continue
                try:
                    value_seconds = float(value_str)
                    value_ns = value_seconds * 1e9
                    measurements[meas_name] = value_ns
                    log_message(f"    Found {meas_name}: {value_ns:.4f} ns")
                except ValueError:
                    log_message(f"    :( Could not parse value for {meas_name}: {value_str}", is_error=True)
                    continue
        return measurements if measurements else None
    except Exception as e:
        log_message(f"  :( Error parsing propagation delay from {mt0_filename}: {e}", is_error=True)
        return None
def get_port_categories(cellname, existing_ports):
    """
    Categorize ports based on cell type using PORT_DIRECTIONS dictionary.
    Also validates that detected ports match expected ports.
    For multi-input gates (nand, nor, and, or), dynamically detects which inputs exist.
    Returns: (input_ports, output_ports, power_ports, passthrough_ports)
    """
    base_cellname = cellname if cellname in PORT_DIRECTIONS else cellname.rstrip('0123456789')
    if base_cellname not in PORT_DIRECTIONS:
        log_message(f"  :( Warning: Cell type '{base_cellname}' not in PORT_DIRECTIONS dictionary", is_error=True)
        log_message("  :( Please add it to the dictionary at the top of the script", is_error=True)
        return [], [], [], []
    directions = PORT_DIRECTIONS[base_cellname]
    if base_cellname in ['nand', 'nor', 'and', 'or']:
        possible_inputs = ['A', 'B', 'C', 'D']
        detected_inputs = [inp for inp in possible_inputs if inp in existing_ports]
        directions = {
            "Power": directions["Power"],
            "Not connected": directions["Not connected"],
            "Input": tuple(detected_inputs),
            "Output": directions["Output"],
        }
        log_message(f"  Detected {len(detected_inputs)}-input {base_cellname} gate: inputs {detected_inputs}")
    expected_ports = set()
    for ports_tuple in directions.values():
        if ports_tuple:
            expected_ports.update(ports_tuple)
    detected_ports_set = set(existing_ports)
    missing_ports = expected_ports - detected_ports_set
    extra_ports = detected_ports_set - expected_ports
    if missing_ports:
        log_message(f"\n  :( WARNING: Expected ports not detected: {sorted(missing_ports)}", is_error=True)
    if extra_ports:
        log_message(f"\n  :( WARNING: Unexpected ports detected: {sorted(extra_ports)}", is_error=True)
    if not missing_ports and not extra_ports:
        log_message(f"\n  :( All ports match dictionary definition")
    input_ports = []
    output_ports = []
    power_ports = []
    passthrough_ports = []
    for port_name in existing_ports:
        categorized = False
        for direction, ports in directions.items():
            if ports and port_name in ports:
                if direction == "Input":
                    input_ports.append(port_name)
                elif direction == "Output":
                    output_ports.append(port_name)
                elif direction == "Power":
                    power_ports.append(port_name)
                elif direction == "Not connected":
                    passthrough_ports.append(port_name)
                categorized = True
                break
        if not categorized:
            log_message(f"  :( Port '{port_name}' not found in dictionary for '{base_cellname}'", is_error=True)
    return input_ports, output_ports, power_ports, passthrough_ports
def append_spice_measurements(cellname, input_ports, output_ports):
    """
    Injects .measure commands into the .sp file generated by ext2sp.
    Inserts content BEFORE the .END statement so HSPICE reads it.
    """
    target_file = f"{cellname}.sp"
    if not os.path.exists(target_file):
        target_file = f"{cellname}.spice" 
    if not os.path.exists(target_file):
         log_message(f"  :( Could not find {target_file} to inject measurements.", is_error=True)
         return
    if not input_ports or not output_ports:
        log_message(f"  :( Cannot generate testbench: missing inputs or outputs.", is_error=True)
        return
    is_sequential = 'Clock' in input_ports
    trig_pin = 'Clock' if is_sequential else input_ports[0]
    targ_pin = output_ports[0] 
    if targ_pin == 'nQ' and 'Q' in output_ports: targ_pin = 'Q'
    log_message(f"  Injecting measurements into {target_file}: Trig={trig_pin} -> Targ={targ_pin}")
    measure_block = []
    measure_block.append(f"*\nAuto-Generated Measurements for {cellname}")
    measure_block.append("* ==========================================")
    measure_block.append(".param sup=1.8V")
    measure_block.append(f"Vstim {trig_pin} GND! PULSE(0 'sup' 1ns 100ps 100ps 4ns 10ns)")
    measure_block.append(f".measure tran tpd_rise TRIG v({trig_pin}) VAL='sup*0.5' RISE=1 TARG v({targ_pin}) VAL='sup*0.5' RISE=1")
    measure_block.append(f".measure tran tpd_fall TRIG v({trig_pin}) VAL='sup*0.5' FALL=1 TARG v({targ_pin}) VAL='sup*0.5' FALL=1")
    measure_block.append(f".measure tran t_rise TRIG v({targ_pin}) VAL='sup*0.1' RISE=1 TARG v({targ_pin}) VAL='sup*0.9' RISE=1")
    measure_block.append(f".measure tran t_fall TRIG v({targ_pin}) VAL='sup*0.9' FALL=1 TARG v({targ_pin}) VAL='sup*0.1' FALL=1")
    measure_block.append("* ==========================================\n")
    try:
        with open(target_file, 'r') as f:
            lines = f.readlines()
        new_lines = []
        inserted = False
        for line in lines:
            if line.strip().upper().startswith('.END'):
                new_lines.extend([l + '\n' for l in measure_block])
                new_lines.append(line)
                inserted = True
            else:
                new_lines.append(line)
        if not inserted:
            new_lines.extend([l + '\n' for l in measure_block])
            new_lines.append(".END\n")
        with open(target_file, 'w') as f:
            f.writelines(new_lines)
        log_message(f"  :( Injected .measure commands before .END")
    except Exception as e:
        log_message(f"  :( Error modifying file: {e}", is_error=True)
def process_cell(cellname):
    """Process a single cell and append to databook"""
    print(f"\nProcessing Cell: {cellname}")
    log_message(f"Processing Cell: {cellname}")
    run_magic_commands = "box\nextract all\next2spice hierarchy on\next2spice\nquit"
    run_magic_process = subprocess.Popen(
        ['magic', '-dnull', '-noconsole', '-T', 'tsmc180', cellname], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True
    )
    stdout, stderr = run_magic_process.communicate(input=run_magic_commands)
    log_message(f"Running ext2sp {cellname}...")
    try:
        subprocess.run(['ext2sp', '-f', cellname], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        log_message("  :D ext2sp execution successful")
    except subprocess.CalledProcessError as e:
        log_message(f"  :( ext2sp execution failed: {e}", is_error=True)
    except FileNotFoundError:
        log_message("  :( ext2sp command not found in path. Skipping.", is_error=True)
    if not os.path.exists(f"{cellname}.ext"):
        log_message(f"  :( CRITICAL: {cellname}.ext was not generated!", is_error=True)
    with open('databook.txt', 'a') as output_file:
        for line in stdout.split('\n'):
            if 'microns:' in line:
                parts = line.split()
                width = float(parts[1])
                height = float(parts[3])
                area = height * width
                log_message(f"Height x Width = {height} x {width}")
                log_message(f"Area = {area:.2f} sq. um")
                description = CELL_DESCRIPTIONS.get(cellname, "Standard Cell")
                output_file.write(f"Cell:     {cellname}\n")
                output_file.write(f"Function: {description}\n")
                output_file.write(f"Height:   {height:.2f} um\n")
                output_file.write(f"Width:    {width:.2f} um\n")
                output_file.write(f"Area:     {area:.2f} sq. um\n")
                output_file.write("-" * 40 + "\n")
                break
    log_message(f"\nFinished dimensions, check databook.txt :D")
    log_message("\nGetting port positions from .mag file...")
    mag_file = f'{cellname}.mag'
    port_positions_mag = []
    known_ports = {
        'D', 'Q', 'nQ', 'SDO', 'SDI', 'ScanReturn', 'Scan', 
        'Vdd!', 'GND!', 'nReset', 'Clock', 'Test', 
        'A', 'B', 'C', 'Y', 'M', 'I0', 'I1', 'S', 'Enable',
        'Cin', 'Cout', 'Load'
    }
    try:
        with open(mag_file, 'r') as f:
            mag_content = f.readlines()
        for line in mag_content:
            if line.startswith('rlabel'):
                parts = line.split()
                if len(parts) >= 8:
                    layer = parts[1]
                    x1_lambda = float(parts[2])
                    y1_lambda = float(parts[3])
                    x2_lambda = float(parts[4])
                    y2_lambda = float(parts[5])
                    port_name = parts[-1]
                    x_lambda = (x1_lambda + x2_lambda) / 2
                    y_lambda = (y1_lambda + y2_lambda) / 2
                    x_um = x_lambda / 50
                    y_um = y_lambda / 50
                    if port_name in known_ports:
                        port_key = f"{port_name}_{layer}"
                        port_exists = False
                        port_index = -1
                        for i, existing_port in enumerate(port_positions_mag):
                            if existing_port['name'] == port_name and existing_port['layer'] == layer:
                                port_exists = True
                                port_index = i
                                break
                        if port_exists:
                            should_replace = False
                            if layer == 'metal1' and x_um == 0.0:
                                should_replace = True
                            elif layer == 'metal2' and y_um == 0.0:
                                should_replace = True
                            if should_replace:
                                port_positions_mag[port_index] = {
                                    'name': port_name,
                                    'x': x_um,
                                    'y': y_um,
                                    'layer': layer
                                }
                                log_message(f"  {port_name}: ({x_um:.3f}, {y_um:.3f}) um on {layer} [updated]")
                        else:
                            port_positions_mag.append({
                                'name': port_name,
                                'x': x_um,
                                'y': y_um,
                                'layer': layer
                            })
                            log_message(f"  {port_name}: ({x_um:.3f}, {y_um:.3f}) um on {layer}")
        log_message(f"\nFound {len(port_positions_mag)} port positions in .mag file")
    except FileNotFoundError:
        log_message(f"Warning: Could not find {mag_file}", is_error=True)
    except Exception as e:
        log_message(f"Error parsing .mag file: {e}", is_error=True)
    ext_file = f'{cellname}.ext'
    existing_ports = []
    port_positions = []
    try:
        with open(ext_file, 'r') as f:
            ext_content = f.readlines()
        log_message("\nPort Parasitics:")
        for line in ext_content:
            line = line.strip()
            if line.startswith('node'):
                parts = line.split()
                if len(parts) >= 7:
                    port_name = parts[1].strip('"')
                    if port_name in known_ports:
                        resistance = parts[2]  
                        capacitance = parts[3]  
                        layer = parts[6]
                        try:
                            resistance_val = float(resistance)
                            capacitance_val = float(capacitance)
                            port_info = {
                                'name': port_name, 
                                'resistance': resistance_val, 
                                'capacitance': capacitance_val, 
                                'layer': layer
                            }
                            port_positions.append(port_info)
                            existing_ports.append(port_name)
                            log_message(f"  {port_name}: R={resistance_val:.2f} ohm, C={capacitance_val:.3f} fF (on {layer})")
                        except ValueError:
                            log_message(f"  Could not parse parasitics for {port_name}", is_error=True)
        log_message(f"\nDetected Ports: {existing_ports}")
        input_ports, output_ports, power_ports, passthrough_ports = get_port_categories(cellname, existing_ports)
        cell_supported = bool(input_ports or output_ports or power_ports or passthrough_ports)
        if not cell_supported:
            log_message(f"\n:( Cell '{cellname}' not supported - skipping port categorization", is_error=True)
        else:
            log_message(f"\nPort Categories:")
            log_message(f"  Input: {input_ports}")
            log_message(f"  Output: {output_ports}")
            log_message(f"  Power: {power_ports}")
            log_message(f"  Passthrough: {passthrough_ports}")
            log_message(f"\n--- Generating Input Capacitance Testbenches ---")
            base_cellname = cellname if cellname in PORT_DIRECTIONS else cellname.rstrip('0123456789')
            cap_measurements = {}  
            for input_pin in input_ports:
                log_message(f"\n  Processing input: {input_pin}")
                sp_file = generate_input_cap_spice(
                    cellname, input_pin, input_ports, output_ports, base_cellname
                )
                if sp_file:
                    log_message(f"    Running HSPICE on {sp_file}...")
                    success, mt0_file = run_hspice(sp_file)
                    if success and mt0_file:
                        log_message(f"    :D HSPICE completed: {mt0_file}")
                        measurements = parse_mt0_file(mt0_file)
                        if measurements:
                            cap_measurements[input_pin] = measurements
                            if 'capacitance_fF' in measurements:
                                log_message(f"    :D Input capacitance: {measurements['capacitance_fF']:.4f} fF")
                        else:
                            log_message(f"    :( Could not parse measurements from {mt0_file}", is_error=True)
                    else:
                        log_message(f"    :( HSPICE failed for {sp_file}", is_error=True)
            log_message(f"\n--- Generating Propagation Delay Testbench ---")
            pd_measurements = {}  
            pd_sp_file = generate_propagation_delay_spice(
                cellname, input_ports, output_ports, base_cellname
            )
            if pd_sp_file:
                log_message(f"  Running HSPICE on {pd_sp_file}...")
                success, mt0_file = run_hspice(pd_sp_file)
                if success and mt0_file:
                    log_message(f"  :D HSPICE completed: {mt0_file}")
                    pd_measurements = parse_propagation_delay_mt0(mt0_file, cellname, base_cellname)
                    if pd_measurements:
                        log_message(f"  :D Extracted {len(pd_measurements)} propagation delay measurements")
                        for meas_name, value in pd_measurements.items():
                            log_message(f"    {meas_name}: {value:.4f} ns")
                    else:
                        log_message(f"  :( Could not parse propagation delays from {mt0_file}", is_error=True)
                else:
                    log_message(f"  :( HSPICE failed for {pd_sp_file}", is_error=True)
        with open('databook.txt', 'a') as output_file:
            output_file.write(f"Detected Ports: {', '.join(existing_ports)}\n")
            if cell_supported:
                output_file.write(f"\nPort Categorization:\n")
                output_file.write(f"  {'Category':<20} {'Ports':<50}\n")
                output_file.write(f"  {'-'*20} {'-'*51}\n")
                output_file.write(f"  {'Input':<20} {', '.join(input_ports) if input_ports else 'None':<50}\n")
                output_file.write(f"  {'Output':<20} {', '.join(output_ports) if output_ports else 'None':<50}\n")
                output_file.write(f"  {'Power':<20} {', '.join(power_ports) if power_ports else 'None':<50}\n")
                output_file.write(f"  {'Passthrough':<20} {', '.join(passthrough_ports) if passthrough_ports else 'None':<50}\n")
            else:
                output_file.write(f"\nCell not supported\n")
            output_file.write(f"\nPort Parasitics:\n")
            output_file.write(f"  {'Port Name':<20} {'Resistance (ohm)':<25} {'Capacitance (fF)':<25}\n")
            output_file.write(f"  {'-'*20} {'-'*25} {'-'*25}\n")
            for port in port_positions:
                output_file.write(f"  {port['name']:<20} {port['resistance']:<25.2f} {port['capacitance']:<25.3f}\n")
            if cell_supported and cap_measurements:
                output_file.write(f"\nInput Capacitance Measurements (HSPICE):\n")
                output_file.write(f"  {'Input Pin':<20} {'Capacitance (fF)':<25}\n")
                output_file.write(f"  {'-'*20} {'-'*51}\n")
                for pin, measurements in cap_measurements.items():
                    if 'capacitance_fF' in measurements:
                        output_file.write(f"  {pin:<20} {measurements['capacitance_fF']:<25.4f}\n")
            if cell_supported and pd_measurements:
                output_file.write(f"\nPropagation Delay Measurements (HSPICE):\n")
                output_file.write(f"  {'Path':<30} {'Rising (ns)':<20} {'Falling (ns)':<20}\n")
                output_file.write(f"  {'-'*30} {'-'*20} {'-'*20}\n")
                paths_dict = {}
                for meas_name, value in pd_measurements.items():
                    parts = meas_name.split('_')
                    if len(parts) >= 4:
                        direction = parts[-1]  
                        output_pin = parts[-2]
                        input_pin = '_'.join(parts[1:-2])  
                        path_name = f"{input_pin} -> {output_pin}"
                        if path_name not in paths_dict:
                            paths_dict[path_name] = {'rising': None, 'falling': None}
                        if direction == 'r':
                            paths_dict[path_name]['rising'] = value
                        elif direction == 'f':
                            paths_dict[path_name]['falling'] = value
                    elif len(parts) == 3 and parts[0] == 'tcq':
                        direction = parts[-1]
                        input_mode = parts[1]
                        path_name = f"Clk -> Q ({input_mode})"
                        if path_name not in paths_dict:
                            paths_dict[path_name] = {'rising': None, 'falling': None}
                        if direction == 'r':
                            paths_dict[path_name]['rising'] = value
                        elif direction == 'f':
                            paths_dict[path_name]['falling'] = value
                for path_name, delays in paths_dict.items():
                    if delays['rising'] is None and delays['falling'] is None:
                        continue
                    rising_str = f"{delays['rising']:.4f}" if delays['rising'] is not None else "-"
                    falling_str = f"{delays['falling']:.4f}" if delays['falling'] is not None else "-"
                    output_file.write(f"  {path_name:<30} {rising_str:<20} {falling_str:<20}\n")
            output_file.write(f"\nPort Positions:\n")
            output_file.write(f"  {'Port Name':<20} {'X (um)':<25} {'Y (um)':<25}\n")
            output_file.write(f"  {'-'*20} {'-'*25} {'-'*25}\n")
            port_layer_count = {}
            for port in port_positions_mag:
                if port['name'] not in ['Vdd!', 'GND!']:
                    port_layer_count[port['name']] = port_layer_count.get(port['name'], 0) + 1
            for port in port_positions_mag:
                if port['name'] not in ['Vdd!', 'GND!']:  
                    if port_layer_count[port['name']] > 1:
                        layer_suffix = ' (m1)' if port['layer'] == 'metal1' else ' (m2)'
                        port_display_name = port['name'] + layer_suffix
                    else:
                        port_display_name = port['name']
                    output_file.write(f"  {port_display_name:<20} {port['x']:<25.3f} {port['y']:<25.3f}\n")
            output_file.write("\n" + "="*75 + "\n\n")
        log_message("\nFinished! Check databook.txt")
    except FileNotFoundError:
        log_message(f"Error: Could not find {ext_file}", is_error=True)
    except Exception as e:
        log_message(f"Error: {e}", is_error=True)
def process_extended_cell(cellname):
    """Process a cell for extended databook - get basic info, parasitics, and positions only"""
    print(f"\nProcessing Extended Cell: {cellname}")
    log_message(f"Processing Extended Cell: {cellname}")
    run_magic_commands = "box\nextract all\next2spice\nquit"
    run_magic_process = subprocess.Popen(
        ['magic', '-dnull', '-noconsole', '-T', 'tsmc180', cellname], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True
    )
    stdout, stderr = run_magic_process.communicate(input=run_magic_commands)
    log_message(f"Running ext2sp {cellname}...")
    try:
        subprocess.run(['ext2sp', '-f', cellname], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        log_message("  :D ext2sp execution successful")
    except subprocess.CalledProcessError as e:
        log_message(f"  :( ext2sp execution failed: {e}", is_error=True)
    except FileNotFoundError:
        print("  :( ext2sp command not found in path. Skipping.")
    width = height = area = None
    for line in stdout.split('\n'):
        if 'microns:' in line:
            parts = line.split()
            width = float(parts[1])
            height = float(parts[3])
            area = height * width
            break
    ext_file = f'{cellname}.ext'
    known_ports = {
        'D', 'Q', 'nQ', 'SDO', 'SDI', 'ScanReturn', 'Scan', 
        'Vdd!', 'GND!', 'nReset', 'Clock', 'Test', 
        'A', 'B', 'C', 'Y', 'M', 'I0', 'I1', 'S', 'Enable',
        'Cin', 'Cout', 'Load'
    }
    existing_ports = []
    port_positions = []
    try:
        with open(ext_file, 'r') as f:
            ext_content = f.readlines()
        for line in ext_content:
            line = line.strip()
            if line.startswith('node'):
                parts = line.split()
                if len(parts) >= 7:
                    port_name = parts[1].strip('"')
                    if port_name in known_ports:
                        resistance = parts[2]
                        capacitance = parts[3]
                        layer = parts[6]
                        try:
                            resistance_val = float(resistance)
                            capacitance_val = float(capacitance)
                            port_info = {
                                'name': port_name, 
                                'resistance': resistance_val, 
                                'capacitance': capacitance_val, 
                                'layer': layer
                            }
                            port_positions.append(port_info)
                            existing_ports.append(port_name)
                        except ValueError:
                            pass
    except FileNotFoundError:
        pass
    mag_file = f'{cellname}.mag'
    port_positions_mag = []
    try:
        with open(mag_file, 'r') as f:
            mag_content = f.readlines()
        for line in mag_content:
            if line.startswith('rlabel'):
                parts = line.split()
                if len(parts) >= 8:
                    layer = parts[1]
                    x1_lambda = float(parts[2])
                    y1_lambda = float(parts[3])
                    x2_lambda = float(parts[4])
                    y2_lambda = float(parts[5])
                    port_name = parts[-1]
                    x_lambda = (x1_lambda + x2_lambda) / 2
                    y_lambda = (y1_lambda + y2_lambda) / 2
                    x_um = x_lambda / 50
                    y_um = y_lambda / 50
                    if port_name in known_ports:
                        port_exists = False
                        port_index = -1
                        for i, existing_port in enumerate(port_positions_mag):
                            if existing_port['name'] == port_name and existing_port['layer'] == layer:
                                port_exists = True
                                port_index = i
                                break
                        if port_exists:
                            should_replace = False
                            if layer == 'metal1' and x_um == 0.0:
                                should_replace = True
                            elif layer == 'metal2' and y_um == 0.0:
                                should_replace = True
                            if should_replace:
                                port_positions_mag[port_index] = {
                                    'name': port_name,
                                    'x': x_um,
                                    'y': y_um,
                                    'layer': layer
                                }
                        else:
                            port_positions_mag.append({
                                'name': port_name,
                                'x': x_um,
                                'y': y_um,
                                'layer': layer
                            })
    except FileNotFoundError:
        pass
    base_cellname = cellname if cellname in PORT_DIRECTIONS else cellname.rstrip('0123456789')
    with open('extended_databook.txt', 'a') as f:
        f.write(f"Cell: {cellname}\n")
        f.write(f"Reason: Extended databook cell (not in main databook list)\n\n")
        if width and height and area:
            f.write(f"Height:   {height:.2f} um\n")
            f.write(f"Width:    {width:.2f} um\n")
            f.write(f"Area:     {area:.2f} sq. um\n\n")
        if existing_ports:
            f.write(f"Detected Ports: {', '.join(existing_ports)}\n")
        if port_positions:
            f.write(f"\nPort Parasitics:\n")
            f.write(f"  {'Port Name':<20} {'Resistance (ohm)':<25} {'Capacitance (fF)':<25}\n")
            f.write(f"  {'-'*20} {'-'*25} {'-'*25}\n")
            for port in port_positions:
                f.write(f"  {port['name']:<20} {port['resistance']:<25.2f} {port['capacitance']:<25.3f}\n")
        if port_positions_mag:
            f.write(f"\nPort Positions:\n")
            f.write(f"  {'Port Name':<20} {'X (um)':<25} {'Y (um)':<25}\n")
            f.write(f"  {'-'*20} {'-'*25} {'-'*25}\n")
            port_layer_count = {}
            for port in port_positions_mag:
                if port['name'] not in ['Vdd!', 'GND!']:
                    port_layer_count[port['name']] = port_layer_count.get(port['name'], 0) + 1
            for port in port_positions_mag:
                if port['name'] not in ['Vdd!', 'GND!']:
                    if port_layer_count[port['name']] > 1:
                        layer_suffix = ' (m1)' if port['layer'] == 'metal1' else ' (m2)'
                        port_display_name = port['name'] + layer_suffix
                    else:
                        port_display_name = port['name']
                    f.write(f"  {port_display_name:<20} {port['x']:<25.3f} {port['y']:<25.3f}\n")
        f.write("\n" + "="*75 + "\n\n")
def main():
    """Main function - process all .mag files in current directory"""
    clean_generated_files()
    mag_files = []
    for filename in os.listdir('.'):
        if filename.endswith('.mag'):
            mag_files.append(filename[:-4])  
    if not mag_files:
        print("Error: No .mag files found in current directory")
        sys.exit(1)
    mag_files.sort()  
    print(f"Found {len(mag_files)} .mag files:")
    for mag_file in mag_files:
        print(f"  - {mag_file}")
    with open('databook.txt', 'w') as f:
        f.write("CELL LIBRARY DATABOOK\n")
        f.write("="*60 + "\n\n")
    with open('extended_databook.txt', 'w') as f:
        f.write("EXTENDED DATABOOK\n")
        f.write("="*60 + "\n\n")
    successful = 0
    failed = 0
    unsupported = 0
    for cellname in mag_files:
        try:
            if cellname in PORT_DIRECTIONS:
                base_cellname = cellname
            else:
                base_cellname = cellname.rstrip('0123456789')
            if base_cellname not in MAIN_DATABOOK_CELLS:
                print(f"\n:( Moving to extended databook: {cellname}")
                unsupported += 1
                try:
                    process_extended_cell(cellname)
                except Exception as e:
                    print(f"  Error getting info for extended cell: {e}")
                    with open('extended_databook.txt', 'a') as f:
                        f.write(f"Cell: {cellname}\n")
                        f.write(f"Reason: Extended databook cell (not in main databook list)\n")
                        f.write(f"Error: {e}\n")
                        f.write("="*60 + "\n\n")
                continue
            if base_cellname not in PORT_DIRECTIONS:
                print(f"\n:( Error: Cell '{cellname}' is in main databook list but missing PORT_DIRECTIONS")
                failed += 1
                with open('extended_databook.txt', 'a') as f:
                    f.write(f"Cell: {cellname}\n")
                    f.write(f"Reason: Missing PORT_DIRECTIONS configuration\n")
                    f.write("="*60 + "\n\n")
                continue
            process_cell(cellname)
            successful += 1
        except Exception as e:
            print(f"\n:( Error processing {cellname}: {e}")
            failed += 1
            with open('extended_databook.txt', 'a') as f:
                f.write(f"Cell: {cellname}\n")
                f.write(f"Reason: Processing error - {e}\n")
                f.write("="*60 + "\n\n")
    with open('databook.txt', 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("END OF DATABOOK\n")
        f.write("="*60 + "\n")
        if unsupported > 0:
            f.write(f"\nNote: {unsupported} cell(s) moved to extended databook.\n")
            f.write("See 'extended_databook.txt' for details.\n")
    print(f"\n{'='*60}")
    print(f"DATABOOK GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully processed: {successful}/{len(mag_files)} cells")
    if unsupported > 0:
        print(f"Extended databook cells: {unsupported}/{len(mag_files)} cells")
        print(f"  -> See extended_databook.txt for details")
    if failed > 0:
        print(f"Failed: {failed}/{len(mag_files)} cells")
    print(f"\nDatabook saved to: databook.txt")
if __name__ == '__main__':
    main()