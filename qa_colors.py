import re
import tkinter as tk
from time import sleep


# functions
def HexToRGB(Hex, vb=True):
    rgb = tuple(int("".join(i for i in re.findall("\w", Hex))[i:i + 2], 16) for i in (0, 2, 4))
    if vb: print("HexToRGB : ", Hex, " >> ", rgb, "dh=", RGBToHex(rgb, False))
    return rgb


def RGBToInt(rgb: tuple, vb=True) -> int:
    n = rgb[0] << 16 | rgb[1] << 8 | rgb[2]

    if vb: print("RGBToInt : ", rgb, " >> ", n, "dh=", IntToHex(n, False))

    return n


def IntToRGB(IRGB, vb=True) -> tuple:
    rgb: tuple = (IRGB // 256 // 256 % 256, IRGB // 256 % 256, IRGB % 256)

    if vb: print("IntToRGB : ", IRGB, " >> ", rgb, "dh=", RGBToHex(rgb, False))
    return rgb


def RGBToHex(RGB: tuple, vb=True):
    Hex = "#%02x%02x%02x" % RGB

    if vb: print("RGBToHex : ", RGB, " >> ", Hex, "dh=", (Hex))

    return Hex


def HexToInt(Hex, vb=True):
    Hex = "".join(i for i in re.findall("\w", Hex))
    Int = RGBToInt(HexToRGB(Hex))

    if vb: print("HexToInt : ", Hex, " >> ", Int, "dh=", IntToHex(Int, False))

    return Int


def IntToHex(Int, vb=True):
    Int = int("".join(i for i in re.findall("\d", str(Int))))
    Hex = RGBToHex(IntToRGB(Int))

    if vb: print("IntToHex : ", Int, " >> ", Hex, "dh=", Hex)

    return Hex


# def sampleColor(colr, uHex, uRGB, uInt):
#     if uHex:
#         colr = "#" + "".join(i for i in re.findall("\w", colr))
#
#     disp = tk.Tk()
#     disp.config(bg=colr if uHex else (RGBToHex(colr) if uRGB else (RGBToHext(IntToRGB(colr)) if uInt else "#000000")))
#     disp.geometry("400x400")
#     disp.protocol("WM_DELETE_WINDOW", lambda: disp.after(0, disp.destroy))
#     disp.title(colr if uHex or uRGB or uInt else "None")
#     tk.Label(disp, text=colr if uHex or uRGB or uInt else "None").pack(fill=tk.X, expand=True)
#     disp.mainloop()


# def sampleAll(Hex):
#     Hex = "#" + "".join(i for i in re.findall("\w", Hex))
#
#     disp = tk.Tk()
#     disp.title(Hex)
#     disp.protocol("WM_DELETE_WINDOW", disp.destroy)
#     disp.geometry("600x400")
#
#     print("\n\n\n\n Producing Hex Value")
#     h = Hex.strip()
#
#     print("\n\n\n\n Producing RGB Value")
#     rgb = RGBToHex(HexToRGB(Hex)).strip()
#
#     print("\n\n\n\n Producing Integer Value")
#     i = IntToHex(HexToInt(Hex)).strip()
#
#     print("\n\n", h, type(h), " = ", rgb, type(rgb), ' = ', i, type(i))
#
#     print("\n\nComplete Converstions...\n\n")
#
#     f1 = tk.Frame(disp);
#     f2 = tk.Frame(disp);
#     f3 = tk.Frame(disp)
#     f1.config(background=h)
#     f1.pack(fill=tk.BOTH, expand=True)  # , pady=(0, 5))
#
#     f2.config(background=rgb)
#     f2.pack(fill=tk.BOTH, expand=True)  # , pady=5)
#
#     f3.config(background=i)
#     f3.pack(fill=tk.BOTH, expand=True)  # , pady=(5, 0))
#
#     # Hex
#     tk.Label(f1, text="Hex\n{}".format(
#         Hex
#     )).pack(fill=tk.X, expand=True, padx=5)
#
#     # RGB
#     tk.Label(f2, text="Hex > RGB > Hex\n{}".format(
#         HexToRGB(Hex)
#     )).pack(fill=tk.X, expand=True, padx=5)
#
#     # Int
#     tk.Label(f3, text="Hex > RGB > Int > RGB > Hex\n{}".format(
#         HexToInt(Hex)
#     )).pack(fill=tk.X, expand=True, padx=5)
#
#     disp.mainloop()


# def sampleMonoFade(start, end, rF, gF, bF, infi=False, interval=0.1):
#     start = HexToInt("#" + "".join(i for i in re.findall("\w", start)));
#     stOg = start
#     end = HexToInt("#" + "".join(i for i in re.findall("\w", end)))
#
#     disp = tk.Tk()
#     disp.title("Fade")
#     disp.protocol("WM_DELETE_WINDOW", disp.destroy)
#     disp.geometry("600x400")
#
#     print(
#         "\n\n\nValues (Int):\nStart: ", start, "\nEnd: ", end, "\n\n\n"
#     )
#
#     while True:
#         if start == end: break
#
#         start += int(rF) << 16 | int(gF) << 8 | int(bF)
#         disp.config(bg=IntToHex(start))
#         disp.title(IntToHex(start))
#
#         if not infi and (((start >= end) and stOg < end) or ((start <= end) and stOg > end)): break
#
#         if interval is not None: sleep(interval)
#         disp.update_ui()


def monoFade(start, end, rF, gF, bF, inHex=True):
    start = HexToInt("#" + "".join(i for i in re.findall("\w", start)));
    stOg = start
    end = HexToInt("#" + "".join(i for i in re.findall("\w", end)))

    print(
        "\n\n\nValues (Int):\nStart: ", start, "\nEnd: ", end, "\n\n\n"
    )

    out: list = []
    while True:
        if start == end: break
        start += int(rF) << 16 | int(gF) << 8 | int(bF)
        out.append(start if not inHex else IntToHex(start))
        if ((start >= end) and stOg < end) or ((start <= end) and stOg > end): break

    return out
