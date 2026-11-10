// =====================================================================
//  AI 면접 녹화 컴포넌트
//  - MediaPipe Face Landmarker(웹): 표정(블렌드셰이프), 시선, 고개 자세
//  - Web Audio: 성량, 음높이(억양), 침묵
//  - MediaRecorder: 답변 오디오 → Python(Whisper)
//  - Web Speech API: 실시간 자막 / 습관어 / 말하기 속도
// =====================================================================
import {
  FaceLandmarker,
  FilesetResolver,
  DrawingUtils,
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14";

const WASM_URL = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm";
const MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

const STRONG_FILLERS = ["음", "음음", "으음", "엄", "흠", "어", "어어", "아", "에", "으", "저기",
  "um", "umm", "uh", "uhm", "uhh", "er", "erm", "ah", "hmm", "a"];
const WEAK_FILLERS = ["그", "저", "뭐", "막", "이제", "약간", "좀", "그니까", "그러니까", "일단", "뭔가", "사실", "like"];
const FILLER_SET = new Set([...STRONG_FILLERS, ...WEAK_FILLERS]);

// ---------------- Streamlit 통신 (npm 없이 프로토콜 직접 구현) ----------------
const Streamlit = {
  send(type, data = {}) {
    window.parent.postMessage({ isStreamlitMessage: true, type, ...data }, "*");
  },
  ready() { this.send("streamlit:componentReady", { apiVersion: 1 }); },
  setValue(value) { this.send("streamlit:setComponentValue", { value, dataType: "json" }); },
  setHeight(h) { this.send("streamlit:setFrameHeight", { height: h }); },
};

let args = { question: "", live_tip: "", live_coaching: true, tip_interval: 15, max_seconds: 120, lang: "ko-KR" };
let lastTip = "";

window.addEventListener("message", (event) => {
  const d = event.data;
  if (!d || d.type !== "streamlit:render") return;
  args = { ...args, ...(d.args || {}) };
  $("question").textContent = args.question || "질문이 없습니다.";
  $("gptBadge").classList.toggle("off", !args.live_coaching);
  if (args.live_tip && args.live_tip !== lastTip) {
    lastTip = args.live_tip;
    const el = $("gptTip");
    el.textContent = args.live_tip;
    el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash");
  }
  fitHeight();
});

const $ = (id) => document.getElementById(id);
const fitHeight = () => Streamlit.setHeight(document.body.scrollHeight + 8);
new ResizeObserver(fitHeight).observe(document.body);

// ---------------- 상태 ----------------
const S = {
  phase: "idle", // idle | countdown | recording | processing | done
  stream: null, audioCtx: null, analyser: null, buf: null, recorder: null, chunks: [],
  speech: null, finalText: "", interim: "",
  startAt: 0, lastFace: 0, lastAudio: 0, lastUi: 0, lastPartial: 0, lastPartialText: "", seq: 0,
  noiseSamples: [], noiseFloor: -60, silenceStart: null, eyeClosed: false,
  recentEye: [], recentSmile: [], recentVol: [], expression: "무표정",
};
let M = newMetrics();

function newMetrics() {
  return {
    frames: 0, faceFrames: 0, eyeFrames: 0, smileFrames: 0, tenseFrames: 0, anxiousFrames: 0,
    smileSum: 0, blinks: 0, nose: [], yaw: [], pitch: [],
    expr: { 미소: 0, 무표정: 0, 긴장: 0, 불안: 0 },
    audioFrames: 0, voicedFrames: 0, volumes: [], pitches: [], longPauses: 0, firstVoice: null,
    timeline: [], bucket: { eye: [], smile: [], vol: [] }, bucketSec: 0,
  };
}

// ---------------- MediaPipe 얼굴 모델 ----------------
let faceLandmarker = null;
let drawer = null;
const canvas = $("overlay");
const ctx = canvas.getContext("2d");

async function loadFaceModel() {
  try {
    const fileset = await FilesetResolver.forVisionTasks(WASM_URL);
    const opts = (delegate) => ({
      baseOptions: { modelAssetPath: MODEL_URL, delegate },
      runningMode: "VIDEO",
      numFaces: 1,
      outputFaceBlendshapes: true,
      outputFacialTransformationMatrixes: true,
    });
    try { faceLandmarker = await FaceLandmarker.createFromOptions(fileset, opts("GPU")); }
    catch { faceLandmarker = await FaceLandmarker.createFromOptions(fileset, opts("CPU")); }
    drawer = new DrawingUtils(ctx);
    $("modelStatus").textContent = "✅ AI 얼굴 분석 준비 완료";
  } catch (e) {
    console.error(e);
    $("modelStatus").textContent = "⚠️ 얼굴 분석 모델을 불러오지 못했어요 (인터넷 연결 확인)";
  }
}
loadFaceModel();

// ---------------- 시작 / 종료 ----------------
$("startBtn").onclick = start;
$("stopBtn").onclick = () => stop();

async function start() {
  if (S.phase !== "idle" && S.phase !== "done") return;
  try {
    S.stream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: false },
    });
  } catch (e) {
    setStatus("❌ 카메라/마이크 권한이 필요해요: " + e.message);
    return;
  }
  resetRun();
  const video = $("video");
  video.srcObject = S.stream;
  await video.play();
  $("placeholder").classList.add("hidden");

  // 오디오 분석기
  S.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const src = S.audioCtx.createMediaStreamSource(S.stream);
  S.analyser = S.audioCtx.createAnalyser();
  S.analyser.fftSize = 2048;
  S.buf = new Float32Array(S.analyser.fftSize);
  src.connect(S.analyser);

  $("startBtn").disabled = true;
  S.phase = "countdown";
  requestAnimationFrame(loop);

  // 3초 카운트다운 동안 주변 소음 측정
  const cd = $("countdown");
  cd.classList.remove("hidden");
  for (let i = 3; i > 0; i--) { cd.textContent = i; await wait(1000); }
  cd.classList.add("hidden");
  S.noiseFloor = percentile(S.noiseSamples, 0.3) ?? -60;
  beginRecording();
}

