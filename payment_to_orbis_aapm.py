from importlib.resources import path
import pyautogui
import time
import csv
from PyInquirer import prompt
from examples import custom_style_3
import pathlib
import os
import traceback
import readchar

pyautogui.FAILSAFE = True
bereits_erfasste_zahlungen = []
rechnungsnummer_nicht_gefunden = []
csv_folder = pathlib.Path.cwd() / "Ergebnisse"
script_folder = pathlib.Path(__file__).parent
pyinquirer_questions = [{"type": "list",
                         "name": "user_input",
                         "message": "Bitte auswählen",
                         "choices": [str(file_path.absolute()) for file_path in pathlib.Path(csv_folder).glob('**/*.[cC][sS][vV]')]}]


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
    aapm_button = pyautogui.locateCenterOnScreen(str(script_folder / "aapm.png"))
    pyautogui.click(aapm_button)
    time.sleep(1)
    pyautogui.hotkey('enter')
    while True:
        if len(pyautogui.getWindowsWithTitle("Rechnungssteller suchen")) > 0:
            break
    time.sleep(1.5)


def choose_privat() -> None:
    pyautogui.write("GP Radiologie privat")
    pyautogui.hotkey("enter")


def choose_weserstadion() -> None:
    pyautogui.write("Radiologie am Weserstadion")
    pyautogui.hotkey("enter")

def is_weserstadion_aapm() -> bool:
    if len(pyautogui.getWindowsWithTitle("ORBIS-AAPM [AZH]  (AZ-BS) Radiologie am Weserstadion(MVZ-Sportmedizin am Weserstadion)")) > 0:
        return True
    else:
        return False

def aapm_open() -> bool:
    if len(pyautogui.getWindowsWithTitle("ORBIS-AAPM")) > 0:
        return True
    else:
        return False


def orbis_open() -> bool:
    if len(pyautogui.getWindowsWithTitle("ORBIS AZH")) > 0:
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
    pyautogui.sleep(0.1)
    pyautogui.write("goz", 0.2)
    pyautogui.keyUp("alt")


def produces_error() -> bool:
    _w = pyautogui.getWindowsWithTitle("Orbis-Meldung")
    if len(_w) > 0:
        pyautogui.write(["enter", "enter"], 0.25)
        return True
    else:
        return False


def exit_aapm() -> None:
    w = pyautogui.getWindowsWithTitle("ORBIS-AAPM")
    w[0].activate()
    pyautogui.hotkey("alt", "F4")
    pyautogui.hotkey("enter")


def write_zahlung(rechnungsnummer: str, data: dict) -> None:
    print(f"Schreibe {rechnungsnummer}. Buchung vom {data['Buchungstag']} über {data['Umsatz']}.")
    pyautogui.write(rechnungsnummer)
    pyautogui.hotkey("tab")
    if produces_error():
        rechnungsnummer_nicht_gefunden.append(rechnungsnummer)
        pyautogui.hotkey('esc')
        return
    # Jump to "Neu"
    for i in range(0, 4):
        pyautogui.hotkey("tab")
    pyautogui.hotkey("enter")
    # Write Buchungsdatum
    pyautogui.write(data['Buchungstag'])
    pyautogui.hotkey("tab")
    # Write Bezahlsumme
    pyautogui.write(data['Umsatz'])
    # Jump to "Speichern"
    for i in range(0, 6):
        if produces_error():
            bereits_erfasste_zahlungen.append(rechnungsnummer)
            pyautogui.hotkey('esc')
            return
        pyautogui.hotkey("tab")
    pyautogui.hotkey("enter")
    # Jump to "OK"
    pyautogui.hotkey("tab")
    pyautogui.hotkey("enter")

    
def main():
    if not orbis_open():
        print("Bitte Orbis starten, einloggen und dann das Skript nochmal starten.")
        exit(1)

    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    answers = prompt(questions=pyinquirer_questions, style=custom_style_3)
    choice = answers.get('user_input')

    if aapm_open and is_weserstadion_aapm():
        exit_aapm()
    
    if not aapm_open():
        start_aapm()
        choose_privat()
   
    working_dict = csv_to_dict(choice)
    for rechnungsnummer, data in working_dict.items():
        if rechnungsnummer.startswith("9"):
            if not zahlung_erfassen_open():
                open_zahlung_erfassen()
            write_zahlung(rechnungsnummer=rechnungsnummer, data=data)
    
    exit_aapm()

    if not aapm_open():
        start_aapm()
        pyautogui.sleep(2)
        choose_weserstadion()
        pyautogui.sleep(2)

    working_dict = csv_to_dict(choice)
    for rechnungsnummer, data in working_dict.items():
        if rechnungsnummer.startswith("7"):
            if not zahlung_erfassen_open():
                open_zahlung_erfassen()
            write_zahlung(rechnungsnummer=rechnungsnummer, data=data)
    
    exit_aapm()

    print(f"Folgende Rechnungsnummer waren bereits gebucht: {bereits_erfasste_zahlungen}")
    print(f"Folgende Rechnungsnummer wurden nicht gefunden: {rechnungsnummer_nicht_gefunden}")


if __name__ == "__main__":
    try:
        main()
    except:
        print(traceback.format_exc())
    finally:
        print("Drücke eine beliebige Taste um das Programm zu beenden...")
        k = readchar.readchar()

