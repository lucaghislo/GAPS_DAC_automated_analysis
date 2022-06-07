import GPIB
# X is your interface number (usually 0)
# Y is your instrument address (should be configured on the device)
inst = GPIB.Gpib(0,40960) 
inst.write("*IDN?")
print(inst.read(100))