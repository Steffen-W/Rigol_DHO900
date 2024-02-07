import vxi11  # pip install python-vxi11
import numpy as np
import matplotlib.pyplot as plt
import usbtmc  # pip install usbtmc

from Rigol_DHO900 import connection_ip, connection_usb, DHO900

def main():

    # for usb connection
    vendor_id = 0x1AB1
    product_id = 0x044C
    instrument = connection_usb(vendor_id, product_id)
    print(instrument.get_identification())

    # for ethernet connection
    ip_rigol = "192.168.178.32"
    instrument = connection_ip(ip_rigol)
    print(instrument.get_identification())

    Rigol = DHO900(instrument)
    print(Rigol.conn.ask(":ACQuire:MDEPth?"))

    print(Rigol.conn.ask(":ACQuire:MDEPth?"))
    print("CHANnel1:DISPlay", Rigol.conn.ask(":CHANnel1:DISPlay?"))
    print("CHANnel2:DISPlay", Rigol.conn.ask(":CHANnel2:DISPlay?"))

    setting_CH1 = Rigol.read_chanel_setting(1)
    setting_CH2 = Rigol.read_chanel_setting(2)

    Rigol.conn.write(":STOP")

    points_CH2_raw = Rigol.convert_raw(Rigol.read_chanel_raw(2), setting_CH2)

    points_CH1 = Rigol.read_chanel(1)
    points_CH2 = Rigol.read_chanel(2)

    Rigol.conn.write(":RUN")

    # Plot data points

    for i in range(10):
        Rigol.read_chanel(1)
    print(Rigol.conn.ask(":SYSTem:ERRor?"))
    print(Rigol.conn.ask("*STB?"))
    Rigol.conn.close()

    fig, ax = plt.subplots()
    ax.plot(points_CH1, label="CH1")
    ax.plot(points_CH2, label="CH2")
    ax.plot(points_CH2_raw, label="CH2 RAW")

    ax.set(xlabel="Sample", ylabel="Voltage / V", title="Rigol_DHO900 Plot")
    ax.grid()
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
