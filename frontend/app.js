/* AI Study Assistant — frontend JavaScript */

const API_BASE = "http://localhost:5000";

// ── DOM refs ──────────────────────────────────────────────────────────────────
const dropZone       = document.getElementById("dropZone");
const fileInput      = document.getElementById("fileInput");
const fileNameEl     = document.getElementById("fileName");
const numItemsInput  = document.getElementById("numItems");
const planDaysInput  = document.getElementById("planDays");
const spinner        = document.getElementById("spinner");
const errorMsg       = document.getElementById("errorMsg");

const textSection      = document.getElementById("textSection");
const extractedTextEl  = document.getElementById("extractedText");
const btnClearText     = document.getElementById("btnClearText");

const questionsSection = document.getElementById("questionsSection");
const questionsList    = document.getElementById("questionsList");

const flashcardsSection    = document.getElementById("flashcardsSection");
const flashcardsContainer  = document.getElementById("flashcardsContainer");

const studyPlanSection     = document.getElementById("studyPlanSection");
const studyPlanContainer   = document.getElementById("studyPlanContainer");

const mockTestSection   = document.getElementById("mockTestSection");
const mockTestContainer = document.getElementById("mockTestContainer");
const btnSubmitTest     = document.getElementById("btnSubmitTest");
const testScoreEl       = document.getElementById("testScore");

// ── File selection ─────────────────────────────────────────────────────────────
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});
fileInput.addEventListener("change", () => { if (fileInput.files[0]) setFile(fileInput.files[0]); });

let selectedFile = null;

function setFile(file) {
  selectedFile = file;
  fileNameEl.textContent = `📄 ${file.name}`;
}

// ── Helpers ────────────────────────────────────────────────────────────────────
function showSpinner()  { spinner.classList.remove("hidden"); errorMsg.classList.add("hidden"); }
function hideSpinner()  { spinner.classList.add("hidden"); }
function showError(msg) { errorMsg.textContent = msg; errorMsg.classList.remove("hidden"); }
function hideAllResults() {
  [textSection, questionsSection, flashcardsSection, studyPlanSection, mockTestSection]
    .forEach((s) => s.classList.add("hidden"));
}

/**
 * Build a FormData or JSON body depending on what is available.
 * If a PDF is selected, always use the file; otherwise fall back to the
 * textarea text (allowing users to paste text directly).
 */
function buildPayload(endpoint) {
  if (selectedFile) {
    const fd = new FormData();
    fd.append("file", selectedFile);
    return { body: fd };
  }
  const text = extractedTextEl.value.trim();
  if (!text) return null;
  return {
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  };
}

async function callApi(path, extraParams = {}) {
  const payload = buildPayload(path);
  if (!payload) {
    showError("Please upload a PDF or extract text first.");
    return null;
  }

  showSpinner();
  try {
    const url = new URL(`${API_BASE}${path}`);
    Object.entries(extraParams).forEach(([k, v]) => url.searchParams.set(k, v));

    const resp = await fetch(url.toString(), {
      method: "POST",
      ...payload,
    });
    const data = await resp.json();

    if (!resp.ok) {
      showError(data.error || `Server error ${resp.status}`);
      return null;
    }
    return data;
  } catch (err) {
    showError(`Network error: ${err.message}`);
    return null;
  } finally {
    hideSpinner();
  }
}

// ── Extract text ───────────────────────────────────────────────────────────────
document.getElementById("btnExtract").addEventListener("click", async () => {
  if (!selectedFile) { showError("Please select a PDF file first."); return; }

  const fd = new FormData();
  fd.append("file", selectedFile);

  showSpinner();
  try {
    const resp = await fetch(`${API_BASE}/extract`, { method: "POST", body: fd });
    const data = await resp.json();
    if (!resp.ok) { showError(data.error || "Extraction failed."); return; }
    extractedTextEl.value = data.text;
    hideAllResults();
    textSection.classList.remove("hidden");
  } catch (err) {
    showError(`Network error: ${err.message}`);
  } finally {
    hideSpinner();
  }
});

btnClearText.addEventListener("click", () => {
  extractedTextEl.value = "";
  textSection.classList.add("hidden");
  selectedFile = null;
  fileNameEl.textContent = "";
});

