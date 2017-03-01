# EAeDIP128-6 Python Driver
#
# Created: March 2015
#      by: Manolo Broseta at ALBA Computing Division
#

Alba_logo = [ 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x40, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x01, 0x04, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xfc, 0x07, 0x00, 0x00, 0x0c, 0x00, 0x00,
   0x80, 0x03, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0x1f, 0x00,
   0x00, 0x2e, 0x00, 0x00, 0xc0, 0x01, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xbf, 0x3f, 0x00, 0x00, 0x2e, 0x00, 0x00, 0xc0, 0x81, 0x03, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x80, 0x0f, 0x3c, 0x00, 0x00, 0x4e, 0x00, 0x00,
   0xc0, 0x81, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x03, 0x78, 0x00,
   0x00, 0x17, 0x00, 0x00, 0xe0, 0xc0, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xc0, 0x03, 0x78, 0x00, 0x00, 0x56, 0x00, 0x00, 0xe0, 0xc0, 0x01, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xc0, 0x03, 0xf0, 0x00, 0x00, 0x2f, 0x00, 0x00,
   0x70, 0xc0, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0xff, 0xff, 0x00,
   0x00, 0xb7, 0x00, 0xe0, 0xff, 0xff, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xe0, 0xff, 0xff, 0x00, 0x00, 0x37, 0x00, 0xe0, 0xff, 0xff, 0xff, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xc0, 0xff, 0x7f, 0x00, 0x80, 0x73, 0x00, 0xf0,
   0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x09, 0x25, 0x00,
   0x80, 0x77, 0x00, 0x80, 0x7c, 0xf9, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xe0, 0x01, 0x00, 0x00, 0x80, 0x73, 0x01, 0x00, 0x3c, 0x70, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xe0, 0x01, 0x00, 0x00, 0x80, 0x77, 0x00, 0x00,
   0x1c, 0x78, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x03, 0x00, 0x00,
   0x83, 0x71, 0x00, 0x00, 0x1c, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xc0, 0x03, 0x00, 0x80, 0xc3, 0xf3, 0x00, 0x00, 0x0e, 0x38, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x80, 0x07, 0x00, 0x80, 0x95, 0x65, 0x01, 0x00,
   0x0e, 0x1c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x1f, 0x00, 0xc0,
   0xc5, 0xe1, 0x00, 0x00, 0x0f, 0x1c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xff, 0xff, 0x80, 0xd4, 0x65, 0x01, 0x0e, 0x02, 0x14, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0xff, 0x2a, 0xdd, 0xe1, 0x00, 0xae,
   0x54, 0x51, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xff, 0x4a,
   0xee, 0xe2, 0x02, 0xa7, 0x23, 0x8f, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x9c, 0xe1, 0x00, 0x87, 0x07, 0x0f, 0x01, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5c, 0xc2, 0x02, 0xcb,
   0x03, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xb8, 0xe0, 0x80, 0xc3, 0x81, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x38, 0xc1, 0x81, 0xcb, 0x81, 0x03, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78, 0xc0, 0xc1, 0xe1,
   0x80, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x30, 0xc1, 0xc5, 0xc5, 0x80, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xe1, 0x01, 0x00, 0x00, 0x00, 0x60,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xe5, 0x04,
   0x00, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xc0, 0xe1, 0x00, 0x00, 0x00, 0x00, 0x70, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x73, 0xe1, 0xff, 0x1f, 0xf8, 0xf9,
   0xc3, 0x8f, 0xff, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x73, 0xe0,
   0xf7, 0x1d, 0xbc, 0xf3, 0xe3, 0x1d, 0xdf, 0x01, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x80, 0xbb, 0x80, 0xe1, 0x38, 0x0e, 0x63, 0x60, 0x38, 0x8e, 0x03,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x33, 0xc0, 0x61, 0x30, 0x06, 0x67,
   0x70, 0x30, 0x8e, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xbb, 0xc0,
   0x61, 0x30, 0xfe, 0x67, 0xf0, 0x3f, 0xc6, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x80, 0x27, 0x80, 0x60, 0x30, 0xbf, 0x65, 0xf4, 0x3f, 0x06, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x2b, 0xc0, 0x61, 0x30, 0x06, 0x62,
   0x3e, 0x00, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x0b, 0x80,
   0x61, 0x30, 0x06, 0x66, 0x74, 0x30, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x57, 0xc0, 0xe1, 0x38, 0x8e, 0xe3, 0x66, 0x38, 0x0e, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0xf0, 0xff, 0xfd, 0xfc, 0xe1,
   0xe7, 0x9f, 0x1f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x20,
   0xa9, 0x2a, 0xb8, 0x80, 0x81, 0x07, 0x0a, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00  ]