function beginRecording() {
  // 오디오만 따로 녹음 (용량 절약)
  const audioStream = new MediaStream(S.stream.getAudioTracks());
  const mime = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg"]
    .find((m) => window.MediaRecorder && MediaRecorder.isTypeSupported(m)) || "";
  S.recorder = new MediaRecorder(audioStream, mime ? { mimeType: mime } : undefined);
  S.chunks = [];
  S.recorder.ondataavailable = (e) => e.data.size && S.chunks.push(e.data);
  S.recorder.start(1000);

  startSpeechRecognition();
  S.phase = "recording";
  S.startAt = performance.now();
  $("recBadge").classList.remove("hidden");
  $("stopBtn").disabled = false;
  setStatus("답변 중… 면접관(카메라)을 바라보며 말해보세요");
  $("gptTip").textContent = args.live_coaching ? "답변을 듣고 있어요…" : "실시간 GPT 코칭이 꺼져 있어요.";
}

async function stop(auto = false) {
  if (S.phase !== "recording") return;
  S.phase = "processing";
  $("stopBtn").disabled = true;
  $("recBadge").classList.add("hidden");
  setStatus(auto ? "⏱️ 제한 시간이 끝났어요. 분석 중…" : "분석 중… 잠시만 기다려 주세요");

  try { S.speech && S.speech.stop(); } catch {}
  const blob = await new Promise((resolve) => {
    S.recorder.onstop = () => resolve(new Blob(S.chunks, { type: S.recorder.mimeType || "audio/webm" }));
    S.recorder.stop();
  });
  const duration = (performance.now() - S.startAt) / 1000;
  const audio_b64 = await blobToBase64(blob);
  const summary = summarize(duration);

  S.stream.getTracks().forEach((t) => t.stop());
  try { S.audioCtx.close(); } catch {}
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  Streamlit.setValue({
    type: "final",
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    question: args.question,
    duration,
    transcript_live: (S.finalText + " " + S.interim).trim(),
    face: summary.face,
    voice: summary.voice,
    timeline: M.timeline,
    audio_b64,
    mime: blob.type,
  });
  S.phase = "done";
  $("startBtn").disabled = false;
  $("startBtn").textContent = "↻ 다시 답변하기";
  $("placeholder").classList.remove("hidden");
  $("placeholder").querySelector("p").textContent = "답변이 제출됐어요. 아래에서 결과를 확인하세요 👇";
  setStatus("✅ 제출 완료 — 아래에서 AI 분석 결과를 확인하세요");
}

