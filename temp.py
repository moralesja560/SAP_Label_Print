import pyads


# connect to the PLC
plc = pyads.Connection('10.65.96.129.1.1', 801)

# open the connection
plc.open()

# read the device name and the version
device_name, version = plc.read_device_info()
print(str(device_name) + ' ' + str(version))
"""
#read a boolean
bReadCommand = plc.read_by_name('Ethernet.bReadCmd', pyads.PLCTYPE_BOOL)
print(bReadCommand)

#write ack
plc.write_by_name('Ethernet.bACKFromPython', bReadCommand)

#read int number
int_number = plc.read_by_name('Ethernet.nMyNumber', pyads.PLCTYPE_INT)
print(int_number)

#read real number
real_number = plc.read_by_name('Ethernet.fMyRealNumber', pyads.PLCTYPE_REAL)
print(real_number)
"""
#read string
plc.write_by_name('PB_Stueckzahl.ADS_Label_Incoming_Ping',101,pyads.PLCTYPE_INT)
message_from_twincat = plc.read_by_name('PB_Stueckzahl.ADS_Label_Outgoing_Ping', pyads.PLCTYPE_INT)

print(message_from_twincat)
"""
#write string
if len(message_from_twincat) > 1:
    message_to_twincat = 'El super mono'
    plc.write_by_name('Ethernet.sMessageFromPython', message_to_twincat, plc_datatype=pyads.PLCTYPE_STRING)
"""
	# close connection
plc.close()