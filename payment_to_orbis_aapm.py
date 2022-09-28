import pyautogui
import time
import csv
import pprint
bereits_erfasste_zahlungen = []


def csv_to_dict(csv_file: str) -> dict:
    with open(csv_file, "r", encoding="utf-8-SIG") as _csv_file:
        reader = csv.DictReader(_csv_file, delimiter=";")
        _dict = {}
        for row in reader:
            _dict[row['Rechnungsnummer']] = {'Umsatz': row['Umsatz'], 'Buchungstag': row['Buchungstag']}
        return _dict



def start_aapm() -> None:
    w = pyautogui.getWindowsWithTitle("ORBIS AZH")
    w[0].activate()
    w[0].maximize()
    time.sleep(1)
    aapm_button = pyautogui.locateCenterOnScreen("aapm.png")
    pyautogui.click(aapm_button)
    time.sleep(1)
    pyautogui.write(['enter'], 0.25)
    while True:
        if len(pyautogui.getWindowsWithTitle("Rechnungssteller suchen")) > 0:
            break
    time.sleep(1.5)


def choose_privat() -> None:
    pyautogui.write(["GP Radiologie privat", "enter"], 0.1)


def choose_westerstadion() -> None:
    pyautogui.write(["Radiologie am Weserstadion", "enter"], 0.1)


def aapm_open():
    if len(pyautogui.getWindowsWithTitle("ORBIS-AAPM")) > 0:
        return True
    else:
        return False


def zahlung_erfassen_open() -> bool:
    if len(pyautogui.getWindowsWithTitle("Zahlungen erfassen")) > 0:
        w = pyautogui.getWindowsWithTitle("Zahlungen erfassen")[0].activate()
        pyautogui.hotkey("esc")
        open_zahlung_erfassen()
        return True
    else:
        return False


def open_zahlung_erfassen() -> None:
    w = pyautogui.getWindowsWithTitle("ORBIS-AAPM")
    w[0].activate()
    pyautogui.keyDown("alt")
    pyautogui.write("goz", 0.1)
    pyautogui.keyUp("alt")


def produces_error() -> bool:
    _w = pyautogui.getWindowsWithTitle("Orbis-Meldung")
    if len(_w) > 0:
        pyautogui.write(["enter", "enter"], 0.25)
        return True
    else:
        return False


def exit_aapm():
    w = pyautogui.getWindowsWithTitle("ORBIS-AAPM")
    w[0].activate()
    pyautogui.hotkey("alt", "F4")
    pyautogui.hotkey("enter")


def write_zahlung(rechnungsnummer: str):
    pyautogui.write(rechnungsnummer)
    pyautogui.hotkey("tab")
    if produces_error():
        bereits_erfasste_zahlungen.append(rechnungsnummer)
        return
    # Jump to "Neu"
    for i in range(0,4):
        pyautogui.hotkey("tab")
    pyautogui.hotkey("enter")
    # Write Buchungsdatum
    pyautogui.write("27092022")
    pyautogui.hotkey("tab")
    # Write Bezahlsumme
    pyautogui.write("221,60")
    # Jump to "Speichern"
    for i in range(0,6):
        pyautogui.hotkey("tab")
    pyautogui.hotkey("enter")
    # Jump to "OK"
    pyautogui.hotkey("tab")
    pyautogui.hotkey("enter")

    
def main():
    if not aapm_open():
        start_aapm()
        choose_privat()

    if not zahlung_erfassen_open():
        open_zahlung_erfassen()


    write_zahlung("90105495")


if __name__ == "__main__":
    pprint.pprint(csv_to_dict("28.09.2022_datev_export.csv"))