function resetRun() {
  M = newMetrics();
  Object.assign(S, {
    finalText: "", interim: "", noiseSamples: [], silenceStart: null, eyeClosed: false,
    recentEye: [], recentSmile: [], recentVol: [], lastPartial: performance.now(), lastPartialText: "",
  });
  $("transcript").innerHTML = '<span class="muted">말씀하시면 여기에 표시돼요</span>';
  $("hints").innerHTML = "";
  $("fillerChips").innerHTML = "";
}

// ---------------- 메인 루프 ----------------
function loop(now) {
  if (S.phase !== "countdown" && S.phase !== "recording") return;
  const video = $("video");
  if (faceLandmarker && video.readyState >= 2 && now - S.lastFace > 66) {
    S.lastFace = now;
    try { processFace(faceLandmarker.detectForVideo(video, now)); } catch (e) { console.warn(e); }
  }
  if (now - S.lastAudio > 50) { S.lastAudio = now; processAudio(now); }
  if (now - S.lastUi > 400) { S.lastUi = now; updateLive(now); }
  requestAnimationFrame(loop);
}

// ---------------- 얼굴 / 표정 ----------------
function processFace(res) {
  const video = $("video");
  if (canvas.width !== video.videoWidth) {
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  }
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const rec = S.phase === "recording";
  if (rec) M.frames++;

  const lm = res.faceLandmarks && res.faceLandmarks[0];
  if (!lm) {
    pushRecent(S.recentEye, 0, 8); S.expression = "얼굴 인식 안 됨";
    return;
  }

  // 얼굴 메시 그리기
  drawer.drawConnectors(lm, FaceLandmarker.FACE_LANDMARKS_TESSELATION, { color: "rgba(255,255,255,0.10)", lineWidth: 0.5 });
  drawer.drawConnectors(lm, FaceLandmarker.FACE_LANDMARKS_LEFT_IRIS, { color: "#22d3ee", lineWidth: 1.5 });
  drawer.drawConnectors(lm, FaceLandmarker.FACE_LANDMARKS_RIGHT_IRIS, { color: "#22d3ee", lineWidth: 1.5 });
  drawer.drawConnectors(lm, FaceLandmarker.FACE_LANDMARKS_LIPS, { color: "rgba(129,140,248,0.8)", lineWidth: 1 });

  const bs = {};
  (res.faceBlendshapes?.[0]?.categories || []).forEach((c) => (bs[c.categoryName] = c.score));
  const avg = (a, b) => ((bs[a] || 0) + (bs[b] || 0)) / 2;

  const smile = avg("mouthSmileLeft", "mouthSmileRight");
  const browDown = avg("browDownLeft", "browDownRight");
  const browUp = bs.browInnerUp || 0;
  const frown = avg("mouthFrownLeft", "mouthFrownRight");
  const press = avg("mouthPressLeft", "mouthPressRight");
  const blink = avg("eyeBlinkLeft", "eyeBlinkRight");
  const gazeH = Math.max(avg("eyeLookOutLeft", "eyeLookInRight"), avg("eyeLookInLeft", "eyeLookOutRight"));
  const gazeV = Math.max(avg("eyeLookUpLeft", "eyeLookUpRight"), avg("eyeLookDownLeft", "eyeLookDownRight"));

  // 고개 자세 (4x4 변환 행렬, column-major)
  let yaw = 0, pitch = 0;
  const m = res.facialTransformationMatrixes?.[0]?.data;
  if (m) {
    yaw = Math.asin(Math.max(-1, Math.min(1, -m[2]))) * 180 / Math.PI;
    pitch = Math.atan2(m[6], m[10]) * 180 / Math.PI;
  }
  const eyeContact = Math.abs(yaw) < 18 && Math.abs(pitch) < 20 && gazeH < 0.5 && gazeV < 0.55 && blink < 0.6;

  // 표정 분류
  let expr = "무표정";
  if (smile > 0.35) expr = "미소";
  else if (browDown > 0.35 || frown > 0.3 || press > 0.45) expr = "긴장";
  else if (browUp > 0.4) expr = "불안";
  S.expression = expr;

  // 눈 깜빡임
  if (blink > 0.5 && !S.eyeClosed) { S.eyeClosed = true; if (rec) M.blinks++; }
  else if (blink < 0.3) S.eyeClosed = false;

  pushRecent(S.recentEye, eyeContact ? 1 : 0, 8);
  pushRecent(S.recentSmile, smile, 8);

  if (!rec) return;
  M.faceFrames++;
  if (eyeContact) M.eyeFrames++;
  if (smile > 0.35) M.smileFrames++;
  if (expr === "긴장") M.tenseFrames++;
  if (expr === "불안") M.anxiousFrames++;
  M.smileSum += smile;
  M.expr[expr]++;
  M.nose.push([lm[1].x, lm[1].y]);
  M.yaw.push(yaw); M.pitch.push(pitch);
  M.bucket.eye.push(eyeContact ? 1 : 0);
  M.bucket.smile.push(smile);
}

