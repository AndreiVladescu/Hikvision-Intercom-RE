(() => {
  const swiperEl = document.getElementById("pcb-swiper");
  const prevEl = document.getElementById("pcb-prev");
  const nextEl = document.getElementById("pcb-next");
  const captionEl = document.getElementById("pcb-caption");

  if (!swiperEl || !prevEl || !nextEl || !captionEl || typeof Swiper === "undefined") return;

  const getActiveCaption = (swiper) => {
    const slide = swiper.slides[swiper.activeIndex];
    const caption = slide?.dataset?.caption || "CAPTION PLACEHOLDER";
    return caption;
  };

  const applyCaption = (swiper) => {
    const caption = getActiveCaption(swiper);
    captionEl.textContent = caption;
    const img = swiper.slides[swiper.activeIndex]?.querySelector("img");
    if (img) img.alt = caption;
  };

  const swiper = new Swiper(swiperEl, {
    slidesPerView: 1,
    spaceBetween: 16,
    loop: true,
    speed: 220,
    preloadImages: false,
    lazy: {
      loadPrevNext: true,
    },
    keyboard: {
      enabled: true,
      onlyInViewport: false,
    },
    navigation: {
      prevEl,
      nextEl,
    },
    zoom: {
      maxRatio: 5,
      toggle: true,
      panOnMouseMove: true,
    },
    on: {
      init() {
        applyCaption(this);
      },
      slideChangeTransitionEnd() {
        applyCaption(this);
      },
    },
  });

  applyCaption(swiper);
})();

