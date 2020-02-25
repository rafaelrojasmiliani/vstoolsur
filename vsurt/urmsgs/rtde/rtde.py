# Copyright (c) 2016, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import struct
import socket
import select
import sys
import logging

from . import serialize

DEFAULT_TIMEOUT = 1.0

class Command:
    RTDE_REQUEST_PROTOCOL_VERSION = 86        # ascii V
    RTDE_GET_URCONTROL_VERSION = 118          # ascii v
    RTDE_TEXT_MESSAGE = 77                    # ascii M
    RTDE_DATA_PACKAGE = 85                    # ascii U
    RTDE_CONTROL_PACKAGE_SETUP_OUTPUTS = 79   # ascii O
    RTDE_CONTROL_PACKAGE_SETUP_INPUTS = 73    # ascii I
    RTDE_CONTROL_PACKAGE_START = 83           # ascii S
    RTDE_CONTROL_PACKAGE_PAUSE = 80           # ascii P


RTDE_PROTOCOL_VERSION = 2

class ConnectionState:
    DISCONNECTED = 0
    CONNECTED = 1
    STARTED = 2
    PAUSED = 3


class RTDE(object):
    def __init__(self, hostname, port=30004):
        self.hostname = hostname           
        self.port = port
        self.__conn_state = ConnectionState.DISCONNECTED
        self.__sock = None  # BSD socket
