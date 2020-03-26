#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Docstring
"""Command Line DownLoader for Motorola/Freescale/NXP MC68HC908GZ60"""

# Set built in COM port useable on Ubuntu:
#   List available ports by 'dmesg | grep tty'. My one is '[    1.427419] 00:01: ttyS0 at I/O 0x3f8 (irq = 4, base_baud = 115200) is a 16550A'
#   Add my user to dialout group by 'sudo gpasswd --add ${USER} dialout' 

# Import statements
import os, sys, getopt, struct
import array
import serial # I use Python 2.7.17. For this I needed 'sudo apt install python-pip' and 'sudo python -m pip install pyserial'
import bincopy # 'pip install bincopy'
import re
import time
import ntpath
import curses # https://docs.python.org/3/library/curses.html#module-curses
import binascii

# Authorship information
__author__ = "Janos BENCSIK"
__copyright__ = "Copyright 2020, butyi.hu"
__license__ = "GPL"
__version__ = "0.0.0"
__maintainer__ = "Janos BENCSIK"
__email__ = "gzdl.py@butyi.hu"
__status__ = "Prototype"

# Code

# ---------------------------------------------------------------------------------------
# Global variables
# ---------------------------------------------------------------------------------------
version = "V0.00 2020.03.25.";

inputfile = ""
if sys.platform.startswith("linux") or sys.platform.startswith("cygwin") or sys.platform.startswith("darwin"): # linux or OS X
  port = "/dev/ttyS0"
elif sys.platform.startswith("win"): # Windows
  port = "COM1"
baud = 9600
mem_dump = False
mem = bytearray(65536)
connected = False
terminal = False

# ---------------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
def p(s):  
  f1.write(s)
  sys.stdout.write(s)
  sys.stdout.flush()

# ---------------------------------------------------------------------------------------
def err(s):
  p("\nERROR! "+s+"\n\n")
  ser.close()
  f1.close() # Close communication log file
  sys.exit(1)

# ---------------------------------------------------------------------------------------
def h(byte,f = "02X"):
  return("$"+format(byte,f))

# ---------------------------------------------------------------------------------------
def DownloadRow(data, address):
  buff = bytearray()
  # Frame header
  buff.append(0x56)
  buff.append(0xAB)

  # Len
  buff.append(0x00) # Len high. Not used in GZ family because page size is just 128 bytes
  cs = len(data)
  buff.append(cs) # Len low

  # Address
  addr_hi = (address >> 8) & 0xFF
  cs += addr_hi
  buff.append(addr_hi)
  addr_lo = address & 0xFF
  cs += addr_lo
  buff.append(addr_lo)

  # Data
  for byte in data:
    cs += int(byte)
  buff += bytearray(data)

  # Checksum
  cs &= 0xFF
  buff.append(cs)


  # Transmission
  f1.write("\nDat Tx: "+binascii.hexlify(buff)+"\n")
  num = ser.write(buff)
  if num < len(buff):
    err("Too less "+h(num)+" written bytes for page "+h(address,"04X"))

  # Receive answer
  answer = bytearray()
  answer.extend(ser.read(5))
  f1.write("Dat Rx: "+binascii.hexlify(answer)+"\n")

  # Check answer if it is proper
  if len(answer) == 0:
    err("There was no answer for page "+h(address,"04X"))
  
  #if(com_dump)printf_hex(fcd, "Rx: ", answer, answer_len);
    
  if len(answer) < 5:
    err("Too short answer for page "+h(address,"04X"))

  if answer[0] != 0xBA:
    err("Wrong answer in first header character for page "+h(address,"04X")+". "+h(answer[0])+" instead of $BA.")
  if answer[1] != 0x65:
    err("Wrong answer in second header character for page "+h(address,"04X")+". "+h(answer[1])+" instead of $65.")
  if answer[2] != addr_hi:
    err("Wrong answer in address high byte for page "+h(address,"04X")+". "+h(answer[2])+" instead of "+h(addr_hi)+".")
  if answer[3] != addr_lo:
    err("Wrong answer in address low byte for page "+h(address,"04X")+". "+h(answer[3])+" instead of "+h(addr_lo)+".")

  if answer[4] == 0: # OK
    return True
  elif answer[4] == 1:
    err("Checksum error from address "+h(address,"04X")+" with len "+str(len(data))+".")
  elif answer[4] == 2:
    err("Address error from address "+h(address,"04X")+" with len "+str(len(data))+".")
  elif answer[4] == 3:
    err("Timeout error from address "+h(address,"04X")+" with len "+str(len(data))+".")
  elif answer[4] == 4:
    err("Len error from address "+h(address,"04X")+" with len "+str(len(data))+".")
  else:
    err("Unknown error "+h(answer[4])+" from address "+h(address,"04X")+" with len "+str(len(data))+".")