EM_Logo = [ 0x80, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xfc, 0x03, 0x00, 0x00, 0x0b, 0x00, 0x00,
   0x30, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0x0f, 0x00,
   0x80, 0x13, 0x00, 0x00, 0x38, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x80, 0x2f, 0x1f, 0x00, 0x80, 0x05, 0x00, 0x00, 0x18, 0x30, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x80, 0x07, 0x1c, 0x00, 0x80, 0x0b, 0x00, 0x00,
   0x18, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x03, 0x3c, 0x00,
   0x80, 0x13, 0x00, 0x00, 0x1c, 0x38, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xc0, 0x01, 0x38, 0x00, 0x80, 0x15, 0x00, 0x00, 0x0c, 0x18, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xc0, 0x01, 0x38, 0x00, 0xc0, 0x09, 0x00, 0x00,
   0x0e, 0x1c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0xef, 0x3d, 0x00,
   0xc0, 0x2a, 0x00, 0xf8, 0x7f, 0xff, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xe0, 0xff, 0x3f, 0x00, 0xc0, 0x0d, 0x00, 0xfc, 0xff, 0xff, 0x0f, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xe0, 0xff, 0x3f, 0x00, 0xc0, 0x1c, 0x00, 0xfc,
   0xff, 0xff, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x00, 0x00, 0x00,
   0xc0, 0x2d, 0x00, 0x00, 0x03, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xe0, 0x01, 0x00, 0x00, 0xc0, 0x1c, 0x00, 0x00, 0x03, 0x07, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0xe0, 0x01, 0x00, 0x00, 0xe0, 0x2d, 0x00, 0x80,
   0x03, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x01, 0x00, 0x80,
   0x61, 0x1c, 0x00, 0x80, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0xc0, 0x03, 0x00, 0xc0, 0x62, 0x39, 0x00, 0xc0, 0x81, 0x03, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x80, 0x03, 0x00, 0xe0, 0xe4, 0x5c, 0x00, 0xc0,
   0x81, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x0f, 0x00, 0xe0,
   0xe9, 0x18, 0x00, 0xc0, 0xc0, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xff, 0x7f, 0x15, 0x32, 0x39, 0x80, 0x55, 0x89, 0x92, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0x7f, 0xa2, 0x76, 0x58, 0xc0, 0x49,
   0x52, 0x94, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0x5d, 0x15,
   0xab, 0x38, 0xc0, 0x32, 0xa9, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x36, 0x78, 0x60, 0x71, 0xe0, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xa6, 0x30, 0xe0, 0x30,
   0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x2e, 0x70, 0x60, 0x39, 0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x4e, 0xb0, 0x70, 0x38, 0x70, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5c, 0x30, 0xb0, 0x18,
   0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x08, 0x70, 0xb1, 0x08, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x70, 0x38, 0x00, 0x00, 0x00, 0x00, 0x02,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xb0, 0x58, 0x00,
   0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xe0, 0x1c, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x2d, 0xdc, 0xf7, 0x81, 0x9f, 0x3f,
   0x7c, 0xfc, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x2c, 0x78,
   0x9e, 0xc3, 0xb9, 0x1f, 0xc6, 0x70, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xe0, 0x0e, 0x30, 0x0c, 0x43, 0x30, 0x02, 0x83, 0x31, 0x0c, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xe0, 0x16, 0x30, 0x0c, 0x63, 0x30, 0x03,
   0x83, 0x31, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60, 0x16, 0x18,
   0x0c, 0xe3, 0x3f, 0x82, 0xff, 0x31, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xe0, 0x04, 0x10, 0x0c, 0x63, 0x15, 0x63, 0xab, 0x30, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x0a, 0x30, 0x0c, 0x63, 0x20, 0x62,
   0x01, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x02, 0x10,
   0x0c, 0x63, 0x30, 0x63, 0x83, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0xc0, 0x04, 0x38, 0x0c, 0xc3, 0x30, 0x66, 0xc3, 0x30, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x05, 0xfc, 0xff, 0xcf, 0x1f, 0x3e,
   0xfe, 0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x40,
   0x92, 0x04, 0x07, 0x08, 0x3c, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00 ]