#
        self.__output_config = None # serialize.DataConfig with 
        self.__input_config = {}
        
    def connect(self):
        """
        1) Creates a BSD socket for connecting with URControl. If connections
            is successful, set __conn_state = ConnectionState.CONNECTED.
        2)  Call self.negotiate_protocol_version, this functions performs
            the first handshake. The handshake is done as follows:
            2.1) Send 5 bytes, [5  (uint16 size of all packet, with size included.),
                                2  (uint8_t, command),
                                86 (uint16, ASCII character V)]
            2.2) self.negotiate_protocol_version returns a binary string.
                 If this string is empty, then the handshake is considered
                 failed. Otherwise the program exit successfully
        """
        if self.__sock:
            return

        self.__buf = b''
        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.__sock.settimeout(DEFAULT_TIMEOUT)
            self.__sock.connect((self.hostname, self.port))
            self.__conn_state = ConnectionState.CONNECTED
        except (socket.timeout, socket.error):
            self.__sock = None
            raise
        handshake_result= self.negotiate_protocol_version()
        if not handshake_result:
            logging.error('Unable to negotiate protocol version')
            sys.exit()
        return handshake_result

    def disconnect(self):
        """
          Just close the socket. This send a FIN TCP packet to RTDE
        Parameters:
        ----------
          None
        Returns:
        --------
          None
        """
        if self.__sock:
            self.__sock.close()
            self.__sock = None
        self.__conn_state = ConnectionState.DISCONNECTED
        
    def is_connected(self):
        """
          Returns if the socket to the RTDE service is connected.
        Parameters:
        ----------
          None
        Returns:
        --------
          Bolean. 
        """
        return self.__conn_state is not ConnectionState.DISCONNECTED
        
    def get_controller_version(self):
        """
          Create a message to ask to the RTDE interface asking for its
          version, and returns it.
        Parameters:
        ----------
          None
        Returns:
        --------
          A 4-tuple. with the version fields of the RTDE interface. 
        """
        cmd = Command.RTDE_GET_URCONTROL_VERSION
        version = self.__sendAndReceive(cmd)
        if version:
            logging.info('Controller version: ' + str(version.major) + '.' + str(version.minor) + '.' + str(version.bugfix)+ '.' + str(version.build))
            if version.major == 3 and version.minor <= 2 and version.bugfix < 19171:
                logging.error("Please upgrade your controller to minimally version 3.2.19171")
                sys.exit()
            return version.major, version.minor, version.bugfix, version.build
        return None, None, None, None
        
    def negotiate_protocol_version(self):
        """
        Description:
        ----------
          Request the controller to work with RTDE protocol version
          RTDE_PROTOCOL_VERSION.
        Parameters:
        ----------
          None
        Returns:
        --------
          A 4-tuple. with the version fields of the RTDE interface. 
        """
        cmd = Command.RTDE_REQUEST_PROTOCOL_VERSION
        payload = struct.pack('>H', RTDE_PROTOCOL_VERSION)
        success = self.__sendAndReceive(cmd, payload)
        return success
        
    def send_input_setup(self, variables, types=[]):
        """
        Sends to the RTDE server a comma-separated list of
        buffer names that we wand to write in the robot.
        Parameters
        ----------
          variables: list of strings
                     a list containt the names of the input registers
                     of RTDE. 
          types    : a list with types (?)
                     a list containing the types do the input registers
                     which the variables refers to.
        Returns:
        --------
          a DataObject instance which to abstrac the receipe. This
          DataObject instance has the a member variable for each
          register of the receipe

            Here is where __input_config is filled up
        """
        cmd = Command.RTDE_CONTROL_PACKAGE_SETUP_INPUTS# set cmd to the bye  'I'

        # create a comma-sepated string with the names of the 
        # input registers for this receipe
        payload = bytes(','.join(variables), 'utf-8')

        #send the data stream to the RTDE socket
        result = self.__sendAndReceive(cmd, payload)

        # Test the consistency of data returned by RTDE
        if len(types)!=0 and not self.__list_equals(result.types, types):
            logging.error('Data type inconsistency for input setup: ' +
                     str(types) + ' - ' +
                     str(result.types))
            return None
        # If the data was consistent, 
        result.names = variables
        self.__input_config[result.id] = result
        return serialize.DataObject.create_empty(variables, result.id)
        
    def send_output_setup(self, variables, types=[], frequency=125):
        """
          This command is used during the setup procdure of the RTDE
          functionality.  It configures the RTDE server to generate output
          messages (with a desired frequency) containing an specific receipe.
          To do this, it constructs a binary packet to sent to the RTDE server
          as 

          |- frequency (int32_t) -|- variables names (String, comma separated) -|

          and send it to the RTDE socket using self.__sendAndReceive. 
          On sucess it sets the self.__output_config member variable
          to an instance of the serialize.DataConfig class and returns
          True. If it fails it returns False.
          Parameters:
          ----------
            variables: a list of strings.
                      a list with the names of the registers described in
                      one receipe to be readed. 
            types:     a list of types.
                      a list with the types of the registers to be readed
            frequency: unsigned int 
                      frequency of the output from RTDE server.
          Returns:
          -------
            Bolean, depending on the success or not for configuring
            the RTDE server to send messages with this receipe
        """
        cmd = Command.RTDE_CONTROL_PACKAGE_SETUP_OUTPUTS
        payload = struct.pack('>d', frequency)
        payload = payload + bytes(','.join(variables), 'utf-8')
        result = self.__sendAndReceive(cmd, payload)
        if len(types)!=0 and not self.__list_equals(result.types, types):
            logging.error('Data type inconsistency for output setup: ' +
                     str(types) + ' - ' +
                     str(result.types))
            return False
        result.names = variables
        self.__output_config = result
        return True
        
    def send_start(self):
        cmd = Command.RTDE_CONTROL_PACKAGE_START
        success = self.__sendAndReceive(cmd)
        if success:
            logging.info('RTDE synchronization started')
            self.__conn_state = ConnectionState.STARTED
        else:
            logging.error('RTDE synchronization failed to start')
        return success
        
    def send_pause(self):
        cmd = Command.RTDE_CONTROL_PACKAGE_PAUSE
        success = self.__sendAndReceive(cmd)
        if success:
            logging.info('RTDE synchronization paused')
            self.__conn_state = ConnectionState.PAUSED
        else:
            logging.error('RTDE synchronization failed to pause')
        return success

    def send(self, input_data):
        if self.__conn_state != ConnectionState.STARTED:
            logging.error('Cannot send when RTDE synchronization is inactive')
            return
        if input_data.recipe_id not in self.__input_config:
            logging.error('Input configuration id not found: ' + str(input_data.recipe_id))
            return
        config = self.__input_config[input_data.recipe_id]
        return self.__sendall(Command.RTDE_DATA_PACKAGE, config.pack(input_data))

    def receive(self):
        """
        Description:
        -----------
            This function test the configuration and the connection. then
            calls and returns  self.__recv(Command.RTDE_DATA_PACKAGE)
            This returns a serialize.DataConfig.unpack that returns
            serialize.DataObject.unpack 
        Parameters:
        ----------
            None
        Returns:
        --------
          Returns the same that self.__unpack_data_package() under
                  self.__output_config. This is serialize.DataConfig.unpack
                  which is a serialize.DataObject.unpack that is a
                  serialize.DataObject
        """
        if self.__output_config is None:
            logging.error('Output configuration not initialized')
            return None
        if self.__conn_state != ConnectionState.STARTED:
            logging.error('Cannot receive when RTDE synchronization is inactive')
            return None
        return self.__recv(Command.RTDE_DATA_PACKAGE)

    def send_message(self, message, source = "Python Client", type = serialize.Message.INFO_MESSAGE):
        cmd = Command.RTDE_TEXT_MESSAGE
        fmt = '>B%dsB%dsB' % (len(message), len(source))
        payload = struct.pack(fmt, len(message), message, len(source), source, type)
        return self.__sendall(cmd, payload)

    def __on_packet(self, cmd, payload):
        """
          This function serves as a wrapper of different deserialization
          methods which return an instance of a specific class representing the
          data of the payload. Depending on the cmd paramenter this method will
          interpret the payload data in a different way, returning also a
          different class instance.

        Parameters:
        -----------
          cmd:  uint8_t
                a char containting the type of command for the RTDE protocol
          payload: binary string

        Returns:
        -------
          Returns an instance of a class represeing the payload data.

        """
        if cmd == Command.RTDE_REQUEST_PROTOCOL_VERSION:
            print("sending command RTDE_REQUEST_PROTOCOL_VERSION:")
            # returns a bolean
            return self.__unpack_protocol_version_package(payload)
        elif cmd == Command.RTDE_GET_URCONTROL_VERSION:
            print("sending command RTDE_GET_URCONTROL_VERSION:")
            # returns an instance of serialize.ControlVersion class
            return self.__unpack_urcontrol_version_package(payload)
        elif cmd == Command.RTDE_TEXT_MESSAGE:
            #returns an instance of serialize.Message class
            return self.__unpack_text_message(payload)
        elif cmd == Command.RTDE_CONTROL_PACKAGE_SETUP_OUTPUTS:
            #returns an instance of serialize.DataConfig
            return self.__unpack_setup_outputs_package(payload)
        elif cmd == Command.RTDE_CONTROL_PACKAGE_SETUP_INPUTS:
            return self.__unpack_setup_inputs_package(payload)
        elif cmd == Command.RTDE_CONTROL_PACKAGE_START:
            return self.__unpack_start_package(payload)
        elif cmd == Command.RTDE_CONTROL_PACKAGE_PAUSE:
            return self.__unpack_pause_package(payload)
        elif cmd == Command.RTDE_DATA_PACKAGE:
            return self.__unpack_data_package(payload, self.__output_config)
        else:
            logging.error('Unknown package command: ' + str(cmd))
            
    def __sendAndReceive(self, cmd, payload=b''):
        """
        Description:
        -----------
          This function is a wrapper for self.__sendall and self.__recv.
          It calls the first and then the second, returning the returned
          value of the second one.
        Parameters:
        ----------
            cmd:        char
                      a char containg the first byte of the message
            payload:  a bynary string 
                      the payload of the message. You must known the
                      protocol to understant what this is.
        Returns:
        -------
          ?
        """
        if self.__sendall(cmd, payload):
            return self.__recv(cmd)
        else:
            return None
        
    def __sendall(self, command, payload=b''):
        """
        Description:
        -----------
          This function incapsulates the byte string payload into the RTDE
          protocol and send the data as soon the socket self.__sock is
          writable. The incapsulation process conssist in adding three bytes
          "at the left" of payload as in the figure

          |- uint16_t message lenght -|- uint8_t command -|- payload -|

          Parameters:
          ----------
            command:  char
                      a char containg the first byte of the message
            payload:  a bynary string 
                      the payload of the message. You must known the
                      protocol to understant what this is.
          Returns:
          -------
            Bolean indicating if the socket could send the message.
        """
        fmt = '>HB'
        size = struct.calcsize(fmt) + len(payload)
        buf = struct.pack(fmt, size, command) + payload
        
        if self.__sock is None:
            logging.error('Unable to send: not connected to Robot')
            return False
        
        _, writable, _ = select.select([], [self.__sock], [], DEFAULT_TIMEOUT)
        if len(writable):
