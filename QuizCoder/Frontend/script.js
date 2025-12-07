// Handle Play button on index.html
document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname.split("/").pop();

  if (currentPage === "index.html" || currentPage === "") {
    const playBtn = document.getElementById("btn-play");
    if (playBtn) {
      playBtn.addEventListener("click", () => {
        window.location.href = "register.html";
      });
    }
  }
});

const BASE_URL = "http://127.0.0.1:5000";
let currentUser = null;

// Navigation Helpers
function goTo(page) {
  window.location.href = page;
}

// Handle Registration
if (document.getElementById("reg-submit")) {
  document.getElementById("reg-submit").onclick = async () => {
    const username = document.getElementById("reg-user").value;
    const password = document.getElementById("reg-pass").value;

    const res = await fetch(`${BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (data.success) {
      alert("✅ Registered! Now login.");
      goTo("login.html");
    } else {
      alert("❌ " + data.message);
    }
  };
}

// Handle Login
if (document.getElementById("log-submit")) {
  document.getElementById("log-submit").onclick = async () => {
    const username = document.getElementById("log-user").value;
    const password = document.getElementById("log-pass").value;

    const res = await fetch(`${BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (data.success) {
      localStorage.setItem("username", username);
      goTo("dashboard.html");
    } else {
      alert("❌ " + data.message);
    }
  };
}

// Dashboard Setup
if (window.location.pathname.includes("dashboard")) {
  const user = localStorage.getItem("username");
  if (!user) goTo("login.html");

  document.getElementById("welcome").innerText = `🎮 Welcome, ${user}!`;

  document.getElementById("start-quiz").onclick = () => {
    goTo("quiz.html");
  };

  document.getElementById("notes-mania").onclick = () => {
    goTo("notes-quiz.html");
  };

  document.getElementById("leaderboard").onclick = async () => {
    goTo("leaderboard.html");
  };

  document.getElementById("logout").onclick = () => {
    localStorage.removeItem("username");
    goTo("index.html");
  };
}

// Timed Quiz
if (window.location.pathname.includes("quiz.html")) {
  const questionContainer = document.getElementById("quiz-container");
  const timerDisplay = document.getElementById("timer");
  let score = 0;
  let index = 0;
  let timer;
  let questions = [];

  async function startQuiz() {
    const res = await fetch(`${BASE_URL}/quiz`);
    const data = await res.json();
    questions = data.questions;
    showQuestion();
  }

  function showQuestion() {
    if (index >= questions.length) {
      submitQuiz();
      return;
    }

    const q = questions[index];
    questionContainer.innerHTML = `
      <h2>${q.question}</h2>
      ${q.options.map(opt => `
        <label>
          <input type="radio" name="option" value="${opt}"> ${opt}
        </label><br>
      `).join("")}
      <button onclick="submitAnswer()">Submit</button>
    `;

    startTimer();
  }

  function startTimer() {
    let timeLeft = 15;
    timerDisplay.innerText = `⏱️ ${timeLeft}s`;
    timer = setInterval(() => {
      timeLeft--;
      timerDisplay.innerText = `⏱️ ${timeLeft}s`;
      if (timeLeft <= 0) {
        clearInterval(timer);
        index++;
        showQuestion();
      }
    }, 1000);
  }

  window.submitAnswer = function () {
    clearInterval(timer);
    const selected = document.querySelector('input[name="option"]:checked');
    if (selected && selected.value === questions[index].answer) score++;
    index++;
    showQuestion();
  };

  function submitQuiz() {
    const user = localStorage.getItem("username");
    fetch(`${BASE_URL}/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: user, score })
    });
    alert(`Quiz finished! Your score: ${score}`);
    goTo("dashboard.html");
  }

  startQuiz();
}

// Notes Mania Quiz
if (window.location.pathname.includes("notes-quiz")) {
  const fileInput = document.getElementById("notes-file");
  const uploadBtn = document.getElementById("upload-notes");
  const quizZone = document.getElementById("notes-quiz-zone");
  let rounds = [];
  let roundScores = [];
  let roundIndex = 0;
  let qIndex = 0;
  let timer;
  let timeLeft;
  let score = 0;

  uploadBtn.onclick = async () => {
    const file = fileInput.files[0];
    if (!file) return alert("Please upload a notes file.");
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${BASE_URL}/upload_notes`, {
      method: "POST",
      body: form
    });
    const data = await res.json();
    rounds = data.rounds;
    roundIndex = 0;
    qIndex = 0;
    score = 0;
    roundScores = [];
    showNotesQuestion();
  };

  function showNotesQuestion() {
    if (roundIndex >= 3) {
      // submit scores
      const user = localStorage.getItem("username");
      fetch(`${BASE_URL}/submit_notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, round_scores: roundScores })
      });
      alert("✅ All rounds completed!");
      return goTo("dashboard.html");
    }

    if (qIndex >= rounds[roundIndex].length) {
      roundScores.push(score);
      roundIndex++;
      qIndex = 0;
      score = 0;
      return showNotesQuestion();
    }

    const q = rounds[roundIndex][qIndex];
    quizZone.innerHTML = `
      <h3>Round ${roundIndex + 1}, Question ${qIndex + 1}</h3>
      <h4>${q.question}</h4>
      ${q.options.map(opt => `
        <label><input type="radio" name="opt" value="${opt}">${opt}</label><br>
      `).join("")}
      <div id="note-timer">⏱️ 15s</div>
      <button onclick="submitNote()">Submit</button>
    `;
    timeLeft = 15;
    timer = setInterval(() => {
      timeLeft--;
      document.getElementById("note-timer").innerText = `⏱️ ${timeLeft}s`;
      if (timeLeft <= 0) {
        clearInterval(timer);
        qIndex++;
        showNotesQuestion();
      }
    }, 1000);
  }

  window.submitNote = function () {
    clearInterval(timer);
    const selected = document.querySelector('input[name="opt"]:checked');
    if (selected && selected.value === rounds[roundIndex][qIndex].answer) score++;
    qIndex++;
    showNotesQuestion();
  };
}

// Leaderboard
if (window.location.pathname.includes("leaderboard")) {
  fetch(`${BASE_URL}/leaderboard`)
    .then(res => res.json())
    .then(data => {
      const board = document.getElementById("board");
      board.innerHTML = data.users.map((user, i) => `
        <li>#${i + 1} — ${user.username}: ${user.score}</li>
      `).join("");
    });
}
