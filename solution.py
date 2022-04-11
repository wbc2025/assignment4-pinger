from socket import *
import os
import sys
import struct
import time
import select
import binascii
import random
# Should use stdev
from statistics import stdev
from warnings import catch_warnings
from socket import gaierror

ICMP_ECHO_REQUEST = 8


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start

        # Fetch the ICMP header from the IP packet

        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")


    # SOCK_RAW is a powerful socket type. For more details:   https://sock-raw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	
    # the client assumes that either the client's ping or the server's pong is lost
    
    dest = ''

    try:
        dest = gethostbyname(host)
        # print("Pinging " + dest + " using Python:")
        # print("")
    except gaierror as ex:
        # print(ex)
        return ['0', '0.0', '0', '0.0']
    
    #Send ping requests to a server separated by approximately one second
    #Add something here to collect the delays of each ping in a list so you can calculate vars after your ping
    
    packet_min = 1000
    packet_max = 0
    packet_sum = 0
    stdev_var = []

    for i in range(0,4): #Four pings will be sent (loop runs for i=0, 1, 2, 3)
        # delay = doOnePing(dest, timeout)

        delay = random.randint(1, 999)
        # delay = 0

        print(delay)

        packet_sum += delay
        stdev_var.append(delay)

        if delay < packet_min:
            packet_min = delay

        if delay > packet_max:
            packet_max = delay


        time.sleep(1)  # one second
        
    packet_avg = packet_sum / 4

    #You should have the values of delay for each ping here; fill in calculation for packet_min, packet_avg, packet_max, and stdev
    vars = [str(round(packet_min, 8)), str(round(packet_avg, 8)), str(round(packet_max, 8)),str(round(stdev(stdev_var), 8))]

    return vars

if __name__ == '__main__':
    vars = ping("google.co.il")
    print(vars)

    vars = ping("No.no.e")
    print(vars)