# Unlike Socket.send, Socket.sendall will continue to send data until eithr all
# data has been sent or an error occurs. It returns None on success. On error
# an exception is raised, there is no way to determine how much data, if any,
# was sent.
            self.__sock.sendall(buf)
            return True
        else:
            self.__trigger_disconnected()
            return False
        
    def has_data(self):
        """
        Description:
        -----------
          Returns if the Layer 4 buffer of the socket self.__sock 
          has data to be readed.

        Parameters:
        ----------
            None
        Returns:
        -------
            Bolean.
        """
        timeout = 0
        readable, _, _ = select.select([self.__sock], [], [], timeout)
        return len(readable)!=0
        
    def __recv(self, command):
        """
        Description:
        -----------
          If we are connected to URControl, this functions do the following
          1) waits for the readability of the socket self.__sock,
          2) when self.sock is readable, call __sock.recv and store the data
             available in the socket's buffer in the local varaible "more".
          3) If there is no data available in the socket's buffer, then, or it
             received a FIN or RST  TCP packet, or timeout. So disconnect by
             calling self.__trigger_disconnected(), and return None.
          4) If the socket receives something, its buffer has that something,
             which is stored in $more and appended to self.__buf.
              ATTENTION) for one reason, self.__buf is not initialized here,
                         it could has something inside. It is initialled in
                         connect.
          5) The self.__buf buffer will be filled up with pieces of data
             received from the socket until its size becomes greater than 3
             bytes.
          6) When we have $more that 3 bytes, we look at the first 3 bytes of
             self.__buf. The first two bytes contain a uint16_t which is stored
             in packet_header.size, the third byte has a uint8_t which is
             stored in packet_header.command.
          7) For several reasons, the socket's internal buffer may contain more
             that a single packet. If that happens, the following proposition
             is True len(self.__buf) >= packet_header.size. If that is
             verified, necessary there was in the buffer a first packet and a
             piece of a second packet or more. The variable packet will refer
             to the content of the packet (without the 3 first bytes).  The
             variable self.__buf will refer to the rest. 
          8) The content of packet is deserialized in
             self.__on_packet(command,packet). This function is a sort of
             switch-case, that calls a specific deserializing algorithm
             depending on the parameter command. This functions waits of an
             specific number of bytes, if not returns None, which is returned
             by this function.
          9) If len(self.__buf[packet_header.size:]) == 0, return that that was
             returned by __on_packet.
        Parameters:
        ----------
          command:  uint8_t
                  a character representing the packet type that we want to
                  retrieve from the connection with URControl.
        Returns:
        --------
          A class containing the last message received which correspint thwith
          thw specified by command paramenter or None in case that the message
          was not correctly received.
        """
        while self.is_connected():
            readable, _, _ = select.select([self.__sock], [], [], DEFAULT_TIMEOUT)
            if len(readable):
                more = self.__sock.recv(4096)
                if len(more) == 0:
                    self.__trigger_disconnected()
                    return None

                self.__buf = self.__buf + more
                
            # unpack_from requires a buffer of at least 3 bytes
            while len(self.__buf) >= 3:
                # Attempts to extract a packet
                # returns a ControlHeader instance with attributes command and size.
                packet_header = serialize.ControlHeader.unpack(self.__buf)
                # here we have packet_header.size == 3 + packet length

                # does buffer contain more than specified in the header?
                if len(self.__buf) >= packet_header.size:
                  # then, necessarily, the buffer contains a new packet
                  # starting at the packet_header.size-th byte.
                    packet, self.__buf = self.__buf[3:packet_header.size], self.__buf[packet_header.size:]
                  # the actual packet is referenced by packet.
                  # The new packet is referenced by self.__buf
                    data = self.__on_packet(packet_header.command, packet)
                    if packet_header.command == command and len(self.__buf) == 0:
                        return data
                    if packet_header.command == command and len(self.__buf) != 0:
                        logging.info('skipping package')
                else:
                    break
        return None
    
    def __trigger_disconnected(self):
        logging.info("RTDE disconnected")
        self.disconnect() #clean-up the socket
    
    def __unpack_protocol_version_package(self, payload):
        """
        Description:
        ----------
          This function will unpack the output message generated by RTDE after
          it receive a RTDE_REQUEST_PROTOCOL_VERSION command. So  it
          deserializes a single bolean in the payload. The deserialization
          process is done through an instance of the class
          serialize.ReturnValue.  The function returns the only member variable of
          this instance.
        Parameters:
        ----------
          payload: binary string
        Returns:
        -------
           a Bolean 
        """
        if len(payload) != 1:
            logging.error('RTDE_REQUEST_PROTOCOL_VERSION: Wrong payload size')
            return None
        result = serialize.ReturnValue.unpack(payload)
        return result.success
    
    def __unpack_urcontrol_version_package(self, payload):
        """
          Deserializes a binary string of 16 bytes containing the version of
          the RTDE, and returns an instance of the class
          serialize.ControlVersion containing this data.
        Parameters:
        ----------
            payload: binary string
        Returns:
        ------
            an instance of the serialize.ControlVersion class with the payload
            data
        """
        if len(payload) != 16:
            logging.error('RTDE_GET_URCONTROL_VERSION: Wrong payload size')
            return None
        version = serialize.ControlVersion.unpack(payload)
        return version
    
    def __unpack_text_message(self, payload):
        """
          Deserializes a payload of bytes containing a string and returns an
          instance of the class serialize.Message representing this data.
        Parameters:
        ----------
            payload: binary string
        Returns:
        ------
            an instance of the serialize.Message class with the payload data
        """
        if len(payload) < 1:
            logging.error('RTDE_TEXT_MESSAGE: No payload')
            return None
        msg = serialize.Message.unpack(payload)
        if(msg.level == serialize.Message.EXCEPTION_MESSAGE or 
           msg.level == serialize.Message.ERROR_MESSAGE):
            logging.error(msg.source + ': ' + msg.message)
        elif msg.level == serialize.Message.WARNING_MESSAGE:
            logging.warning(msg.source + ': ' + msg.message)
        elif msg.level == serialize.Message.INFO_MESSAGE:
            logging.info(msg.source + ': ' + msg.message)
    
    def __unpack_setup_outputs_package(self, payload):
        """
        Description:
        -----------
          This function is used to unpack the RTDE output message after
          receiving a RTDE_CONTROL_PACKAGE_SETUP_OUTPUTS command.
          Deserializes a payload of bytes  and returns an instance of the class
          serialize.DataConfig representing this data.
        Parameters:
        ----------
            payload: binary string
        Returns:
        ------
            an instance of the serialize.DataConfig class with the payload data
        """
        if len(payload) < 1:
            logging.error('RTDE_CONTROL_PACKAGE_SETUP_OUTPUTS: No payload')
            return None
        output_config = serialize.DataConfig.unpack_recipe(payload)
        return output_config
    
    def __unpack_setup_inputs_package(self, payload):
        if len(payload) < 1:
            logging.error('RTDE_CONTROL_PACKAGE_SETUP_INPUTS: No payload')
            return None
        input_config = serialize.DataConfig.unpack_recipe(payload)
        return input_config
    
    def __unpack_start_package(self, payload):
        if len(payload) != 1:
            logging.error('RTDE_CONTROL_PACKAGE_START: Wrong payload size')
            return None
        result = serialize.ReturnValue.unpack(payload)
        return result.success
    
    def __unpack_pause_package(self, payload):
        if len(payload) != 1:
            logging.error('RTDE_CONTROL_PACKAGE_PAUSE: Wrong payload size')
            return None
        result = serialize.ReturnValue.unpack(payload)
        return result.success
    
    def __unpack_data_package(self, payload, output_config):
        if output_config is None:
            logging.error('RTDE_DATA_PACKAGE: Missing output configuration')
            return None
        output = output_config.unpack(payload)
        return output
    
    def __list_equals(self, l1, l2):
        if len(l1) != len(l2):
            return False
        for i in range(len((l1))):
            if l1[i] != l2[i]:
                return False
        return True
    
