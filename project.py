import socket

import threading

import queue

import pickle

import argparse

from datetime import datetime

from dataclasses import dataclass

#dataclass for Message info
@dataclass
class Message:
    msg: str
    time: datetime

#dataclass for network details
@dataclass
class NetworkDetails:
    here: str
    there: str
    outport: int
    inport: int

def prepare_message(inputString):
    return pickle.dumps(Message(msg = inputString, time=datetime.now()))

#Thread for sending messages
def sender(s, networkDetails, messages, event):
    msg = ""
    while not event.is_set():
        msg = input(f"(Message): ")
        if( msg == "/end"):
            event.set()
        else:
            out = prepare_message(msg)
            s.sendto(out, (networkDetails.there, networkDetails.outport))
            if not messages.empty():
                print_messages(messages)

#Thread for receiving messages
def receiver(s, networkDetails, messages, event):
    try:
        s.bind((networkDetails.here, networkDetails.inport))
    except:
        pass
    while not event.is_set():
        try:
            temp = s.recvfrom( 1024 )
            received = pickle.loads(temp[0])
            messages.put(received)
        except socket.error:
            pass

def print_messages(messages):
    while not messages.empty():
        msg = messages.get()
        print(f"(Received {datetime.now()-msg.time} seconds ago): {msg.msg}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="UDP Messaging Application")
    
    parser.add_argument('Your Address', metavar='H', type=str,
     help="Your Address")

    parser.add_argument('Their Address', metavar='D', type=str,
     help="Address you will be sending to.")
    
    parser.add_argument('Out Port', metavar='PI', type=int,
     help="Port you will be sending over.")

    parser.add_argument('In Port', metavar='PO', type=int,
    help="Port you will be listening on.")

    args = parser.parse_args()
    cmdLineArgs = vars(args)
    home, direction, outport, inport = cmdLineArgs.values()

    networkDetails = NetworkDetails(here=home, there=direction, outport=outport, inport=inport)

    return networkDetails

#Main function
def main():
    networkDetails = parse_arguments()
    messages = queue.Queue()
    event = threading.Event()
    udp = socket.getprotobyname('udp')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
    s.setblocking(0)

    x = threading.Thread(target=sender, args=(s, networkDetails, messages, event))
    y = threading.Thread(target=receiver, args=(s, networkDetails, messages, event))

    x.start()
    y.start()

if __name__ == "__main__":
    main()