# ---------------------------------------------------------------------------------------
def ConnectDevice():
  conn = b"\x1C\x1C\x1C\x1C"
  goodresp = b"\xE3\xE3\xE3\xE3"
  try:
    while True:
      f1.write("\nConn Tx: "+binascii.hexlify(conn)+"\n")
      ser.write(conn)

      answer = bytearray()
      answer.extend(ser.read(4))
      if 0<len(answer): # If there was any answer
        f1.write("\nConn Rx: "+binascii.hexlify(answer)+"\n")
      if answer == goodresp:
        break
      #p(h(ord(resp[0]))) 
  except KeyboardInterrupt:
    p("\nUser abort.\n")
    ser.close()
    f1.close() # Close communication log file
    sys.exit(0)
  else:
    return
  
# ---------------------------------------------------------------------------------------
def PrintHelp(): 
  p("gzdl.py - MC68HC908GZ60 DownLoader - " + version +"\n")
  p("Download software into flash memory from an S19 file through RS232\n")
  p("Log file gzdl.com is always created/updated (See with 'cat gzdl.com')\n");
  p("Options: \n")
  p("  -p port      Set serial com PORT used to communicate with target (e.g. COM1 or /dev/ttyS0)\n")
  p("  -b baud      Baud rate of downloading\n")
  p("  -f s19file   S19 file path to be downloaded\n")
  p("  -t           Terminal after download.\n");
  p("  -m           Memory dump into text file gzdl.mem (See with 'xxd gzdl.mem')\n")
  p("  -h           Print out this HELP text\n")
  p("Examples:\n")
  p("  gzml.py -f xy.s19  Download xy.s19 software into uC\n")
  f1.close() # Close communication log file
  sys.exit(0)

# ---------------------------------------------------------------------------------------
# MAIN()
# ---------------------------------------------------------------------------------------

# Open communication log file
f1 = open("./gzdl.com", "w+")

#Parsing command line options
argv = sys.argv[1:]
try:
  opts, args = getopt.getopt(argv,"p:b:f:mth:",["port=","baud=","file=","memory","terminal","help"])
except getopt.GetoptError:
  p("Wrong option.\n")
  PrintHelp()
for opt, arg in opts:
  if opt in ("-h", "--help"):
    PrintHelp()
  elif opt in ("-p", "--port"):
    port = arg
  elif opt in ("-b", "--baud"):
    baud = int(arg)
  elif opt in ("-f", "--file"):
    inputfile = arg
  elif opt in ("-m", "--memory"):
    mem_dump = True
  elif opt in ("-t", "--terminal"):
    terminal = True

# Inform user about parsed parameters
p("gzdl.py - MC68HC908GZ60 DownLoader - " + version + "\n")
p("Port '" + port + "'\n")
p("Baud rate is " + str(baud) + "\n")

# Open serial port
p("Open serial port")
try:
  ser = serial.Serial(port, baud, timeout=1)
except:
  err("Cannot open serial port " + port)
p(", Done.\n")