Face_image = [ 0x33, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
				0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
				0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
				0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf8, 0x00, 0x00, 0x00,
				0x00, 0x00, 0x00, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xff, 0x01,
				0x00, 0x00, 0x00, 0x00, 0xc0, 0xff, 0x01, 0x00, 0x00, 0x00, 0x00, 0xe0,
				0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xff, 0x00, 0x00, 0x00, 0x00,
				0x00, 0xf0, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf8, 0xff, 0x00, 0x00,
				0x00, 0x00, 0x00, 0xf8, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xf8, 0xff,
				0x00, 0x00, 0x00, 0x00, 0x00, 0xf8, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00,
				0xf8, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfc, 0x3f, 0x00, 0x00, 0x00,
				0x00, 0x00, 0xfc, 0x3f, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfc, 0x3f, 0x00,
				0x00, 0x00, 0x00, 0x00, 0xfc, 0xff, 0xc0, 0x4f, 0x00, 0x00, 0x00, 0xfc,
				0xff, 0xfb, 0x4f, 0x00, 0x00, 0x00, 0xfe, 0xff, 0xfb, 0x49, 0x00, 0x00,
				0x00, 0xfc, 0xff, 0xf3, 0x43, 0x00, 0x00, 0x00, 0xfc, 0xff, 0xf3, 0x8d,
				0x00, 0x00, 0x00, 0xfc, 0xff, 0xf3, 0x80, 0x00, 0x00, 0x00, 0xfc, 0xff,
				0xe3, 0x00, 0x00, 0x00, 0x00, 0xfc, 0xff, 0x03, 0x00, 0x00, 0x00, 0x00,
				0xf8, 0xff, 0x03, 0x00, 0x00, 0x00, 0x00, 0xf8, 0xff, 0x03, 0x00, 0x00,
				0x00, 0x00, 0xf8, 0xff, 0x03, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xff, 0x43,
				0x00, 0x00, 0x00, 0x00, 0xc0, 0xff, 0x83, 0x00, 0x00, 0x00, 0x00, 0xc0,
				0xff, 0x83, 0x01, 0x00, 0x00, 0x00, 0xc0, 0xff, 0x07, 0x01, 0x00, 0x00,
				0x00, 0xc0, 0xff, 0x07, 0x02, 0x00, 0x00, 0x00, 0xc0, 0xff, 0x07, 0x00,
				0x00, 0x00, 0x00, 0x80, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xff,
				0x0f, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xff, 0x07, 0x00, 0x00, 0x00, 0x00,
				0xc0, 0xff, 0x07, 0x00, 0x00, 0x00, 0x00, 0xe0, 0xff, 0x07, 0x00, 0x00,
				0x00, 0x00, 0xe0, 0xff, 0x07, 0x00, 0x00, 0x00, 0x00, 0xf0, 0xff, 0x07,
				0x00, 0x00, 0x00, 0x00, 0xfc, 0xff, 0x07, 0x02, 0x00, 0x00, 0x80, 0xff,
				0xff, 0x07, 0x07, 0x00, 0x00, 0xe0, 0xff, 0xff, 0xef, 0x07, 0x00, 0x00,
				0xf8, 0xff, 0xff, 0xff, 0x07, 0x00, 0x00, 0xfc, 0xff, 0xff, 0xff, 0x07,
				0x00, 0x00, 0xf8, 0xff, 0xff, 0xff, 0x03, 0x00, 0x00, 0xd0, 0xff, 0xf7,
				0xff, 0x05, 0x00, 0x00, 0xc0, 0xff, 0x7f, 0x7f, 0x0e, 0x00, 0x00, 0x80,
				0xfe, 0x9f, 0x3d, 0x1f, 0x00, 0x00, 0x00, 0xfc, 0xfd, 0xbf, 0x1f, 0x00,
				0x00, 0x00, 0xfc, 0xff, 0xbf, 0x1f, 0x00, 0x00, 0x04, 0xf8, 0xfc, 0x1f,
				0x1e, 0x00, 0x00, 0x00, 0x78, 0xcc, 0x03, 0x02, 0x00, 0x00, 0x00, 0x20,
				0xc8, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0xd0, 0x01, 0x00, 0x00, 0x00,
				0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00,
				0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80,
				0x00, 0x00, 0x00, 0x00 ]

Navigation_keys = [ 0xf7, 0xfb, 0xfd, 0xbe, 0xdf, 0xef, 0x77, 0x01, 0x00, 0x00, 0x10, 0x00,
					0x00, 0x80, 0x01, 0x00, 0x00, 0x10, 0x00, 0x00, 0x80, 0x01, 0x00, 0x18,
					0x10, 0x18, 0x00, 0x80, 0x01, 0x00, 0x1e, 0x10, 0x78, 0x00, 0x80, 0x01,
					0xc0, 0x1f, 0x10, 0xf8, 0x03, 0x80, 0x01, 0xf0, 0x1f, 0x18, 0xf8, 0x0f,
					0x80, 0x01, 0xfc, 0x1f, 0x10, 0xf8, 0x7f, 0x80, 0x01, 0xff, 0x1f, 0x18,
					0xf8, 0xff, 0x81, 0xc1, 0xff, 0x1f, 0x10, 0xf8, 0xff, 0x83, 0x01, 0xff,
					0x1f, 0x18, 0xf8, 0xff, 0x80, 0x01, 0xfc, 0x1f, 0x10, 0xf8, 0x1f, 0x80,
					0x01, 0xe0, 0x1f, 0x18, 0xf8, 0x07, 0x80, 0x01, 0x80, 0x1f, 0x10, 0xf8,
					0x01, 0x80, 0x01, 0x00, 0x1c, 0x18, 0x78, 0x00, 0x80, 0x01, 0x00, 0x00,
					0x10, 0x08, 0x00, 0x80, 0x01, 0x00, 0x00, 0x18, 0x00, 0x00, 0x80, 0xff,
					0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]