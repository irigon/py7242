import time
import struct

#### got from: git@gitlab.dtnsat.de:upcn/upcn.git

# BP Constants

# Default BPv6 flags
BUNDLE_V6_FLAG_IS_FRAGMENT = 0x00001
BUNDLE_V6_FLAG_ADMINISTRATIVE_RECORD = 0x00002
BUNDLE_V6_FLAG_MUST_NOT_FRAGMENT = 0x00004
BUNDLE_V6_FLAG_CUSTODY_TRANSFER_REQUESTED = 0x00008
BUNDLE_V6_FLAG_SINGLETON_ENDPOINT = 0x00010
BUNDLE_V6_FLAG_ACKNOWLEDGEMENT_REQUESTED = 0x00020
# Priority
BUNDLE_V6_FLAG_NORMAL_PRIORITY = 0x00080
BUNDLE_V6_FLAG_EXPEDITED_PRIORITY = 0x00100
# Reports
BUNDLE_V6_FLAG_REPORT_RECEPTION = 0x04000
BUNDLE_V6_FLAG_REPORT_CUSTODY_ACCEPTANCE = 0x08000
BUNDLE_V6_FLAG_REPORT_FORWARDING = 0x10000
BUNDLE_V6_FLAG_REPORT_DELIVERY = 0x20000
BUNDLE_V6_FLAG_REPORT_DELETION = 0x40000
# (Extension) block types
BUNDLE_BLOCK_TYPE_PAYLOAD = 1
BUNDLE_BLOCK_TYPE_CURRENT_CUSTODIAN = 5
BUNDLE_BLOCK_TYPE_PREVIOUS_NODE = 7
BUNDLE_BLOCK_TYPE_BUNDLE_AGE = 8
BUNDLE_BLOCK_TYPE_HOP_COUNT = 9
BUNDLE_BLOCK_TYPE_MAX = 255
# (Extension) block flags
BUNDLE_BLOCK_FLAG_NONE = 0x00
BUNDLE_BLOCK_FLAG_MUST_BE_REPLICATED = 0x01
BUNDLE_BLOCK_FLAG_REPORT_IF_UNPROC = 0x02
BUNDLE_BLOCK_FLAG_DELETE_BUNDLE_IF_UNPROC = 0x04
BUNDLE_BLOCK_FLAG_LAST_BLOCK = 0x08
BUNDLE_BLOCK_FLAG_DISCARD_IF_UNPROC = 0x10
BUNDLE_BLOCK_FLAG_FWD_UNPROC = 0x20
BUNDLE_BLOCK_FLAG_HAS_EID_REF_FIELD = 0x40

DEFAULT_OUTGOING_BUNDLE_FLAGS = (
    BUNDLE_V6_FLAG_SINGLETON_ENDPOINT |
    BUNDLE_V6_FLAG_NORMAL_PRIORITY
)

# TCPCL Constants
TCPCL_CONNECTION_FLAG_REQUEST_ACK = 0x01
TCPCL_CONNECTION_FLAG_REACTIVE_FRAGMENTATION = 0x02
TCPCL_CONNECTION_FLAG_ALLOW_REFUSAL = 0x04
TCPCL_CONNECTION_FLAG_REQUEST_LENGTH = 0x08

DEFAULT_TCPCL_CONNECTION_FLAGS = 0


# uPCN Command Constants
ROUTER_COMMAND_ADD = "1"
ROUTER_COMMAND_UPDATE = "2"
ROUTER_COMMAND_DELETE = "3"
ROUTER_COMMAND_QUERY = "4"

# Default EIDs
NULL_EID = "dtn:none"


def sdnv_encode(value):
    value = int(value)
    if value == 0:
        return b"\0"
    result = bytearray()
    while value != 0:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result[0] &= 0x7F
    return bytes(reversed(result))

def sdnv_read(buffer, offset=0):
    result = 0
    cur = 0x80
    while (cur & 0x80) != 0:
        cur = buffer[offset]
        offset += 1
        result <<= 7
        result |= (cur & 0x7F)
    return result, offset


