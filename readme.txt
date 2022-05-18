In February the company migrated to SAP, the famous Enterprise Resource Planning. Practically every single process depends on that software.
SAP came to replace a very old software called XPPS. This XPPS used a SATO printer to get labels for the ready-to-ship boxes.

This software will serve as the interface between a serial port that sends 3 values that are needed, and a pyautogui process that will click some stuff to get the print done.

Features:
-Serial port with pyserial to receive the needed info
-Tkinter GUI to inform the user what's going on and to set some parameters, such as com port selection
-pyautogui to click the membrain software to get the tag.
-CSV to log some information about the printed labels.