// ---------------- 목소리 ----------------
function processAudio(now) {
  if (!S.analyser) return;
  S.analyser.getFloatTimeDomainData(S.buf);
  let sum = 0;
  for (let i = 0; i < S.buf.length; i++) sum += S.buf[i] * S.buf[i];
  const rms = Math.sqrt(sum / S.buf.length);
  const db = 20 * Math.log10(rms + 1e-8);

  $("meterFill").style.width = `${Math.max(0, Math.min(100, (db + 60) * 2))}%`;

  if (S.phase === "countdown") { S.noiseSamples.push(db); return; }
  if (S.phase !== "recording") return;

  const thr = Math.max(S.noiseFloor + 9, -55);
  const voiced = db > thr;
  const elapsed = (now - S.startAt) / 1000;
  M.audioFrames++;
  pushRecent(S.recentVol, voiced ? db - S.noiseFloor : null, 40);

  if (voiced) {
    M.voicedFrames++;
    M.volumes.push(db);
    M.bucket.vol.push(db - S.noiseFloor);
    const f0 = detectPitch(S.buf, S.audioCtx.sampleRate);
    if (f0 > 0) M.pitches.push(f0);
    if (M.firstVoice === null) M.firstVoice = elapsed;
    if (S.silenceStart !== null && now - S.silenceStart > 1200) M.longPauses++;
    S.silenceStart = null;
  } else if (M.firstVoice !== null && S.silenceStart === null) {
    S.silenceStart = now;
  }

  // 1초 단위 타임라인
  const sec = Math.floor(elapsed);
  if (sec > M.bucketSec) {
    const b = M.bucket;
    M.timeline.push({
      t: M.bucketSec,
      eye: b.eye.length ? mean(b.eye) : null,
      smile: b.smile.length ? mean(b.smile) : null,
      vol: b.vol.length ? mean(b.vol) : 0,
    });
    M.bucket = { eye: [], smile: [], vol: [] };
    M.bucketSec = sec;
  }
}

// 정규화 자기상관 기반 음높이(F0) 추정
function detectPitch(buf, sr) {
  const n = buf.length;
  const minLag = Math.floor(sr / 400), maxLag = Math.min(Math.floor(sr / 70), n - 1);
  let best = -1, bestCorr = 0;
  for (let lag = minLag; lag <= maxLag; lag += 1) {
    let c = 0, e1 = 0, e2 = 0;
    for (let i = 0; i < n - lag; i += 2) {
      const a = buf[i], b = buf[i + lag];
      c += a * b; e1 += a * a; e2 += b * b;
    }
    const r = c / Math.sqrt(e1 * e2 + 1e-12);
    if (r > bestCorr) { bestCorr = r; best = lag; }
  }
  return bestCorr > 0.8 ? sr / best : -1;
}

// ---------------- 실시간 자막 (Web Speech API) ----------------
function startSpeechRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    $("transcript").innerHTML = '<span class="muted">이 브라우저는 실시간 자막을 지원하지 않아요. 답변은 녹음되어 AI가 분석합니다.</span>';
    return;
  }
  const sr = new SR();
  sr.lang = args.lang || "ko-KR";
  sr.continuous = true;
  sr.interimResults = true;
  sr.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) S.finalText += t + " ";
      else interim += t;
    }
    S.interim = interim;
    renderTranscript();
  };
  sr.onend = () => { if (S.phase === "recording") { try { sr.start(); } catch {} } };
  sr.onerror = (e) => { if (e.error === "not-allowed") setStatus("자막 권한이 막혀 있어요 (녹음 분석은 계속됩니다)"); };
  try { sr.start(); } catch {}
  S.speech = sr;
}

