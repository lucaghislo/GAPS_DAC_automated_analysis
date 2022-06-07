import pyvisa
from agilent_34461A import Agilent34461A

rm = pyvisa.ResourceManager()
print(rm.list_resources())

#print(rm)

#pyvisa.ResourceManager().list_resources()

agilent = Agilent34461A(rm)

print(agilent.get_voltage())