# ---------------------------------------------------------------------------------------
# Download operation
if 0 < len(inputfile):

  p("Build up memory model")
  # Build memory map of MC68HC908GZ60 in rows. This is a list of dictionary (c struct array)
  #  Property row and rowlen depends on bootloader, start and length depends on used range in row.
  rows =        [{"row":0x462, "start":0x462, "rowlen":30, "used":False, "data":bytearray() }]
  for r in range(0x480,0x500,128):
    rows.append({"row":r, "start":r, "rowlen":128, "used":False, "data":bytearray() })
  for r in range(0x980,0x1B80,128):
    rows.append({"row":r, "start":r, "rowlen":128, "used":False, "data":bytearray() })
  rows.append({"row":0x1E20, "start":0x1E20, "rowlen":0x60, "used":False, "data":bytearray() })
  for r in range(0x1E80,0xF500,128):
    rows.append({"row":r, "start":r, "rowlen":128, "used":False, "data":bytearray() })
  rows.append({"row":0xFFCC, "start":0xFFCC, "rowlen":0x34, "used":False, "data":bytearray() })
  p(", Done.\n")

  # Read S19 into data array. Not used bytes are 0xFF.
  p("Read S19 file "+ntpath.basename(inputfile))
  f = bincopy.BinFile(inputfile)
  p(", Done.\n")

  p("Collect data")
  mem = [0xFF] * 65536
  for segment in f.segments:
    i = 0
    for x in range(segment.address,segment.address+len(segment.data)):
      mem[x] = segment.data[i]
      i += 1
  p(", Done.\n")

  # Save memory content
  if mem_dump:
    p("Create or update file gzdl.mem")
    f2 = open("./gzdl.mem", "w+")
    f2.write(bytearray(mem))
    f2.close()
    p(", Done.\n")

  # Fill memory map data from S19
  p("Fill memory rows with data")
  for r in rows:
    for a in range(r["row"], r["row"] + r["rowlen"]): # Go forward on row addresses
      if mem[a] != 0xFF and r["used"] == False: # If this is the first data byte
        r["start"] = a # Save start address
        r["used"] = True # Mark as row is used
      if r["used"] == True: # If row used
        r["data"].append(mem[a]) # Add further data bytes 
    if r["used"] == False: # If there is no data in row,
      continue # There is no more task
    # Delete 0xFF bytes from end of row
    for a in range(r["row"] + r["rowlen"]-1, r["row"]-1, -1): # Go backward on row addresses
      if mem[a] == 0xFF: # If data byte is empty
        r["data"].pop() # Drop it from data list
      else: # At first not empty data byte 
        break # leave the loop

  # Delete not used rows from list
  rows[:] = [r for r in rows if r.get("used") != False]
  #p(rows)
  p(", Done.\n")

  # Connecting to devive
  p("Connect to device (Press Ctrl+C to abort)");
  ConnectDevice()
  p(", Done.\n")

  # Erase start vector page first
  p("Erase start vector page first")
  erase = bytearray()
  erase.append(0xFF)
  erase.append(0xFF)
  DownloadRow( erase, 0xFFFE ) # Here it is not problem, that the complete page is erased. Content will be written again during download.
  p(", Done.\n")

  # Download rows
  for r in rows:
    p("Write row "+h(r["row"],"04X")+"("+h(r["rowlen"])+"): "+h(len(r["data"]))+" bytes from "+h(r["start"],"04X"))
    ret = DownloadRow(r["data"],r["start"])
    p(", Done.\n")

# ---------------------------------------------------------------------------------------

# Terminal
if terminal:
  f1.write("\nTerminal started\n")
  ser.timeout = 0 # clear timeout to speed up terminal response
  stdscr = curses.initscr()
  curses.noecho() # switch off echo
  stdscr.nodelay(1) # set getch() non-blocking
  stdscr.scrollok(True)
  stdscr.idlok(True)
  while True:

    # From keyboard to UART
    c = stdscr.getch()
    if c == 0x1B: # ESC button
      break
    if c != -1:
      ser.write(chr(c))
      f1.write(chr(c))

    # From UART to display
    bs = ser.read(1)
    if len(bs) != 0:
      stdscr.addch(bs)
      f1.write(bs)

  # Restore original window mode
  curses.echo()
  curses.reset_shell_mode()
  p("\n")

# ---------------------------------------------------------------------------------------

p("Done.\n")
ser.close()
f1.close() # Close communication log file
sys.exit(0)

