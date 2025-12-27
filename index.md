
<link rel="shortcut icon" type="image/x-icon" href="icon.ico">

<style>
.lb-backdrop{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,.72);
  display:none;
  align-items:center;
  justify-content:center;
  z-index:9999;
  padding:24px;
}

.lb-backdrop[aria-hidden="false"]{ display:flex; }

.lb-dialog{
  width:min(1100px, 100%);
  background:rgba(255,255,255,.98);
  border-radius:16px;
  overflow:hidden;
  box-shadow:0 12px 40px rgba(0,0,0,.35);
  display:flex;
  flex-direction:column;
}

.lb-topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  padding:10px 12px;
  border-bottom:1px solid rgba(0,0,0,.08);
}

.lb-title{
  font-size:.95rem;
  opacity:.85;
  white-space:nowrap;
  overflow:hidden;
  text-overflow:ellipsis;
}

.lb-close{
  border:0;
  background:transparent;
  font-size:22px;
  line-height:1;
  padding:6px 10px;
  border-radius:10px;
  cursor:pointer;
}
.lb-close:focus{ outline:2px solid #4c9ffe; outline-offset:2px; }

.lb-stage{
  position:relative;
  background:rgba(0,0,0,.03);
}

.lb-img{
  width:100%;
  height:min(72vh, 720px);
  object-fit:contain;
  display:block;
}

.lb-caption{
  padding:10px 12px 14px;
  font-size:.95rem;
  border-top:1px solid rgba(0,0,0,.08);
}

.lb-nav{
  position:absolute;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:space-between;
  pointer-events:none;
  padding:0 8px;
}

.lb-btn{
  pointer-events:auto;
  border:0;
  cursor:pointer;
  padding:10px 12px;
  border-radius:12px;
  background:rgba(255,255,255,.92);
  box-shadow:0 2px 8px rgba(0,0,0,.18);
  font-size:16px;
}
.lb-btn:focus{ outline:2px solid #4c9ffe; outline-offset:2px; }

.lb-open{
  display:inline-block;
  border:0;
  cursor:pointer;
  padding:10px 14px;
  border-radius:12px;
  background:rgba(0,0,0,.06);
  box-shadow:0 1px 4px rgba(0,0,0,.12);
  font-size:1rem;
}
.lb-open:focus{ outline:2px solid #4c9ffe; outline-offset:2px; }

@media (prefers-color-scheme: dark){
  .lb-open{ background:rgba(255,255,255,.10); color:inherit; }
  .lb-dialog{ background:rgba(20,20,20,.98); color:inherit; }
  .lb-topbar, .lb-caption{ border-color:rgba(255,255,255,.10); }
  .lb-stage{ background:rgba(255,255,255,.06); }
  .lb-btn{ background:rgba(30,30,30,.92); color:inherit; }
}
</style>

<figure>
  <img
    src="./img/banner.png"
    alt="Intercom System"
    width="40%">
</figure>

# Introduction

Commercial videointercom systems are found in front of most buildings, public or residential. While older models use analog systems to call and display video, these are gradually phased out, as cheaper digital systems take over market and use modern TCP/IP networking.

One such device is the Hikvision DS-KV6113-WPE1 IP Video Intercom system, which aims to bring TCP/IP and video calling to affordable standards. As with most cheap devices, there has to be a corner-cut in costs somewhere, and this article will hopefully shed some light on the current state of security this particular model implements.

<img src="./img/front_view.png" width="80%">

# PCB Analysis

The device has 2 PCBs that are connected via a mezzanine connector. The black PCB holds the majority of the connectors, including the RJ45 and exterior-facing connectors, as well as the PoE and voltage regulation circuitry.

The microprocessor is an HK-2019-A16B TRXM7500, specially made for Hikvision. The flash IC, MX25L25645G holds 256Mb of memory and holds the entire firmware of the device.

## PCB gallery

<button class="lb-open" type="button" id="open-pcb-gallery">
  Open PCB photo viewer
</button>

<div class="lb-backdrop" id="lightbox" role="dialog" aria-modal="true" aria-hidden="true">
  <div class="lb-dialog" role="document">
    <div class="lb-topbar">
      <div class="lb-title" id="lb-title">Image</div>
      <button class="lb-close" type="button" id="lb-close" aria-label="Close">×</button>
    </div>

    <div class="lb-stage">
      <img class="lb-img" id="lb-img" src="" alt="">
      <div class="lb-nav">
        <button class="lb-btn" type="button" id="lb-prev" aria-label="Previous image">‹ Prev</button>
        <button class="lb-btn" type="button" id="lb-next" aria-label="Next image">Next ›</button>
      </div>
    </div>

    <div class="lb-caption" id="lb-caption">CAPTION PLACEHOLDER</div>
  </div>
</div>

<script>
(() => {
  const pcbGallery = [
    { src: "./img/back_shield.png",     caption: "CAPTION PLACEHOLDER" },
    { src: "./img/connection.png",      caption: "CAPTION PLACEHOLDER" },
    { src: "./img/ethernet_back_2.png", caption: "CAPTION PLACEHOLDER" },
    { src: "./img/small_pcb.png",       caption: "CAPTION PLACEHOLDER" },
    { src: "./img/sensor_flash.png",    caption: "CAPTION PLACEHOLDER" },
    { src: "./img/mcu_closeup.png",     caption: "CAPTION PLACEHOLDER" },
  ];

  const openBtn  = document.getElementById("open-pcb-gallery");
  const lb       = document.getElementById("lightbox");
  const imgEl    = document.getElementById("lb-img");
  const titleEl  = document.getElementById("lb-title");
  const capEl    = document.getElementById("lb-caption");
  const closeBtn = document.getElementById("lb-close");
  const prevBtn  = document.getElementById("lb-prev");
  const nextBtn  = document.getElementById("lb-next");

  let index = 0;
  let lastActive = null;

  function preload(i){
    const item = pcbGallery[i];
    if (!item) return;
    const im = new Image();
    im.src = item.src;
  }

  function render(){
    const item = pcbGallery[index];
    imgEl.src = item.src;
    imgEl.alt = item.caption || "Gallery image";
    capEl.textContent = item.caption || "";
    titleEl.textContent = `PCB Gallery — ${index + 1} / ${pcbGallery.length}`;

    preload((index + 1) % pcbGallery.length);
    preload((index - 1 + pcbGallery.length) % pcbGallery.length);
  }

  function openAt(i){
    lastActive = document.activeElement;
    index = (i + pcbGallery.length) % pcbGallery.length;
    render();
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    closeBtn.focus();
  }

  function close(){
    lb.setAttribute("aria-hidden", "true");
    imgEl.src = "";
    document.body.style.overflow = "";
    if (lastActive && typeof lastActive.focus === "function") lastActive.focus();
  }

  function prev(){
    index = (index - 1 + pcbGallery.length) % pcbGallery.length;
    render();
  }

  function next(){
    index = (index + 1) % pcbGallery.length;
    render();
  }

  openBtn?.addEventListener("click", () => openAt(0));
  closeBtn?.addEventListener("click", close);
  prevBtn?.addEventListener("click", prev);
  nextBtn?.addEventListener("click", next);

  lb?.addEventListener("click", (e) => {
    if (e.target === lb) close();
  });

  document.addEventListener("keydown", (e) => {
    if (lb.getAttribute("aria-hidden") === "true") return;

    if (e.key === "Escape") { e.preventDefault(); close(); }
    if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
    if (e.key === "ArrowRight") { e.preventDefault(); next(); }
  });
})();
</script>
