TX_REGISTER_SIZE        = 63

REG_PACKET_TYPE         = 0  # value must always be 2
REG_HW_VERSION          = 1
REG_CPU_LOAD            = 2  # in %
REG_CPU_TEMP            = 3  # in degress C
REG_MEM_USED            = 4  # in %

REG_IP_1                = 10
REG_IP_2                = 11
REG_IP_3                = 12
REG_IP_4                = 13
REG_WLAN_IP_1           = 14
REG_WLAN_IP_2           = 15
REG_WLAN_IP_3           = 16
REG_WLAN_IP_4           = 17

REG_CAMERA_FLAGS        = 18
REG_SMS_FLAGS           = 19

REG_SCREEN_TAP          = 20
REG_SCREEN_TAP_X_POS_HB     = 21
REG_SCREEN_TAP_X_POS_LB     = 22
REG_SCREEN_TAP_Y_POS_HB     = 23
REG_SCREEN_TAP_Y_POS_LB     = 24
REG_WIFI_STATUS         = 25
REG_MAIL_STATUS         = 26
REG_SMS_STATUS          = 27

REG_RFID_STATUS         = 28
REG_RFID_TAG_CONTENT    = 29

TX_HEADER1              = 0x54
TX_HEADER2              = 0xfe


# Command constants
USE_CAMERA              = 200
CLOSE_CAMERA            = 201
START_FIND_FACE         = 202
STOP_FIND_FACE          = 203
FACE_FOUND              = 204
TAKE_SNAP_SHOT          = 205
TAKE_PREVIEW_IMAGE      = 208

USE_SMS                 = 210
SEND_SMS                = 211

SEND_MAIL               = 212
SEND_SNAPSHOT           = 213
PLAY_SOUND              = 214
STOP_SOUND              = 215
SHOW_IMAGE              = 216
SCREEN_TAPPED           = 217
WIFI_CONNECT            = 218
WIFI_DISCONNECT         = 219
RPI_REBOOT              = 220
RPI_SHUTDOWN            = 221
RPI_NEWRECORDFILE       = 222
RPI_RECORD_TO_RPI       = 223
RPI_SHOW_LOG_PLOT       = 224
EMAIL_CONFIG            = 225
EMAIL_SEND              = 226

# RFID byte codes
RPI_USE_RFID            = 227
RPI_CLOSE_RFID          = 228
RPI_RFID_BEEP           = 229
RPI_READ_RFID           = 230
RPI_WRITE_RFID          = 231
RPI_RFID_TAG_FOUND      = 232
RPI_RFID_READER_FOUND   = 233
RPI_SAY                 = 234
RPI_SET_TX_BUFFER       = 20

#Packet type On Envent
REG_PACKET_TYPE_ON_TAP     = 6
REG_PACKET_TYPE_KEY_VALUE  = 7