import serial
from Processes import *

def generate_ccsds_header(packet_sequence: int, data_length: int) -> bytes:
    packet_version_number = 0b000

    # Packet identification
    packet_type = 0b0  # 0 for telemtry
    secondary_header_flag = 0b0  # no secondary header is present
    apid = 101 # MAX 0x3ff

    # Packet sequence
    sequence_flags = 0b11  # Unsegmented frame
    # packet_sequence = packet_sequence

    packet_length = data_length - 1

    # Pack data
    version_identification = 0 \
        | ((packet_version_number << (16 - 3)) & 0xE000) \
        | ((packet_type << (16 - 4)) & 0x1000) \
        | ((secondary_header_flag << (16 - 5)) & 0x0800) \
        | ((apid << 0) & 0x07FF)

    packet_sequence_control = 0 \
        | ((sequence_flags << (16 - 2)) & 0xC000) \
        | ((packet_sequence << 0) & 0x3FFF)

    data = b'' \
        + version_identification.to_bytes(2, 'big') \
        + packet_sequence_control.to_bytes(2, 'big') \
        + packet_length.to_bytes(2, 'big')

    return data

#def extract_ccsds_data(data: bytes):
#    version_identification = int.from_bytes(data[:2], 'big')
#    packet_version_number = ((version_identification & 0xE000) >> (16 - 3))
#    packet_type = ((version_identification & 0x1000) >> (16 - 4))
#    secondary_header_flag = ((version_identification & 0x0800) >> (16 - 5))
#    apid = ((version_identification & 0x07FF) >> 0)

#    packet_sequence_control = int.from_bytes(data[2:4], 'big')
#    sequence_flags = ((version_identification & 0xC000) >> (16 - 2))
#    packet_sequence = ((version_identification & 0x3FFF) >> 0)

#    packet_length = int.from_bytes(data[4:6], 'big') + 1 # One byte is removed from length because of specification

#    payload = data[6:(6+packet_length)]

#    return apid, packet_length, payload

#def extract_can_packet(data: bytes):
#    can_id = int.from_bytes(data[:2], 'big') # Usally 11 bits, but for simplicty assume 16 bit

#    payload = data[2:]

#    return can_id, payload

# TELEMETRY

class TMLink(SocketProcess):
    
    HOST = "127.0.0.1"
    PORT = 10017
    
    def setup(self):
        super().setup()
        self.counter = 0
    
    def loop(self):
        if not self.queueDict["TM_Queue"].empty():
            currentMsg = self.queueDict["TM_Queue"].get()
            #self.log("Send data to mission control")
            #self.log(currentMsg)
            try:
                header = generate_ccsds_header(self.counter, len(currentMsg))
                self.conn.send(header+currentMsg)
            except:
                self.log("TCP SEND EXCEPTION")
            self.counter += 1

# COMMANDING

class TCLink(SocketProcess):
    
    HOST = "127.0.0.1"
    PORT = 10019
    
    def loop(self):
        data = None
        command = None

        try:
            data = self.conn.recv(1024)
        except socket.timeout:  # fail after 1 second of no activity
            self.log("Recv Timeout")
        
        if data is not None:
            #data_str = ""
            #for item in data:
            #    data_str += str(item)
            self.queueDict["TC_Queue"].put(data)
            self.log(data)
            self.log('[TC] Command send')
            
class UartLink(StaProcess):
    
    def setup(self):
        super().setup()
        try:
            self.ser = serial.Serial('COM3', 38400, timeout=None)
        except serial.SerialException:
            self.log('[ERROR] Port Error')
    def cleanUp(self):
        super().cleanUp()
        self.ser.close()
    def loop(self):
        id_dict = {
        0 : 22,
        #1 : 49,
        2 : 34,
        3 : 3
        }
        
        # State definitions:
        # 0: waiting for sync_1
        # 1: waiting for sync_2
        # 2: waiting for ID (complete header)
        # 3: reading payload
        # 4: reset state (process current byte as possible sync_1, then immediately go to state 0 if not found)
        state = 0
        current_packet = b''
        current_byte = b''
        packet_name = ''
        counter = 0
        length = 0
        packet_counter = 0

        while True:
            if not self.queueDict["TC_Queue"].empty():
                currentCmd = self.queueDict["TC_Queue"].get()
                written = self.ser.write(currentCmd)
                #self.queueDict["TM_Queue"].put(bytes.fromhex('42acfa00b703'))
                #self.queueDict["TM_Queue"].put(bytes.fromhex('42acff0048f6'))
                #self.log(currentCmd)
                self.log('[TC] Command sent')

            if state != 4:
                current_byte = self.ser.read()
            # else: data is already set from previous iteration

            self.log('[DEBUG] Byte: ' + str(current_byte) + ', Packet: ' + packet_name + ', Counter: ' + str(packet_counter))

            match state:
                case 0:  # Waiting for sync_1
                    if current_byte == bytes.fromhex('42'):
                        current_packet = current_byte
                        state = 1
                    else:
                        self.log('[DEBUG] Wrong sync_1 in packet ' + str(packet_counter))
                    # else: stay in state 0
                    continue

                case 1:  # Waiting for sync_2
                    if current_byte == bytes.fromhex('ac'):
                        current_packet += current_byte
                        state = 2
                    else:
                        # Not a valid sync_2, restart sync search
                        state = 0
                        self.log('[DEBUG] Wrong sync_2 in packet ' + str(packet_counter))
                    continue

                case 2:  # Waiting for ID (complete header)
                    match current_byte:
                        case bytes.fromhex('f0'):
                            length = id_dict[0]
                            packet_name = 'Status'
                        #case bytes.fromhex('f1'):
                            #length = id_dict[1]
                            #packet = 'Sensors'
                        case bytes.fromhex('f2') | bytes.fromhex('f3') | bytes.fromhex('f4'):
                            length = id_dict[2]
                            packet_name = 'Hull Sensors'
                        case bytes.fromhex('fa') | bytes.fromhex('ff'):
                            length = id_dict[3]
                            packet_name = 'Error'
                        case _:
                            # Not a valid ID, go to reset state and process this byte as possible sync_1
                            current_packet = b''
                            state = 4
                            counter = 0
                            self.log('[DEBUG] Wrong ID in packet ' + str(packet_counter))
                            continue
                    current_packet += current_byte
                    counter = 0
                    state = 3
                    continue

                case 3:  # Reading payload
                    # Read the rest of the payload in a tight loop
                    while counter < length:
                        if counter == 0:
                            # First byte already read as 'current_byte'
                            current_packet += current_byte
                        else:
                            current_packet += self.ser.read() # Read next byte
                        counter += 1
                    packet_counter += 1
                    self.queueDict["TM_Queue"].put(current_packet)
                    self.log('[TM] ' + packet_name + ' Packet received ('+ str(packet_counter) +')')
                    # Reset for next packet
                    state = 0
                    current_packet = b''
                    current_byte = b''
                    packet_name = ''
                    counter = 0
                    length = 0
                    continue

                case 4:  # Reset state: process current byte as possible sync_1, then immediately go to state 0 if not found
                    if current_byte == bytes.fromhex('42'):
                        current_packet = current_byte
                        state = 1
                    else:
                        # Not a sync_1, go back to waiting for sync_1 and read next byte
                        state = 0
                    continue

if __name__ == "__main__":
    manager = ProcessManager(5, 1)

    manager.addProcess(TMLink)
    manager.addProcess(TCLink)
    manager.addProcess(UartLink)
    
    manager.addQueue("TM_Queue")
    manager.addQueue("TC_Queue")

    manager.run()

    print(manager.exitCode)
    
    