function renderTranscript() {
  const hl = (txt) => escapeHtml(txt).replace(/[가-힣]+|[A-Za-z]+/g, (w) => (FILLER_SET.has(w.toLowerCase()) ? `<mark>${w}</mark>` : w));
  $("transcript").innerHTML = `${hl(S.finalText)}<span class="interim">${hl(S.interim)}</span>`;
  const box = $("transcript").parentElement;
  box.scrollTop = box.scrollHeight;
}

// ---------------- 실시간 UI / 코칭 ----------------
function updateLive(now) {
  if (S.phase !== "recording") return;
  const elapsed = (now - S.startAt) / 1000;
  $("timer").textContent = fmtTime(elapsed) + (args.max_seconds ? ` / ${fmtTime(args.max_seconds)}` : "");
  if (args.max_seconds && elapsed >= args.max_seconds) { stop(true); return; }

  const eye = S.recentEye.length ? mean(S.recentEye) : 0;
  const smile = S.recentSmile.length ? mean(S.recentSmile) : 0;
  const volVals = S.recentVol.filter((v) => v !== null);
  const vol = volVals.length ? mean(volVals) : 0;
  const pitch = semitoneStd(M.pitches.slice(-200));

  setBar("sEye", "bEye", eye * 100, `${Math.round(eye * 100)}%`);
  setBar("sSmile", "bSmile", Math.min(100, smile * 200), smile > 0.35 ? "좋아요" : smile > 0.15 ? "보통" : "낮음");
  setBar("sVol", "bVol", Math.min(100, (vol / 25) * 100), vol ? `${vol.toFixed(0)} dB` : "-");
  $("sPitch").textContent = pitch === null ? "-" : pitch < 1.6 ? "단조로움" : pitch > 4.5 ? "흔들림" : "자연스러움";

  const exprIcon = { 미소: "😊", 무표정: "😐", 긴장: "😣", 불안: "😟" }[S.expression] || "🫥";
  $("exprBadge").textContent = `${exprIcon} ${S.expression}`;

  // 말하기 속도 & 습관어
  const text = (S.finalText + " " + S.interim).trim();
  const speakSec = M.firstVoice === null ? 0 : elapsed - M.firstVoice;
  const syll = (text.match(/[가-힣]/g) || []).length;
  const words = (text.match(/[A-Za-z']+/g) || []).length;
  let speedLabel = "-";
  let spm = 0;
  if (speakSec > 5 && (syll || words)) {
    if (syll >= words) { spm = Math.round(syll / (speakSec / 60)); speedLabel = `${spm} 음절/분`; }
    else { spm = Math.round(words / (speakSec / 60)); speedLabel = `${spm} WPM`; }
  }
  $("sSpeed").textContent = speedLabel;

  const counts = {};
  (text.toLowerCase().match(/[가-힣]+|[a-z]+/g) || []).forEach((w) => {
    if (FILLER_SET.has(w)) counts[w] = (counts[w] || 0) + 1;
  });
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  $("sFiller").textContent = `${total}회`;
  $("fillerChips").innerHTML = Object.entries(counts).sort((a, b) => b[1] - a[1])
    .map(([w, c]) => `<span class="chip">${escapeHtml(w)} ×${c}</span>`).join("");

  // 규칙 기반 즉시 코칭
  const hints = [];
  if (S.recentEye.length >= 6 && eye < 0.5) hints.push("👀 카메라(면접관)를 바라보세요");
  if (elapsed > 8 && smile < 0.1) hints.push("🙂 표정을 조금 더 밝게");
  if (elapsed > 3 && volVals.length > 10 && vol < 12) hints.push("🔊 목소리를 조금 더 크게");
  if (spm && syll >= words && spm > 380) hints.push("🐢 조금 천천히 말해보세요");
  if (spm && syll >= words && spm < 230 && speakSec > 15) hints.push("⚡ 조금 더 힘 있게, 속도를 높여보세요");
  if (total >= 3 && total / Math.max(speakSec / 60, 0.3) > 4) hints.push("🗣️ '음/어' 대신 잠깐 쉬어가세요");
  if (M.firstVoice === null && elapsed > 4) hints.push("🎤 첫 문장을 시작해 보세요 (결론부터!)");
  if (pitch !== null && pitch < 1.4 && speakSec > 15) hints.push("🎵 핵심 단어에 힘을 주어 억양을 살리세요");
  $("hints").innerHTML = hints.slice(0, 3).map((h) => `<li>${h}</li>`).join("") || "<li>좋아요! 지금처럼 계속하세요 👍</li>";

  // 일정 주기로 중간 답변을 Python 으로 보내 GPT 코칭 받기
  const interval = (args.tip_interval || 15) * 1000;
  if (args.live_coaching && now - S.lastPartial > interval && text.length > 25 && text !== S.lastPartialText) {
    S.lastPartial = now;
    S.lastPartialText = text;
    Streamlit.setValue({
      type: "partial", seq: ++S.seq, transcript: text, elapsed: Math.round(elapsed),
      stats: { 시선맞춤: `${Math.round(eye * 100)}%`, 표정: S.expression, 속도: speedLabel, 습관어: counts },
    });
  }
}

// ---------------- 최종 요약 ----------------
function summarize(duration) {
  const minutes = Math.max(duration / 60, 0.1);
  const nx = M.nose.map((p) => p[0]), ny = M.nose.map((p) => p[1]);
  const ff = Math.max(M.faceFrames, 1);
  const face = {
    frames: M.frames,
    face_frames: M.faceFrames,
    presence: M.frames ? M.faceFrames / M.frames : 0,
    eye_contact: M.eyeFrames / ff,
    smile_avg: M.smileSum / ff,
    smile_ratio: M.smileFrames / ff,
    tension_ratio: M.tenseFrames / ff,
    anxious_ratio: M.anxiousFrames / ff,
    expression_dist: Object.fromEntries(Object.entries(M.expr).map(([k, v]) => [k, v / ff])),
    blink_per_min: M.blinks / minutes,
    head_movement: (std(nx) + std(ny)) * 100,
    yaw_std: std(M.yaw),
    pitch_std: std(M.pitch),
  };
  const voice = {
    frames: M.audioFrames,
    duration,
    noise_floor: S.noiseFloor,
    voiced_ratio: M.audioFrames ? M.voicedFrames / M.audioFrames : 0,
    mean_db: M.volumes.length ? mean(M.volumes) : null,
    db_std: std(M.volumes),
    pitch_mean: M.pitches.length ? median(M.pitches) : null,
    pitch_semitone_std: semitoneStd(M.pitches),
    long_pauses: M.longPauses,
    first_voice_sec: M.firstVoice,
  };
  return { face, voice };
}

// ---------------- 유틸 ----------------
function semitoneStd(pitches) {
  if (pitches.length < 15) return null;
  const med = median(pitches);
  // 옥타브 오류(배음) 제거
  const st = pitches.map((f) => 12 * Math.log2(f / med)).filter((s) => Math.abs(s) < 10);
  return st.length < 10 ? null : std(st);
}
function mean(a) { return a.reduce((x, y) => x + y, 0) / a.length; }
function std(a) {
  if (a.length < 2) return 0;
  const m = mean(a);
  return Math.sqrt(a.reduce((s, x) => s + (x - m) ** 2, 0) / a.length);
}
function median(a) { return percentile(a, 0.5); }
function percentile(a, p) {
  if (!a.length) return null;
  const s = [...a].sort((x, y) => x - y);
  return s[Math.min(s.length - 1, Math.floor(p * s.length))];
}
function pushRecent(arr, v, n) { arr.push(v); if (arr.length > n) arr.shift(); }
function setBar(sid, bid, pct, label) { $(sid).textContent = label; $(bid).style.width = `${Math.max(0, Math.min(100, pct))}%`; }
function fmtTime(s) { s = Math.floor(s); return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`; }
function wait(ms) { return new Promise((r) => setTimeout(r, ms)); }
function setStatus(t) { $("status").textContent = t; }
function escapeHtml(s) { return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
function blobToBase64(blob) {
  return new Promise((resolve) => {
    const r = new FileReader();
    r.onloadend = () => resolve(String(r.result).split(",")[1] || "");
    r.readAsDataURL(blob);
  });
}

Streamlit.ready();
fitHeight();
