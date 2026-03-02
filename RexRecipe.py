# Meowy - https://github.com/LawnMeower64
# 2/2/2026
# Python 3.13
#
# Random project I made during my free time to see my progress on a Rex:R recipe.
# Please note I don't even play Rex:R that much I just find coding fun.
# I'm not an expert on python so if you have any feedback I'd like to hear it. I am
# more specialized on Java and C, but I found it interesting to code on Python.
#
# This project is dependant off a github library called easyocr: https://github.com/JaidedAI/EasyOCR
#
# To run this program, make sure to select Python 3.13 as your interpreter.
# You can install easyocr through this command:
# > pip install easyocr
#
# Other note:
# I did use AI at some point to figure out what libraries i need and how to use them, but I handwrote my code.
# AI is a tool, not a magic feature that can create all the scripts you can think off.


import tkinter as tk
from typing import Callable, Optional
from PIL import ImageGrab, Image
from pathlib import Path
import shutil
import easyocr as ocr
import os

cache = Path("CACHE")
cache.mkdir(exist_ok = True)

root = tk.Tk()

_ocrReader = None

# getReader()
#
# if the reader is not initialized then it creates one then returns the reader
#
# input: none
# output: the reader (just created or already created)
#
# note: sorry for the use of global I've heard its bad practice, but I couldn't be asked
#       to make this script too seriously.
def getReader() -> ocr.Reader:
    global _ocrReader
    if _ocrReader is None:
        _ocrReader = ocr.Reader(['en'])
    return _ocrReader


# validateImage(imagePath: Path)
#
# checks different factors for the image thats been given in to make sure you dont give a random image.
# it checks the image size, the colors, and makes sure it contains somewhere "materials to craft". if the
# library i use doesnt recognize "materials to craft", oh well ...
#
# input: the path to the image, they are stored in the CACHE folder under the same directory as this script.
# output: a cool boolean that says if the image is valid or not
#
# note: this shouldn't cause too many issues unless someone decided it'd be fun to play on a smart fridge
def validateImage(imagePath: Path) -> bool:
    try:
        with Image.open(imagePath) as im:
            if im.mode not in ("RGB", "RGBA", "L"):
                return False
            
            w, h = im.size
            if w < 150 or h < 70:
                return False

        reader = getReader()
        ocrResult = reader.readtext(str(imagePath))
        combined = " ".join(item[1] for item in ocrResult).lower()
        return "materials to craft" in combined
    except Exception:
        return False


# notify(timeMS: int, message: str, color: str)
#
# adds a text (message) with a color (color) for the duration in milliseconds (timeMS) under text
#
# input: the time the text appears for in milliseconds, the message displayed, and finally the color of the text
# output: none
#
# note: realized it would be great to have a function like this. im not a professional with tkinter so you'll enjoy
#       my plain UI design
def notify(timeMS: int, message: str, color: str) -> None:
    notifyLabel = tk.Label(root, text = message, font = ("Arial", 10), fg = color)
    notifyLabel.pack(pady = 10)
    
    root.after(timeMS, notifyLabel.destroy)


# copyToClipboard(text: str)
#
# copies a string to your clipboard so you can paste it anywhere
#
# input: the string that will get sent to the clipboard
# output: none
def copyToClipboard(text: str) -> None:
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

labels: list[tk.Label] = []


# handler()
#
# creates and returns a function called paste. it initalize an int "i" to
# keep track of the images name so it can be sorted later on
#
# input: none
# output: the paste function
#
# note: workaround to avoid global, later on regretted since I've used global anyways

# paste(event: Optional[tk.Event] = None)  WITHIN  handler()
#
# grabs the image from the clipboard, passes a few verifications (is an image, format), and adds it to the CACHE folder
# it gives a name by default, so then it can be sorted out during the image process. this being clipboard{image order}.png
# it also adds the image name to the UI so we can keep track of them, aswell as the anomalous ones.
#
# input: an event from tkinter initialized as none
# output: none
#
# note: theres a lot of redundency in this one but meh I am lazy to go through and fix it 😭💔
def handler() -> Callable[[Optional[tk.Event]], None]:
    i = 1
    def paste(event: Optional[tk.Event] = None):
        nonlocal i
        clip = ImageGrab.grabclipboard()
        if not clip:
            notify(3000, "no image on clipboard", "red")
            return
        
        if isinstance(clip, list):
            for path in clip:
                try:
                    p = Path(path)
                    if p.is_file():
                        dest = cache / p.name
                        shutil.copy(p, dest)
                        valid = validateImage(dest)
                        lbl = tk.Label(root, text = dest.name + ("" if valid else " (unrecognized format)"), anchor = "w", fg = ("blue" if valid else "red"))
                        lbl.pack(fill = "x", padx = 4, pady = 2)

                        if not valid: notify(3000, f"/!\\ potentially unrecognized format on image: clipboard{i}.png", "orange")

                        labels.append(lbl)
                        i += 1
                except Exception as e:
                    notify(3000, f"failed to copy from clipboard path {path}: {e}", "red")
        else:
            try:
                fileName = cache / f"clipboard{i}.png"
                clip.save(fileName)
                valid = validateImage(fileName)
                lbl = tk.Label(root, text = fileName.name + ("" if valid else " (unrecognized format)"), anchor = "w", fg = ("blue" if valid else "red"))
                lbl.pack(fill = "x", padx = 4, pady = 2)

                if not valid: notify(3000, f"/!\\ potentially unrecognized format on image: clipboard{i}.png", "orange")

                labels.append(lbl)
                i += 1
            except Exception as e:
                notify(3000, f"failed to save clipboard image: {e}", "red")
    return paste


