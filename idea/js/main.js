/* =========================================================
   KKUMi 메인 페이지 스크립트
   ========================================================= */
document.addEventListener('DOMContentLoaded', () => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const won = n => n.toLocaleString('ko-KR') + '원';

  /* ---------- 토스트 ---------- */
  const toastEl = $('#toast');
  let toastTimer;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2400);
  }

  /* ---------- 꾸미 표정 바꾸기 ---------- */
  function setFace(el, expr, time) {
    el.dataset.kkumi = expr;
    el.innerHTML = Kkumi.svg(expr, { time });
  }

  /* ---------- 헤더 ---------- */
  const header = $('.site-header');
  window.addEventListener('scroll', () => header.classList.toggle('scrolled', scrollY > 10), { passive: true });

  const menuBtn = $('#menuBtn'), gnb = $('#gnb');
  menuBtn.addEventListener('click', () => {
    const open = gnb.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open);
  });
  $$('#gnb a').forEach(a => a.addEventListener('click', () => {
    gnb.classList.remove('open'); menuBtn.setAttribute('aria-expanded', false);
  }));

  /* ---------- 스크롤 등장 ---------- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: .12 });
  $$('.reveal').forEach(el => io.observe(el));

  /* ---------- 쓰담쓰담 ---------- */
  const pet = $('#petKkumi'), petFace = $('#petFace'), petHint = $('#petHint');
  const petLines = ['헤헤 기분 좋아요', '조금만 더 쓰다듬어 줘요', '이제 다시 공부하러 가볼까요?'];
  let petCount = 0, petTimer;
  pet.addEventListener('click', () => {
    setFace(petFace, 'love');
    pet.classList.remove('petted'); void pet.offsetWidth; pet.classList.add('petted');
    petHint.textContent = petLines[petCount++ % petLines.length];
    clearTimeout(petTimer);
    petTimer = setTimeout(() => { setFace(petFace, 'happy'); petHint.textContent = '꾸미를 눌러서 쓰담쓰담 해보세요'; }, 2200);
  });

  /* ---------- 폰 사용 시간 → 표정 ---------- */
  const range = $('#moodRange'), out = $('#moodOut'), moodFace = $('#moodFace'),
        moodState = $('#moodState'), push = $('#pushPreview'), pushText = $('#pushText'),
        device = $('.mood-device'), steps = $$('.mood-steps li');
  const levels = [
    { min: 0,  face: 'happy', state: '공부 중 · 꾸미가 뿌듯해해요', push: '' },
    { min: 1,  face: 'ok',    state: '5분 내외 · 아직은 괜춘해요', push: '' },
    { min: 8,  face: 'sad',   state: '10분 내외 · 꾸미가 약간 우울해요', push: '이제 슬슬 공부해볼까? 🌱' },
    { min: 20, face: 'cry',   state: '30분 내외 · 꾸미가 엉엉 울어요', push: '꾸미 지금 울고 있어요… 다시 와줄 거죠? 😢' },
    { min: 50, face: 'angry', state: '1시간 넘음 · 꾸미 폭발 직전!', push: '진짜 너무해!! 당장 폰 내려놔!! 💢' }
  ];
  let curFace = 'happy';
  function updateMood() {
    const m = +range.value;
    out.textContent = m >= 60 ? '1시간+' : m + '분';
    range.style.setProperty('--fill', (m / range.max * 100) + '%');
    const lv = [...levels].reverse().find(l => m >= l.min);
    if (lv.face !== curFace) { setFace(moodFace, lv.face); curFace = lv.face; }
    moodState.textContent = lv.state;
    device.classList.toggle('shake', lv.face === 'cry');
    device.classList.toggle('angry', lv.face === 'angry');
    if (lv.push) { pushText.textContent = lv.push; push.classList.add('show'); setFace($('.push-icon'), lv.face); }
    else push.classList.remove('show');
    const idx = levels.indexOf(lv);
    steps.forEach((s, i) => s.classList.toggle('on', i === idx));
  }
  range.addEventListener('input', updateMood);
  steps.forEach(s => s.addEventListener('click', () => { range.value = s.dataset.min; updateMood(); }));
  $('#backToStudy').addEventListener('click', () => {
    range.value = 0; updateMood();
    setFace(moodFace, 'cheer'); curFace = 'cheer';
    moodState.textContent = '다시 공부 시작! 꾸미가 기뻐해요';
    toast('꾸미: 돌아와 줘서 고마워요! 🌱');
  });
  updateMood();

  /* ---------- 기능 탭 + 캐러셀 ---------- */
  const track = $('#featTrack'), cards = $$('.feat-card', track), tabs = $$('#featTabs button');
  $('#featTotal').textContent = String(cards.length).padStart(2, '0');
  let featIdx = 0;
  function activateFeature(i, scroll = true) {
    featIdx = (i + cards.length) % cards.length;
    cards.forEach((c, k) => c.classList.toggle('active', k === featIdx));
    tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === cards[featIdx].dataset.tab));
    tabs.forEach(t => t.setAttribute('aria-selected', t.dataset.tab === cards[featIdx].dataset.tab));
    $('#featIdx').textContent = String(featIdx + 1).padStart(2, '0');
    if (scroll) track.scrollTo({ left: cards[featIdx].offsetLeft - track.offsetLeft, behavior: 'smooth' });
  }
  tabs.forEach(t => t.addEventListener('click', () => activateFeature(cards.findIndex(c => c.dataset.tab === t.dataset.tab))));
  cards.forEach((c, i) => c.addEventListener('click', () => activateFeature(i)));
  $('#featPrev').addEventListener('click', () => activateFeature(featIdx - 1));
  $('#featNext').addEventListener('click', () => activateFeature(featIdx + 1));
  $$('.quick-menu a[data-tab]').forEach(a => a.addEventListener('click', () => {
    setTimeout(() => activateFeature(cards.findIndex(c => c.dataset.tab === a.dataset.tab)), 500);
  }));
  activateFeature(0, false);

  /* ---------- 앱: 달력 (이번 달) ---------- */
  (function buildCalendar() {
    const now = new Date();
    const y = now.getFullYear(), mo = now.getMonth(), today = now.getDate();
    $('#calTitle').textContent = `${y}년 ${mo + 1}월`;
    const first = new Date(y, mo, 1).getDay(), days = new Date(y, mo + 1, 0).getDate();
    const grid = $('#calGrid');
    let html = '';
    for (let i = 0; i < first; i++) html += '<span class="empty"></span>';
    for (let d = 1; d <= days; d++) {
      let cls = '';
      if (d < today) { const v = (d * 37 + 11) % 10; cls = v < 1 ? '' : v < 3 ? 'l1' : v < 6 ? 'l2' : v < 9 ? 'l3' : 'l4'; }
      if (d === today) cls += ' today l3';
      html += `<span class="${cls}" title="${mo + 1}월 ${d}일">${d}</span>`;
    }
    grid.innerHTML = html;
  })();

  /* ---------- 앱: 주간 막대 (공부 vs 휴대폰) ---------- */
  (function buildBars() {
    const data = [['월', 3.2, 1.1], ['화', 4.0, .6], ['수', 2.1, 1.8], ['목', 4.6, .4], ['금', 2.8, 1.2], ['토', 5.2, .9], ['일', 3.6, .7]];
    const max = 5.5;
    $('#weekBars').innerHTML = data.map(([d, s, p]) => `
      <div class="bar-col" title="${d} · 공부 ${s}시간 / 휴대폰 ${p}시간">
        <div class="bar-pair"><i class="s" style="height:0" data-h="${s / max * 100}%"></i><i class="p" style="height:0" data-h="${p / max * 100}%"></i></div>
        <small>${d}</small>
      </div>`).join('');
    const barIO = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { $$('#weekBars i').forEach(i => i.style.height = i.dataset.h); barIO.disconnect(); }
    }), { threshold: .4 });
    barIO.observe($('#weekBars'));
  })();

  /* ---------- 제품 클로즈업 핫스팟 ---------- */
  const spots = $$('.hotspot'), spotItems = $$('#spotList li');
  function activateSpot(i) {
    spots.forEach(s => s.classList.toggle('active', +s.dataset.spot === i));
    spotItems.forEach(s => s.classList.toggle('active', +s.dataset.spot === i));
  }
  spots.forEach(s => s.addEventListener('click', () => activateSpot(+s.dataset.spot)));
  spotItems.forEach(s => s.addEventListener('click', () => activateSpot(+s.dataset.spot)));
  activateSpot(2);

  /* ---------- 구매 ---------- */
  const PRICE = 79000;
  const colorMap = {   // 색상 미리보기 (실제 색상별 사진이 생기면 src만 바꾸면 돼요)
    mint:     { name: '세이지 민트', filter: 'none',                                          bg: '#F2F6EE' },
    cream:    { name: '밀크 크림',   filter: 'hue-rotate(-75deg) saturate(.55) brightness(1.08)', bg: '#F8F3E8' },
    peach:    { name: '피치 블러썸', filter: 'hue-rotate(-125deg) saturate(1.05) brightness(1.05)', bg: '#FAEEEA' },
    sky:      { name: '스카이 블루', filter: 'hue-rotate(75deg) saturate(.9)',                   bg: '#EEF4F9' },
    lavender: { name: '라벤더',     filter: 'hue-rotate(140deg) saturate(.7) brightness(1.04)',  bg: '#F3F0F9' }
  };
  const buyImg = $('#buyImg'), buyPhoto = $('#buyPhoto'), qty = $('#qty'), bundle = $('#bundle');
  function applyColor(key) {
    const c = colorMap[key];
    $('#colorName').textContent = c.name;
    buyImg.style.filter = c.filter;
    buyPhoto.style.background = c.bg;
  }
  function calcTotal() {
    const q = Math.min(10, Math.max(1, parseInt(qty.value) || 1));
    qty.value = q;
    $('#total').textContent = won((PRICE + +bundle.value) * q);
  }
  $$('#swatches input').forEach(r => r.addEventListener('change', () => applyColor(r.value)));
  $('#qtyMinus').addEventListener('click', () => { qty.value = +qty.value - 1; calcTotal(); });
  $('#qtyPlus').addEventListener('click', () => { qty.value = +qty.value + 1; calcTotal(); });
  qty.addEventListener('change', calcTotal);
  bundle.addEventListener('change', calcTotal);
  $$('.thumb').forEach(t => t.addEventListener('click', () => {
    $$('.thumb').forEach(x => x.classList.remove('active')); t.classList.add('active');
    buyImg.style.opacity = 0;
    setTimeout(() => { buyImg.src = t.dataset.src; buyImg.style.opacity = 1; }, 200);
  }));
  $('#cartBtn').addEventListener('click', () => toast(`장바구니에 담았어요 · ${$('#colorName').textContent} ${qty.value}개`));
  $('#buyForm').addEventListener('submit', e => {
    e.preventDefault();
    toast(`${$('#colorName').textContent} 꾸미 ${qty.value}개 · ${$('#total').textContent} 결제 페이지로 이동해요`);
  });
  calcTotal();
});