def unix2dtn(unix_timestamp):
    return unix_timestamp - 946684800

def dtn2unix(dtn_timestamp):
    return dtn_timestamp + 946684800

def serialize_upcn_config_message(eid, cla_address,
                                  reachable_eids=None, contacts=None,
                                  config_type=ROUTER_COMMAND_ADD):
    # missing escaping has to be addresses in uPCN
    assert "(" not in "".join([eid, cla_address] + (reachable_eids or []))
    assert ")" not in "".join([eid, cla_address] + (reachable_eids or []))

    eid_list = (
        (
            "[" +
            ",".join("(" + eid + ")" for eid in reachable_eids) +
            "]"
        )
        if reachable_eids else ""
    )
    contact_list = (
        (
            "[" +
            ",".join(
                "{{{},{},{}}}".format(start, end, bitrate)
                for start, end, bitrate in contacts
            ) +
            "]"
        )
        if contacts else ""
    )

    return "{}({}):({}):{}:{};".format(
        config_type,
        eid,
        cla_address,
        eid_list,
        contact_list,
    ).encode("ascii")


def serialize_bundle(source_eid, destination_eid, payload,
                     report_to_eid=NULL_EID, custodian_eid=NULL_EID,
                     creation_timestamp=None, sequence_number=0,
                     lifetime=300, flags=DEFAULT_OUTGOING_BUNDLE_FLAGS,
                     fragment_offset=None, total_adu_length=None):

    # RFC 5050 header: https://tools.ietf.org/html/rfc5050#section-4.5
    # Build part before "primary block length"
    header_part1 = bytearray()
    header_part1.append(0x06)
    header_part1 += sdnv_encode(flags)

    # Build part after "primary block length"
    header_part2 = bytearray()

    # NOTE: This does not do deduplication (which is optional) currently.
    dictionary = bytearray()
    cur_dict_offset = 0
    for eid in (destination_eid, source_eid, report_to_eid, custodian_eid):
        scheme, ssp = eid.encode("ascii").split(b":", 1)
        dictionary += scheme + b"\0"
        header_part2 += sdnv_encode(cur_dict_offset)
        cur_dict_offset += len(scheme) + 1
        dictionary += ssp + b"\0"
        header_part2 += sdnv_encode(cur_dict_offset)
        cur_dict_offset += len(ssp) + 1

    if creation_timestamp is None:
        creation_timestamp = unix2dtn(time.time())
    header_part2 += sdnv_encode(creation_timestamp)
    header_part2 += sdnv_encode(sequence_number)
    header_part2 += sdnv_encode(lifetime)

    header_part2 += sdnv_encode(len(dictionary))
    header_part2 += dictionary

    if fragment_offset is not None and total_adu_length is not None:
        assert (flags & BUNDLE_V6_FLAG_IS_FRAGMENT) != 0
        header_part2 += sdnv_encode(fragment_offset)
        header_part2 += sdnv_encode(total_adu_length)

    # Add the length of all remaining fields as primary block length
    header = header_part1 + sdnv_encode(len(header_part2)) + header_part2

    # Build payload block
    # https://tools.ietf.org/html/rfc5050#section-4.5.2
    payload_block = bytearray()
    payload_block.append(BUNDLE_BLOCK_TYPE_PAYLOAD)
    payload_block += sdnv_encode(BUNDLE_BLOCK_FLAG_LAST_BLOCK)
    # Block length is the length of the remaining part of the block (PL data)
    payload_block += sdnv_encode(len(payload))
    payload_block += payload

    # NOTE: This does _not_ support extension blocks currently
    return header + payload_block


def make_contact(start_offset, end_offset, bitrate):
    cur_time = int(time.time())
    return (
        unix2dtn(cur_time + start_offset),
        unix2dtn(cur_time + end_offset),
        bitrate,
    )
