# The SAP Automatic Label Printing System

In February the company migrated to SAP, the famous Enterprise Resource Planning software. Practically every single corporate department now depends on that software.

Finished Goods that are ready for shipment need a label that previously came from the now-defunct XPPS software. Now, labels come from a software called Membrain PAS, rendering the old SATO printer obsolete. A previously automated process now is performed by the area personnel. SAP inventory suffers grave damage when LT employees print wrong labels or discard already printed labels. The typical cardboard/plastic container can hold up to 120-140 pcs. Once i saw an employee print a 10,000 container label and attach to the cardboard container without much care.



This python interface will receive data from a serial connection and will click some stuff with pyautogui to get the label, leaving human error out of the process.

Features:
-It can detect the screen and act accordingly if an employee left Membrain in another screen (i.e he was cancelling an HU, or left an error message open)
-Serial data pre processing to find corrupted or incomplete data.
-It can try to print a second time if the error allows it (i.e if the error is caused by internet outage, etc)
-console prints are optimized to identify the program sequence
-Tesseract can read the error message and decide if send notification or to try again.
-Telegram notifications serve as the point of contact with supervisors and management. 
  -When something goes wrong or some data is changed (Container capacity suddenly changed), Telegram sends a message to the specied group.
