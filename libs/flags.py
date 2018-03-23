
# Bundle Processing Control Flags v6
class BPCF_v6:
    # https://datatracker.ietf.org/doc/rfc5050/?include_text = 1
    IS_FRAGMENT = 0x00001
    IS_ADMNISTRATIVE_RECORD = 0x00002
    MUST_NOT_FRAGMENT = 0x00004
    CUSTODY_TRANSFER_REQUESTED = 0x00008
    SINGLETON_ENDPOINT = 0x00010
    ACKNOWLEDGEMENT_REQUESTED = 0x00020
    # 7th bit RESERVED = 0x00004
    BULK_PRIORITY = 0x00000
    NORMAL_PRIORITY = 0x00080
    EXPEDITED_PRIORITY = 0x00100
    # priority with bits 7 and 8 set (11) RESERVED = 0x00180
    # 9 - 13 bits reserved
    REPORT_RECEPTION = 0x04000
    CUSTODY_ACCEPTANCE = 0x08000
    REPORT_FORWARDING = 0x10000
    REPORT_DELIVERY = 0x20000
    REPORT_DELETION = 0x40000

    # this probably do not belongs here. TODO
    # https://tools.ietf.org/html/rfc5050#section-4.5.2
    BLOCK_TYPE_PAYLOAD = 1

# Extension block flags
class EBF:
    NONE = 0x00
    MUST_BE_REPLICATED = 0x01
    REPORT_IF_UNPROC = 0x02
    DELETE_BUNDLE_IF_UNPROC = 0x04
    LAST_BLOCK = 0x08
    DISCARD_IF_UNPROC = 0x10
    FWD_UNPROC = 0x20
    HAS_EID_REF_FIELD = 0x40

class MessageCodeType:
    DATA_SEGMENT = 0x1
    ACK_SEGMENT = 0x2
    REFUSE_BUNDLE = 0x3
    KEEPALIVE = 0x4
    SHUTDOWN = 0x5
    LENGTH = 0x6