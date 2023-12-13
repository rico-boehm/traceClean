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
            self.ser = serial.Serial('COM5', 38400, timeout=None)
        except serial.SerialException:
            self.log('[ERROR] Port Error')
    def cleanUp(self):
        super().cleanUp()
        self.ser.close()
    def loop(self):
        id_dict = {
        0 : 19,
        1 : 49,
        2 : 52,
        3 : 3
        }
        
        sync_1 = False
        sync_2 = False
        header = False
        reset = False
        serial_data = b''
        data = b''
        packet = ''
        counter = 0
        length = 0
        packet_counter = 0
        
        while True:
            if not self.queueDict["TC_Queue"].empty():
                currentMsg = self.queueDict["TC_Queue"].get()
                written = self.ser.write(currentMsg)
                self.queueDict["TM_Queue"].put(bytes.fromhex('42acfa00b703'))
                self.queueDict["TM_Queue"].put(bytes.fromhex('42acff0048f6'))
                #self.log(currentMsg)
                #self.log(written)
            
            if reset == False: #If two sync bytes or a wrong 'id' where encountered in the previous iteration the old packet is discarded and a new one is started with the received bytes
                data = self.ser.read()
                self.log('[DEBUG] Byte: ' + str(data) + ', Packet: ' + packet + ', Counter: ' + str(packet_counter))
            else:
                reset = False
            if data == bytes.fromhex('42') and sync_1 == False: #First byte of a packet
                serial_data += bytes.fromhex('42')
                sync_1 = True
                continue
            elif data == bytes.fromhex('ac') and sync_1 == True and sync_2 == False: #Second byte of a packet
                serial_data += bytes.fromhex('ac')
                sync_2 = True
                continue
            elif sync_1 == True and sync_2 == True and header == False: #Third byte of a packet; If byte is a known id, header is complete, otherwise packet is reset with the received byte as first       
                if data == bytes.fromhex('f0'):
                    length = id_dict[0]
                    packet = 'Status'
                elif data == bytes.fromhex('f1'):
                    length = id_dict[1]
                    packet = 'Sensors'
                elif data == bytes.fromhex('f2') or data == bytes.fromhex('f3') or data == bytes.fromhex('f4') or data == bytes.fromhex('f5'):
                    length = id_dict[2]
                    packet = 'Hull Sensors'
                elif data == bytes.fromhex('fa') or data == bytes.fromhex('ff'):
                    length = id_dict[3]
                    packet = 'Error'
                else:
                    serial_data = data
                    sync_1 = False
                    sync_2 = False
                    reset = True
                    counter = 0
                    self.log('[DEBUG] Wrong ID')
                    continue                       
                serial_data += data
                header = True
                counter = 0
                continue                        
            elif counter < length: #After the header is complete the payload is built
                serial_data += data	
                counter += 1
                if counter == length: #If the last byte is received without error the loop is exited
                    packet_counter += 1
                    self.queueDict["TM_Queue"].put(serial_data)
                    self.log('[TM] ' + packet + ' Packet received ('+ str(packet_counter) +')')
                    sync_1 = False
                    sync_2 = False
                    header = False
                    reset = False
                    serial_data = b''
                    data = b''
                    packet = ''
                    counter = 0
                    length = 0
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
    
    