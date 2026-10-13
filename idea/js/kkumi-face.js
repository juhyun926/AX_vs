/* ==========================================================
   꾸미 캐릭터 SVG (사이트 곳곳의 꾸미 일러스트)
   사용법: <div data-kkumi="happy"></div>  → 자동으로 그려짐
   표정: happy, cheer, ok, sad, cry, angry, sleep, love, wow
   ========================================================== */
(function () {
  const C = {
    body: '#CFE5D0', bodyShade: '#B4D4B8', leaf: '#9CCB9F', leafDark: '#7FB487',
    screen: '#232825', face: '#FFFFFF', blush: '#F4A9A3', ring: '#F3E7A8'
  };

  const faces = {
    happy: `
      <path d="M68 96 q9 -11 18 0" class="kf-stroke"/>
      <path d="M106 96 q9 -11 18 0" class="kf-stroke"/>
      <path d="M90 108 q3 4 6 0 q3 4 6 0" class="kf-stroke thin"/>
      <ellipse cx="66" cy="110" rx="8" ry="4.5" class="kf-blush"/>
      <ellipse cx="126" cy="110" rx="8" ry="4.5" class="kf-blush"/>`,
    cheer: `
      <circle cx="77" cy="94" r="7" fill="${C.face}"/><circle cx="79" cy="92" r="2.4" fill="${C.screen}"/>
      <circle cx="115" cy="94" r="7" fill="${C.face}"/><circle cx="117" cy="92" r="2.4" fill="${C.screen}"/>
      <path d="M88 106 q8 10 16 0 z" fill="${C.face}"/>
      <ellipse cx="64" cy="108" rx="8" ry="4.5" class="kf-blush"/>
      <ellipse cx="128" cy="108" rx="8" ry="4.5" class="kf-blush"/>
      <path d="M135 74 l2 5 l5 2 l-5 2 l-2 5 l-2 -5 l-5 -2 l5 -2 z" fill="${C.ring}"/>`,
    ok: `
      <circle cx="77" cy="95" r="4.5" fill="${C.face}"/>
      <circle cx="115" cy="95" r="4.5" fill="${C.face}"/>
      <path d="M89 108 q7 5 14 0" class="kf-stroke thin"/>
      <ellipse cx="66" cy="109" rx="7" ry="4" class="kf-blush" opacity=".6"/>
      <ellipse cx="126" cy="109" rx="7" ry="4" class="kf-blush" opacity=".6"/>`,
    sad: `
      <path d="M68 90 l14 -5" class="kf-stroke thin"/><path d="M124 90 l-14 -5" class="kf-stroke thin"/>
      <circle cx="77" cy="98" r="4.5" fill="${C.face}"/>
      <circle cx="115" cy="98" r="4.5" fill="${C.face}"/>
      <path d="M89 112 q7 -6 14 0" class="kf-stroke thin"/>
      <ellipse cx="66" cy="110" rx="7" ry="4" class="kf-blush" opacity=".5"/>
      <ellipse cx="126" cy="110" rx="7" ry="4" class="kf-blush" opacity=".5"/>`,
    cry: `
      <path d="M68 93 q9 6 18 0" class="kf-stroke"/>
      <path d="M106 93 q9 6 18 0" class="kf-stroke"/>
      <rect x="73" y="97" width="7" height="22" rx="3.5" fill="#8EC9F2" class="kf-tear"/>
      <rect x="112" y="97" width="7" height="22" rx="3.5" fill="#8EC9F2" class="kf-tear"/>
      <path d="M88 113 q8 -9 16 0 z" fill="${C.face}"/>
      <ellipse cx="62" cy="108" rx="7" ry="4" class="kf-blush"/>
      <ellipse cx="130" cy="108" rx="7" ry="4" class="kf-blush"/>`,
    angry: `
      <path d="M66 84 l17 7" class="kf-stroke"/><path d="M126 84 l-17 7" class="kf-stroke"/>
      <circle cx="78" cy="98" r="4.5" fill="${C.face}"/>
      <circle cx="114" cy="98" r="4.5" fill="${C.face}"/>
      <path d="M86 114 l5 -5 l5 5 l5 -5 l5 5" class="kf-stroke thin"/>
      <path d="M130 70 l6 0 m-3 -3 l0 6 M127 64 l4 4 m0 -4 l-4 4" stroke="#FF7A6B" stroke-width="2.6" stroke-linecap="round"/>
      <ellipse cx="64" cy="110" rx="8" ry="4.5" fill="#FF8E80" opacity=".8"/>
      <ellipse cx="128" cy="110" rx="8" ry="4.5" fill="#FF8E80" opacity=".8"/>`,
    sleep: `
      <path d="M69 97 h16" class="kf-stroke"/>
      <path d="M107 97 h16" class="kf-stroke"/>
      <ellipse cx="96" cy="110" rx="4" ry="3" fill="none" stroke="${C.face}" stroke-width="2.4"/>
      <text x="126" y="82" class="kf-z">z</text><text x="134" y="74" class="kf-z small">z</text>
      <ellipse cx="66" cy="108" rx="7" ry="4" class="kf-blush" opacity=".6"/>
      <ellipse cx="126" cy="108" rx="7" ry="4" class="kf-blush" opacity=".6"/>`,
    love: `
      <path d="M77 101 l-8 -8 a4.6 4.6 0 0 1 8 -5 a4.6 4.6 0 0 1 8 5 z" fill="#FF8FA0"/>
      <path d="M115 101 l-8 -8 a4.6 4.6 0 0 1 8 -5 a4.6 4.6 0 0 1 8 5 z" fill="#FF8FA0"/>
      <path d="M88 108 q8 9 16 0" class="kf-stroke thin"/>
      <ellipse cx="64" cy="110" rx="8" ry="4.5" class="kf-blush"/>
      <ellipse cx="128" cy="110" rx="8" ry="4.5" class="kf-blush"/>`,
    wow: `
      <circle cx="77" cy="94" r="6" fill="${C.face}"/>
      <circle cx="115" cy="94" r="6" fill="${C.face}"/>
      <ellipse cx="96" cy="110" rx="5" ry="6" fill="${C.face}"/>
      <ellipse cx="64" cy="108" rx="7" ry="4" class="kf-blush"/>
      <ellipse cx="128" cy="108" rx="7" ry="4" class="kf-blush"/>`
  };

  function svg(expr, opts = {}) {
    const face = faces[expr] || faces.happy;
    const screenFill = expr === 'angry' ? '#3A2422' : C.screen;
    const time = opts.time ? `<text x="96" y="80" class="kf-time">${opts.time}</text>` : '';
    return `
<svg viewBox="0 0 200 182" class="kkumi-svg kf-${expr}" role="img" aria-label="꾸미 (${expr})">
  <style>
    .kf-stroke{fill:none;stroke:${C.face};stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
    .kf-stroke.thin{stroke-width:2.6}
    .kf-blush{fill:${C.blush}}
    .kf-time{fill:#E9F2EA;font:600 10px 'Pretendard',sans-serif;text-anchor:middle;letter-spacing:.5px;opacity:.85}
    .kf-z{fill:#CFE5D0;font:700 13px sans-serif}.kf-z.small{font-size:9px}
  </style>
  <ellipse cx="100" cy="172" rx="70" ry="7" fill="#000" opacity=".07"/>
  <g class="kf-leaves">
    <path d="M99 34 C 84 6, 56 12, 62 26 C 68 38, 88 38, 99 34 Z" fill="${C.leaf}"/>
    <path d="M101 34 C 116 4, 146 10, 140 24 C 134 37, 112 38, 101 34 Z" fill="${C.leaf}"/>
    <path d="M99 34 C 88 26, 76 24, 66 25" stroke="${C.leafDark}" stroke-width="1.6" fill="none" opacity=".6"/>
    <path d="M101 34 C 112 25, 124 22, 136 23" stroke="${C.leafDark}" stroke-width="1.6" fill="none" opacity=".6"/>
    <rect x="96" y="32" width="8" height="10" rx="3" fill="${C.leafDark}"/>
  </g>
  <ellipse cx="48" cy="160" rx="22" ry="14" fill="${C.bodyShade}"/>
  <ellipse cx="150" cy="160" rx="22" ry="14" fill="${C.bodyShade}"/>
  <path d="M100 38 C 158 38, 192 70, 190 112 C 188 146, 152 164, 100 164 C 48 164, 12 146, 10 112 C 8 70, 42 38, 100 38 Z" fill="${C.body}"/>
  <path d="M40 70 C 52 52, 72 46, 92 45" stroke="#fff" stroke-width="6" stroke-linecap="round" fill="none" opacity=".45"/>
  <ellipse cx="48" cy="161" rx="20" ry="12" fill="${C.body}"/>
  <ellipse cx="150" cy="161" rx="20" ry="12" fill="${C.body}"/>
  <rect x="38" y="64" width="116" height="74" rx="32" fill="${screenFill}"/>
  ${time}
  <g class="kf-face">${face}</g>
  <circle cx="181" cy="104" r="11" fill="${C.bodyShade}" stroke="${C.ring}" stroke-width="2.5"/>
</svg>`;
  }

  function render(root = document) {
    root.querySelectorAll('[data-kkumi]').forEach(el => {
      el.innerHTML = svg(el.dataset.kkumi, { time: el.dataset.time });
    });
  }

  window.Kkumi = { svg, render, faces: Object.keys(faces) };
  document.addEventListener('DOMContentLoaded', () => render());
})();