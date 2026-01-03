# BOS descriptor decoding thoughtstream

## Example bos_descriptors
00000000: 050f 2a00 0307 1002 0200 0000 0a10 0300  ..*.............
00000010: 0e00 010a 0a00 1410 0400 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000                 ..........

## Manual decode
bLength = 5
bDescriptorType = 0x0f
wTotalLength = 0x2a00
bNumDeviceCaps = 3

bLength = 7
bDescriptorType = 0x10
bDevCapabilityType = 0x02
Payload = 0x02000000

bLength = 10
bDescriptorType = 0x10
bDevCapabilityType = 0x03
Payload = 0x000e00010a0a00

bLength = 20
bDescriptorType = 0x10
bDevCapabilityType = 0x04 (Container ID!)
Payload = 0x0000000000000000000000000000000000