# delete(event: Optional[tk.Event] = None)
#
# deletes every single images inside of the CACHE folder
#
# input: event initialized as none
# output: none
#
# note: we're reaching the meowy 4 am code, get ready for the blasphemous code in processAndPrint
def delete(event: Optional[tk.Event] = None) -> None:
    for filename in os.listdir(cache):
        filePath = cache / filename
        try:
            if filePath.is_file() or filePath.is_symlink():
                filePath.unlink()
            elif filePath.is_dir():
                shutil.rmtree(filePath)
        except Exception as e:
            notify(3000, f"failed to delete {filePath}: {e}", "red")
    
    for lbl in labels:
        lbl.destroy()
    labels.clear()


# processAndPrint(event: Optional[tk.Event] = None)
#
# processes every single images in order. it then uses the easyocr tool to decode the image into text.
# it will later on tokenize the text and try to sort out the values, while also fixing the potentially trash
# generated by misreading the text. it then proceeds to compile a readable result by mixing the generated and fixed
# tokens, while adding tier 0 calculations to get percentages. ONLY THEN, it will send the compiled result into your
# clipboard
#
# input: event, initialized as none
# output: the sheet containing all sorted tokens
#
# note: this function is chaotic as hell and does not deserve any attention. forgive me but it was LATE when doing this.
def processAndPrint(event: Optional[tk.Event] = None) -> list[tuple[str, int, int]]:
    reader = getReader()
    texts: list[str] = []

    for imagePath in sorted(cache.glob("*.png")):
        if not imagePath.is_file():
            continue
        ocrResult = reader.readtext(str(imagePath))
        texts.append(" ".join(item[1] for item in ocrResult))

    sheets = {}

    for text in texts:
        #print(f"\n--- RAW OCR ---\n{text}\n")
        
        if "Materials to Craft:" not in text:
            continue

        header, _, content = text.partition("Materials to Craft:")
        sheetName = header.strip()

        if sheetName not in sheets:
            sheets[sheetName] = []
        
        tokens = content.split()

        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if "/" in token:
                amountString = token.replace("O", "0").replace("l", "1").replace("I", "1")
                amountString = "".join(c for c in amountString if c.isdigit() or c == "/")
                
                oreParts = []
                j = i + 1
                while j < len(tokens) and "/" not in tokens[j]:
                    oreParts.append(tokens[j])
                    j += 1

                oreName = " ".join(oreParts) if oreParts else "Unknown"

                try:
                    current, maxVal = map(int, amountString.split("/"))
                    sheets[sheetName].append((oreName, current, maxVal))
                except ValueError:
                    pass

                i = j
            else:
                i += 1

    #print("\n--- PARSED ---")
    compiledResult: str = ""
    subTotals: list[tuple[int, int]] = []

    for sheetName, ores in sheets.items():
        compiledResult += f"- {sheetName}:"
        
        totalCollected = 0
        totalMax = 0

        for oreName, current, maxVal in ores:
            #print(f"  {ore_name}: {current}/{max_val}")
            totalCollected += min(current, maxVal)
            totalMax += maxVal

            compiledResult += f"\n  - {oreName}: {((min(current, maxVal)/maxVal) * 100):.2f}%   |   {current}/{maxVal}"
        
        subTotals.append((totalCollected, totalMax))
        compiledResult += f"\n\n  {sheetName} TOTAL: {((totalCollected / totalMax) * 100):.2f}%   |   {totalCollected}/{totalMax}\n\n"

    grandCollected = sum(collected for collected, _ in subTotals)
    grandMax = sum(maxVal for _, maxVal in subTotals)
    grandPercent = (grandCollected / grandMax * 100) if grandMax > 0 else 0

    compiledResult += f"\nTOTAL PROGRESS: {grandPercent:.2f}%   |   {grandCollected}/{grandMax}"
    #print(compiledResult)
    copyToClipboard(compiledResult)

    notify(3000, "Success! Copied results to clipboard", "green")

    return sheets


# onClose()
#
# deletes the cache folder and kills the root when the program is closed
#
# input: none
# output: none
def onClose() -> None:
    if cache.exists():
        shutil.rmtree(cache)
    root.destroy()


root.bind("<Control-v>", handler())
root.bind("<Return>", processAndPrint)
root.bind("<BackSpace>", delete)


root.title("Rex Recipe Progress")
root.geometry("400x300")

label = tk.Label(root, text = "Rex:R Recipe Progress (Windows Only Probably)\n\nControls:", font = ("Arial", 10), fg = "black")
label.pack(pady = 10)

# this line is horrible
label2 = tk.Label(root, text = "- CTRL + V: Paste ore sheet             \n- Backspace: Delete all images stored\n- Enter: Process and copy results      ",
                  font = ("Arial", 10), fg = "red")
label2.pack(pady = 0)

root.protocol("WM_DELETE_WINDOW", onClose)
root.mainloop()