/* =========================================================
   KKUMi × 콜라보 페이지 스크립트
   ========================================================= */
document.addEventListener('DOMContentLoaded', () => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const won = n => n.toLocaleString('ko-KR') + '원';

  /* ---------- 이미지 파일이 아직 없으면 안내 상자로 대체 ---------- */
  $$('img[data-fallback]').forEach(img => {
    const showMissing = () => {
      if (img.dataset.missing) return;
      img.dataset.missing = '1';
      img.style.display = 'none';
      const box = document.createElement('div');
      box.className = 'img-missing';
      box.textContent = `images/${img.dataset.fallback} 파일을 넣어주세요`;
      img.after(box);
    };
    img.addEventListener('error', showMissing);
    if (img.complete && img.naturalWidth === 0) showMissing();
  });

  /* ---------- 토스트 ---------- */
  const toastEl = $('#cToast'); let t;
  const toast = m => { toastEl.textContent = m; toastEl.classList.add('show'); clearTimeout(t); t = setTimeout(() => toastEl.classList.remove('show'), 2400); };

  /* ---------- 사전 예약 카운트다운 (마감일은 여기서 바꾸세요) ---------- */
  const DEADLINE = new Date('2026-11-30T23:59:59+09:00');
  const cd = $('#countdown');
  function tick() {
    let s = Math.max(0, Math.floor((DEADLINE - Date.now()) / 1000));
    const d = Math.floor(s / 86400); s %= 86400;
    const pad = n => String(n).padStart(2, '0');
    cd.textContent = `${d}일 ${pad(Math.floor(s / 3600))}:${pad(Math.floor(s % 3600 / 60))}:${pad(s % 60)}`;
  }
  tick(); setInterval(tick, 1000);

  /* ---------- 주문 ---------- */
  const PRICE = 89000, GIFT = 3000;
  const editions = [
    { name: '치이카와 에디션', img: 'images/cldl.png', file: 'cldl.png', tone: '#FFE3E8' },
    { name: '하치와레 에디션', img: 'images/gkcl.png', file: 'gkcl.png', tone: '#DDEEFF' },
    { name: '우사기 에디션',   img: 'images/dntk.png', file: 'dntk.png', tone: '#FFF3C9' }
  ];
  const orderImg = $('#orderImg'), orderPhoto = $('#orderPhoto'), orderTag = $('#orderTag'),
        qty = $('#cQty'), gift = $('#cGift');

  function selected() { return $('#edPick input:checked').value; }

  function showEdition(v) {
    $$('.ed-card').forEach(c => c.classList.toggle('picked', c.dataset.ed === v));
    if (v === 'set') {
      orderTag.textContent = '3종 세트 · 세 친구 모두 데려가기';
      orderPhoto.style.background = '#F3EEFF';
      return;
    }
    const e = editions[+v];
    orderTag.textContent = `EDITION 0${+v + 1} · ${e.name}`;
    orderPhoto.style.background = e.tone;
    orderImg.style.opacity = 0;
    setTimeout(() => {
      const missing = orderPhoto.querySelector('.img-missing');
      if (missing) missing.remove();
      delete orderImg.dataset.missing;
      orderImg.style.display = '';
      orderImg.dataset.fallback = e.file;
      orderImg.src = e.img;
      orderImg.style.opacity = 1;
    }, 180);
  }

  function calc() {
    const q = Math.min(5, Math.max(1, parseInt(qty.value) || 1)); qty.value = q;
    const v = selected();
    const unit = v === 'set' ? Math.round(PRICE * 3 * 0.9) : PRICE;
    $('#cUnit').textContent = won(unit);
    $('#cTotal').textContent = won(unit * q + (gift.checked ? GIFT : 0));
  }

  $$('#edPick input').forEach(r => r.addEventListener('change', () => { showEdition(r.value); calc(); }));
  $$('[data-pick]').forEach(b => b.addEventListener('click', () => {
    const r = $(`#edPick input[value="${b.dataset.pick}"]`);
    r.checked = true; showEdition(r.value); calc();
    $('#order').scrollIntoView({ behavior: 'smooth' });
    toast(`${editions[+b.dataset.pick].name}을(를) 골랐어요!`);
  }));
  $('#cMinus').addEventListener('click', () => { qty.value = +qty.value - 1; calc(); });
  $('#cPlus').addEventListener('click', () => { qty.value = +qty.value + 1; calc(); });
  qty.addEventListener('change', calc);
  gift.addEventListener('change', calc);

  $('#orderForm').addEventListener('submit', e => {
    e.preventDefault();
    const v = selected();
    const name = v === 'set' ? '3종 세트' : editions[+v].name;
    toast(`${name} ${qty.value}개 예약 완료! (${$('#cTotal').textContent})`);
  });

  showEdition('0'); calc();
});