/* ---------- 콜라보 광고 팝업 ---------- */
document.addEventListener('DOMContentLoaded', () => {
  const pop = document.getElementById('collabPop');
  if (!pop) return;
  // ek.png가 없으면 꾸미 일러스트로 대체
  const img = document.getElementById('cpImg');
  const fallback = () => { const d = document.createElement('div'); d.className = 'cp-fallback'; d.innerHTML = Kkumi.svg('love'); img.replaceWith(d); };
  if (img.complete && img.naturalWidth === 0) fallback(); else img.addEventListener('error', fallback);
  const KEY = 'kkumi-collab-pop-hide';
  const today = new Date().toISOString().slice(0, 10);
  let hiddenToday = false;
  try { hiddenToday = localStorage.getItem(KEY) === today; } catch (e) {}
  if (hiddenToday) return;

  // 페이지 열고 1.5초 뒤에 살짝 등장
  setTimeout(() => {
    pop.hidden = false;
    requestAnimationFrame(() => pop.classList.add('show'));
  }, 1500);

  const close = () => {
    pop.classList.remove('show');
    setTimeout(() => { pop.hidden = true; }, 450);
  };
  document.getElementById('cpClose').addEventListener('click', close);
  document.getElementById('cpToday').addEventListener('click', () => {
    try { localStorage.setItem(KEY, today); } catch (e) {}
    close();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) close(); });
});