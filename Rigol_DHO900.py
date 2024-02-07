import vxi11  # pip install python-vxi11
import numpy as np
import matplotlib.pyplot as plt
import usbtmc  # pip install usbtmc


class connection_ip(vxi11.Instrument):
    def __init__(self, host, *args, **kwargs):
        super(connection_ip, self).__init__(host, *args, **kwargs)

    def get_identification(self):
        return self.ask("*IDN?")

    def __del__(self):
        self.close()
        
class connection_usb(usbtmc.Instrument):
    def __init__(self, vendor_id, product_id, *args, **kwargs):
        super(connection_usb, self).__init__(vendor_id, product_id, *args, **kwargs)

    def get_identification(self):
        return self.ask("*IDN?")

    def __del__(self):
        self.close()


class DHO900:
    """Class to control a Rigol DHO900 (DHO924S,DHO924 DHO914S, DHO914) oscilloscope"""

    def __init__(self, connection):
        self.conn = connection
        self.name = self.conn.ask("*IDN?")
        if self.name:
            print(self.name)
        else:
            raise ValueError("Connection error")
        print(self.conn.ask("*STB?"))
        print(self.conn.ask(":SYSTem:ERRor?"))

    def read_chanel_setting(self, chanel="1"):
        self.conn.write(":WAVeform:SOURce CHAN" + str(chanel))
        c = {}
        PREamble = str(self.conn.ask(":WAVeform:PREamble?")).split(",")
        # indicates 0 (BYTE), 1 (WORD), or 2 (ASC).
        c["format"] = int(PREamble[0])
        # indicates 0 (NORMal), 1 (MAXimum), or 2 (RAW).
        c["type"] = int(PREamble[1])
        # an integer ranging from 1 to 50,000,000.
        c["points"] = int(PREamble[2])
        # indicates the number of averages in the average sample mode
        c["count"] = int(PREamble[3])
        # indicates the time difference between two neighboring points in theX direction.
        c["xdeltra"] = float(PREamble[4])
        # indicates the start time of the waveform data in the X direction.
        c["xorigin"] = float(PREamble[5])
        # indicates the reference time of the waveform data in the X direction.
        c["xreference"] = float(PREamble[6])
        # indicates the step value of the waveforms in the Y direction.
        c["ydeltra"] = float(PREamble[7])
        # indicates the vertical offset relative to the "Vertical Reference Position" in the Y direction.
        c["yorigin"] = float(PREamble[8])
        # indicates the vertical reference position in the Y direction.
        c["yreference"] = float(PREamble[9])
        c["DISPlay"] = self.conn.ask(":CHANnel" + str(chanel) + ":DISPlay?")
        c["OFFSet"] = self.conn.ask(":CHANnel" + str(chanel) + ":OFFSet?")
        c["SCALe"] = self.conn.ask(":CHANnel" + str(chanel) + ":SCALe?")
        c["PROBe"] = self.conn.ask(":CHANnel" + str(chanel) + ":PROBe?")
        c["LABel"] = self.conn.ask(":CHANnel" + str(chanel) + ":LABel:CONTent?")
        return c

    def read_chanel(self, chanel="1"):
        self.conn.write(":WAVeform:SOURce CHAN" + str(chanel))
        self.conn.write(":WAVeform:FORMat ASCii")
        # print(self.conn.ask(":WAVeform:POINts?"))
        points = str(self.conn.ask(":WAVeform:DATA?")).split(",")
        return np.array(points, dtype=float)

    def read_chanel_raw(self, chanel="1"):
        self.conn.write(":WAVeform:SOURce CHAN" + str(chanel))
        self.conn.write(":WAVeform:FORMat WORD")
        # self.conn.write(":WAV:STAR 1")
        # self.conn.write(":WAV:STOP 10000")
        stop = int(self.conn.ask(":WAVeform:STOP?"))
        self.conn.write(":WAVeform:DATA?")
        header = self.conn.read_raw(11)
        # print(header)
        # NumberHeader = header[1]
        data = self.conn.read_raw(stop * 2)
        return np.frombuffer(data, dtype=np.uint16)

    def convert_raw(self, raw_data, settings):
        c = settings
        return (raw_data - c["yorigin"] - c["yreference"]) * c["ydeltra"]

    def __del__(self):
        self.conn.close()