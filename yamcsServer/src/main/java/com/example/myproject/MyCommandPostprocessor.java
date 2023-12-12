package com.example.myproject;

import org.yamcs.YConfiguration;
import org.yamcs.cmdhistory.CommandHistoryPublisher;
import org.yamcs.commanding.PreparedCommand;
//import org.yamcs.tctm.CcsdsSeqCountFiller;
import org.yamcs.tctm.CommandPostprocessor;
//import org.yamcs.utils.ByteArrayUtils;

import java.nio.ByteBuffer;

/**
 * Component capable of modifying command binary before passing it to the link for further dispatch.
 * <p>
 * A single instance of this class is created, scoped to the link udp-out.
 * <p>
 * This is specified in the configuration file yamcs.myproject.yaml:
 * 
 * <pre>
 * ...
 * dataLinks:
 *   - name: udp-out
 *     class: org.yamcs.tctm.UdpTcDataLink
 *     stream: tc_realtime
 *     host: localhost
 *     port: 10025
 *     commandPostprocessorClassName: com.example.myproject.MyCommandPostprocessor
 * ...
 * </pre>
 */
public class MyCommandPostprocessor implements CommandPostprocessor {

    private CommandHistoryPublisher commandHistory;
    //private CcsdsSeqCountFiller seqFiller = new CcsdsSeqCountFiller();

    // Constructor used when this postprocessor is used without YAML configuration
    public MyCommandPostprocessor(String yamcsInstance) {
        this(yamcsInstance, YConfiguration.emptyConfig());
    }

    // Constructor used when this postprocessor is used with YAML configuration
    // (commandPostprocessorClassArgs)
    public MyCommandPostprocessor(String yamcsInstance, YConfiguration config) {
    }

    // Called by Yamcs during initialization
    @Override
    public void setCommandHistoryPublisher(CommandHistoryPublisher commandHistory) {
        this.commandHistory = commandHistory;
    }

    // Called by Yamcs *after* a command was submitted, but *before* the link handles it.
    // This method must return the (possibly modified) packet binary.
    @Override
    public byte[] process(PreparedCommand pc) {
        byte[] binary_raw = pc.getBinary();
        byte[] crc = crc_calc(binary_raw);
        byte[] binary = new byte[binary_raw.length+2];

        for (int i = 0; i < binary.length; i++){
            if (i < binary.length-2) {
                binary[i] = binary_raw[i];
            }
            else {
                binary[i] = crc[i-binary_raw.length+2];
            }
        }
        // Set CCSDS packet length
        /*ByteArrayUtils.encodeUnsignedShort(binary.length - 7, binary, 4);

        // Set CCSDS sequence count
        int seqCount = seqFiller.fill(binary);

        // Publish the sequence count to Command History. This has no special
        // meaning to Yamcs, but it shows how to store custom information specific
        // to a command.
        commandHistory.publish(pc.getCommandId(), "ccsds-seqcount", seqCount);*/

        // Since we modified the binary, update the binary in Command History too.    
        commandHistory.publish(pc.getCommandId(), PreparedCommand.CNAME_BINARY, binary);
        System.out.println("Command"+binary);
        return binary;
    }


    private static byte[] crc_calc(byte[] bytes){
        int crc = 0x0000;          // initial value
        int polynomial = 0x1021;   // 0001 0000 0010 0001  (0, 5, 12)
    
        for (byte b : bytes) {
            for (int i = 0; i < 8; i++) {
                boolean bit = ((b   >> (7-i) & 1) == 1);
                boolean c15 = ((crc >> 15    & 1) == 1);
                crc <<= 1;
                if (c15 ^ bit) crc ^= polynomial;
            }
        }

        crc &= 0xffff;
        return ByteBuffer.allocate(4).putInt(crc).array();
    }
}