// ── Questions ──────────────────────────────────────────────────────────────────
document.getElementById("btnQuestions").addEventListener("click", async () => {
  const num = parseInt(numItemsInput.value, 10) || 10;
  const data = await callApi("/generate/questions", { num_questions: num });
  if (!data) return;

  questionsList.innerHTML = "";
  data.questions.forEach(({ question, answer }) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <div class="q-text">${escHtml(question)}</div>
      <div class="q-answer">💡 ${escHtml(answer)}</div>`;
    questionsList.appendChild(li);
  });

  hideAllResults();
  questionsSection.classList.remove("hidden");
});

// ── Flashcards ─────────────────────────────────────────────────────────────────
document.getElementById("btnFlashcards").addEventListener("click", async () => {
  const num = parseInt(numItemsInput.value, 10) || 10;
  const data = await callApi("/generate/flashcards", { num_cards: num });
  if (!data) return;

  flashcardsContainer.innerHTML = "";
  data.flashcards.forEach(({ front, back }) => {
    const card = document.createElement("div");
    card.className = "flashcard";
    card.innerHTML = `
      <div class="flashcard-inner">
        <div class="flashcard-front">${escHtml(front)}</div>
        <div class="flashcard-back">${escHtml(back)}</div>
      </div>
      <span class="flashcard-hint">click to flip</span>`;
    card.addEventListener("click", () => card.classList.toggle("flipped"));
    flashcardsContainer.appendChild(card);
  });

  hideAllResults();
  flashcardsSection.classList.remove("hidden");
});

// ── Study Plan ─────────────────────────────────────────────────────────────────
document.getElementById("btnStudyPlan").addEventListener("click", async () => {
  const days = parseInt(planDaysInput.value, 10) || 7;
  const data = await callApi("/generate/study-plan", { days });
  if (!data) return;

  studyPlanContainer.innerHTML = "";
  (data.plan || []).forEach(({ day, tasks }) => {
    const block = document.createElement("div");
    block.className = "day-block";
    const taskItems = (tasks || []).map((t) => `<li>${escHtml(t)}</li>`).join("");
    block.innerHTML = `<h3>Day ${day}</h3><ul>${taskItems}</ul>`;
    studyPlanContainer.appendChild(block);
  });

  hideAllResults();
  studyPlanSection.classList.remove("hidden");
});

// ── Mock Test ──────────────────────────────────────────────────────────────────
let mockTestData = [];

document.getElementById("btnMockTest").addEventListener("click", async () => {
  const num = parseInt(numItemsInput.value, 10) || 10;
  const data = await callApi("/generate/mock-test", { num_questions: num });
  if (!data) return;

  mockTestData = data.questions || [];
  mockTestContainer.innerHTML = "";
  testScoreEl.classList.add("hidden");

  mockTestData.forEach(({ question, options }, qi) => {
    const div = document.createElement("div");
    div.className = "mc-question";
    const optionsHtml = options.map((opt, oi) => `
      <label class="mc-option" id="opt-${qi}-${oi}">
        <input type="radio" name="q${qi}" value="${oi}" />
        ${escHtml(opt)}
      </label>`).join("");
    div.innerHTML = `
      <p class="mc-q">${qi + 1}. ${escHtml(question)}</p>
      ${optionsHtml}
      <div class="mc-explanation" id="exp-${qi}"></div>`;
    mockTestContainer.appendChild(div);
  });

  hideAllResults();
  mockTestSection.classList.remove("hidden");
});

btnSubmitTest.addEventListener("click", () => {
  let score = 0;
  mockTestData.forEach(({ correct_index, explanation }, qi) => {
    const selected = document.querySelector(`input[name="q${qi}"]:checked`);
    const expEl = document.getElementById(`exp-${qi}`);

    for (let oi = 0; oi < 4; oi++) {
      const optEl = document.getElementById(`opt-${qi}-${oi}`);
      if (!optEl) continue;
      optEl.classList.remove("correct", "incorrect");
      if (oi === correct_index) optEl.classList.add("correct");
      else if (selected && parseInt(selected.value, 10) === oi) optEl.classList.add("incorrect");
    }

    if (selected && parseInt(selected.value, 10) === correct_index) score++;

    if (expEl) {
      expEl.textContent = `Explanation: ${explanation}`;
      expEl.classList.add("visible");
    }

    // Disable all options in this question
    document.querySelectorAll(`input[name="q${qi}"]`).forEach((r) => (r.disabled = true));
  });

  const total = mockTestData.length;
  const pct = total ? Math.round((score / total) * 100) : 0;
  testScoreEl.textContent = `🎯 Score: ${score} / ${total} (${pct}%)`;
  testScoreEl.classList.remove("hidden");
  btnSubmitTest.disabled = true;
});

// ── Utility ────────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
