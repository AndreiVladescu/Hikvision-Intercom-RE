
<link rel="shortcut icon" type="image/x-icon" href="icon.ico">

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.css">

<style>
.pcb-swiper{
  max-width: 980px;
  margin: 1rem auto 0.75rem;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0,0,0,.10);
  background: rgba(0,0,0,.02);
}

.pcb-swiper .swiper-slide{
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(0,0,0,.02);
}

.pcb-swiper .swiper-zoom-container{
  width:100%;
  height: min(72vh, 760px);
  display:flex;
  align-items:center;
  justify-content:center;
}

.pcb-swiper img{
  width:100%;
  height:100%;
  object-fit: contain;
  display:block;
  user-select: none;
  -webkit-user-drag: none;
}

.pcb-gallery-controls{
  max-width: 980px;
  margin: 0 auto 2rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
}

.pcb-gallery-controls button{
  border:0;
  cursor:pointer;
  padding:10px 14px;
  border-radius:12px;
  background: rgba(0,0,0,.06);
  box-shadow: 0 1px 4px rgba(0,0,0,.12);
  font-size: 1rem;
}

.pcb-gallery-controls button:focus{
  outline:2px solid #4c9ffe;
  outline-offset:2px;
}

#pcb-caption{
  flex: 1;
  text-align:center;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(0,0,0,.03);
  box-shadow: inset 0 0 0 1px rgba(0,0,0,.08);
  font-size: 0.95rem;
  overflow:hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (prefers-color-scheme: dark){
  .pcb-swiper{ background: rgba(255,255,255,.06); }
  .pcb-swiper .swiper-slide{ background: rgba(255,255,255,.06); }
  .pcb-gallery-controls button{ background: rgba(255,255,255,.10); color: inherit; }
  #pcb-caption{ background: rgba(255,255,255,.08); box-shadow: inset 0 0 0 1px rgba(255,255,255,.12); }
}
</style>

<script src="https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.js" defer></script>
<script src="./js/pcb-gallery.js" defer></script>

# Introduction

Commercial videointercom systems are found in front of most buildings, public or residential. While older models use analog systems to call and display video, these are gradually phased out, as cheaper digital systems take over market and use modern TCP/IP networking.

One such device is the Hikvision DS-KV6113-WPE1 IP Video Intercom system, which aims to bring TCP/IP and video calling to affordable standards. As with most cheap devices, there has to be a corner-cut in costs somewhere, and this article will hopefully shed some light on the current state of security this particular model implements.

<img src="./img/front_view.png" width="50%">

# PCB Analysis

The device has 2 PCBs that are connected via a mezzanine connector. The black PCB holds the majority of the connectors, including the RJ45 and exterior-facing connectors, as well as the PoE and voltage regulation circuitry.

The microprocessor is an HK-2019-A16B TRXM7500, specially made for Hikvision. The flash IC, MX25L25645G holds 256Mb of memory and holds the entire firmware of the device.

<div class="swiper pcb-swiper" id="pcb-swiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide" data-caption="CAPTION PLACEHOLDER">
      <div class="swiper-zoom-container">
        <img src="./img/back_shield.png" alt="CAPTION PLACEHOLDER" loading="lazy">
      </div>
    </div>

    <div class="swiper-slide" data-caption="CAPTION PLACEHOLDER">
      <div class="swiper-zoom-container">
        <img src="./img/connection.png" alt="CAPTION PLACEHOLDER" loading="lazy">
      </div>
    </div>

    <div class="swiper-slide" data-caption="CAPTION PLACEHOLDER">
      <div class="swiper-zoom-container">
        <img src="./img/ethernet_back_2.png" alt="CAPTION PLACEHOLDER" loading="lazy">
      </div>
    </div>

    <div class="swiper-slide" data-caption="CAPTION PLACEHOLDER">
      <div class="swiper-zoom-container">
        <img src="./img/small_pcb.png" alt="CAPTION PLACEHOLDER" loading="lazy">
      </div>
    </div>

    <div class="swiper-slide" data-caption="CAPTION PLACEHOLDER">
      <div class="swiper-zoom-container">
        <img src="./img/sensor_flash.png" alt="CAPTION PLACEHOLDER" loading="lazy">
      </div>
    </div>

    <div class="swiper-slide" data-caption="CAPTION PLACEHOLDER">
      <div class="swiper-zoom-container">
        <img src="./img/mcu_closeup.png" alt="CAPTION PLACEHOLDER" loading="lazy">
      </div>
    </div>
  </div>
</div>

<div class="pcb-gallery-controls">
  <button type="button" id="pcb-prev" aria-label="Previous image">‹ Prev</button>
  <div id="pcb-caption">CAPTION PLACEHOLDER</div>
  <button type="button" id="pcb-next" aria-label="Next image">Next ›</button>
</div>

# Firmware Analysis

## Initial sniffing

Chip-off extraction was performed on the MX25L25645G flash IC, and the contents were read using a flash reader. Afterwards, `binwalk3` was used to extract the data: two JFFS partitions and a CramFS partition were found, alongside a U-Boot bootloader.

At the U-Boot offset we can find a lot of interesting information, some of which would probably be printed on the debug UART console, if the console is available:

- console settings and bootargs: `console=ttyS0,115200`
- TFTP info to download new image: `Download Filename '%s'`
- IPv4 of the device, server and gateway
- the Linux Kernel to be loaded: `uImage`
- bootargs of the images to be loaded: `default=cramfsload 0x80400000 uImage cramfsload 0x80800000 ramdisk.gz`

The uImage is found on the CramFS partition, and it's a `Linux-3.18.20`. The ramdisk has a ubuntu image, with it's own rootfs on it and binaries.

The JFFS partition at `0x60438` holds only the `dev.bin` binary, and the other JFFS at `0xA02E0` holds a backup partition, with configuration data and crypto stuff, such as server keys and certificates. However, the CramFS partition at `0x1E0000` hides the bulk of the system files.

## Further digging

After the initial reccoinassance, the CramFS partition was targeted, as it holds a lot of interesting files:

- device tree blobs `DSXXXX`
- start script `start.sh`
- the ramdisk & Linux image
- audio files
- DSP & BSP files (for image sensor, maybe?)
- Open source license files
- an `.xls` device list config file
- the digicapkeyArm.ko kernel module, important for HikVision security updates
- web server files
- `visdoor` folder containing `hicore` binary
- other binaries & config files

The ramdisk decompressed image contains the linux regular file system:

```
.
├── bin
├── etc
│   ├── dropbear
│   ├── init.d
│   ├── iscsi
│   │   └── ifaces
│   ├── rcS.d
│   └── udev
│       └── rules.d
├── lib
├── sbin
├── usr
│   ├── bin
│   └── sbin
└── var
    └── run

17 directories
```
 
