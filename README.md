# USB insight hub host

## Description

The [USB insight hub](https://github.com/Aeriosolutions/USB-Insight-HUB-Hardware) currently only has a Windows host app.

However, as it is open source and has a [documented protocol](https://github.com/Aeriosolutions/USB-Insight-HUB/blob/main/UIH%20Serial%20API%20v1_0.pdf), this aims to implement a Linux host.

## Features

- [ ] Multiple "screens" (different information layouts)
    - [x] VID+PID (can show both VID + PID if a dual USB2+3 hub is connected)
    - [ ] video4linux device node
    - [ ] serial device node
    - [ ] audio device ID/name/node
    - [ ] block device node
    - [ ] ethernet device name
    - [ ] transfer activity for disks
    - [ ] transfer activity for ethernet
- [x] Default priority for screens
- [ ] Configurable priority for screens
- [x] Screens are shown in the following way
    - Find all currently relevant screens; if there is only one, show it
    - If relevant screens have different priorities, discard all that are not at the highest found value    
      e.g.: If you have 4 screens with priorities 3, 3, 2 and 1, only keep the two screens with a priority of 3
    - Cycle through the left over screens at a regular interval
