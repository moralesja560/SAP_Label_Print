# The SAP Automatic Label Printing System

In February 2022 the company migrated to SAP, the famous Enterprise Resource Planning software. Practically every single corporate department now depends on that software.

Crates of Finished Goods that are ready for shipment need a label that previously came from the now-defunct XPPS software. 
Now, labels come from a software called Membrain PAS, rendering the old SATO printer obsolete. 
A previously automated process now is performed by the area personnel.
SAP inventory suffers grave damage when LT employees print wrong labels or discard already printed labels. The typical cardboard/plastic container can hold up to 120-140 pcs. Once i saw an employee print a 10,000 pieces container label and attach it to the cardboard container without much care.


The software reads a string from PLC using Twincat ADS and pyads, the native communication protocol from beckhoff. The string contains the SAP order, the type and capacity of the container. The software receives the string, pre-process it to ensure validity and completeness and then performs the necessary clicks to print the label. 

Features:
- It can detect the screen and act accordingly if an employee left Membrain in another screen (i.e he was cancelling an HU, or left an error message open)
- Serial data pre processing to find corrupted or incomplete data and use previously stored data.
- Console prints are optimized to identify the program sequence
- Tesseract can read the error message and decide to send a notification or to print a second time if the error allows it (i.e if the error is caused by internet outage, etc)
- Tesseract can also read the label Handling Unit number to keep a record of printed labels.
- Telegram notifications serve as the point of contact with supervisors and management. 
  -When something goes wrong or some data is changed (Container capacity suddenly changed), Telegram sends a message to the specified group.
  
### File Descriptions:
#### Images Folder
1. Images folder contains all the pictures needed to deploy pyautogui locatescreen feature, the main UI picture and some CSV files that contain tkinter buttons
#### root

1. listdir.py iterates trough a function to discover local paths such as My Documents, Program Files and many other relevant paths.

2. locate_Test.py served as a training area to test the pyautogui.locatescreen "confidence" parameter. A very high setting in this parameter will prevent the software to see what's on the screen. And a low confidence parameter may wrongly select an incorrect screen area. 

3. #### maing.py  The main software file

4. screenshot.py serves as the training area for Tesseract

5. tkinter_template.py is the base file to develop new applications based on this threading technique.

## Updates
There have been many updates over the years, mostly to adjust some functions and to fix some bugs with threading system and stuff.
Our biggest change is that we use now Pyads instead of serial port. A more reliable connection to the PLC using Twincat ADS.

### Twincat ADS
The ADS protocol (ADS: Automation Device Specification) is a transport layer within the TwinCAT system. It was developed for data exchange between the different software modules, for instance the communication between the NC and the PLC. This protocol enables communication with other tools from any point within the TwinCAT. If communication with other PCs or devices is required, the ADS protocol can use TCP/IP as a basis. Within a networked system it is thus possible to reach all data from any point
