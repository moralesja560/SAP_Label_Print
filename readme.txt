In February the company migrated to SAP, the famous Enterprise Resource Planning software. Practically every single corporate department now depends on that software.

Labels now come from SAP, rendering the old SATO printer obsolete. A previously automated process now is done by area personnel, but the main issue is that people print many labels without having the actual shipment ready to attach the label to. This action gravely damages the SAP inventory number by adding ghosts containers.

This python interface will receive data from a serial connection and will click some stuff with pyautogui to get the label, leaving human error out of the process.

Features:
-Serial port with pyserial to receive the needed info
-Tkinter GUI to inform the user what's going on and to set some parameters, such as com port selection
-pyautogui to click the membrain software to get the tag.
-CSV to log some information about the printed labels.
