In February the company migrated to SAP, the famous Enterprise Resource Planning software. Practically every single corporate department now depends on that software.

Finished Goods that are ready for shipment need a label that previously came from the now-defunct XPPS software. Now, labels come from a software called Membrain PAS, rendering the old SATO printer obsolete. A previously automated process now is performed by the area personnel. SAP inventory suffers grave damage when LT employees print wrong labels or discard already printed labels. The typical cardboard/plastic container can hold up to 120-140 pcs. Once i saw an employee print a 10,000 container label and attach to the cardboard container without much care.



This python interface will receive data from a serial connection and will click some stuff with pyautogui to get the label, leaving human error out of the process.

Features:
-Serial port with pyserial to receive the needed info
-Tkinter GUI to inform the user what's going on and to set some parameters, such as com port selection
-pyautogui to click the membrain software to get the tag.
-CSV to log printed labels and errors
-Telegram automated notifications: 
  -This is a big deal: The fact that the script can send Telegram messages in case of error, opens the door to very big developments.
