async function login() {

    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("http://localhost:8080/auth/login", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    if (!response.ok) {
        const message = await response.text();
        document.getElementById("login-message").textContent = message;
        return;
    }

    const data = await response.json();

    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("game-section").classList.remove("hidden");
    if (data.role === "ADMIN") {
    document.getElementById("admin-section").classList.remove("hidden");
    }

    startGame();
}


async function startGame() {
    const response = await fetch("http://localhost:8080/games/start", {
        method: "POST",
        credentials: "include"
    });

    if (!response.ok) {
        const message = await response.text();
        document.getElementById("game-message").textContent = message;
        return;
    }

    const data = await response.json();

    console.log("Game started:", data);

    const guessesContainer = document.getElementById("guesses");
    guessesContainer.innerHTML = "";

    // Restore previous guesses
    for (let i = 0; i < data.guesses.length; i++) {
        displayGuess(data.guesses[i], data.results[i]);
    }

    document.getElementById("game-message").textContent = "";
    document.getElementById("guess").value = "";
    document.getElementById("guess").disabled = false;
    document.querySelector(".guess-button").disabled = false;
}
async function submitGuess() {

    const guessInput = document.getElementById("guess");
    const guess = guessInput.value;

    const response = await fetch("http://localhost:8080/games/guess", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            guess: guess
        })
    });

    if (!response.ok) {
        const message = await response.text();
        document.getElementById("game-message").textContent = message;
        return;
    }

    const data = await response.json();

    displayGuess(guess.toUpperCase(), data.results);

    guessInput.value = "";

    if (data.status === "WON") {

        document.getElementById("game-message").textContent =
            "🎉 Congratulations! You guessed the word!";

        guessInput.disabled = true;
        document.querySelector("#guess-input button").disabled = true;

    } else if (data.status === "LOST") {

        document.getElementById("game-message").textContent =
            "Better luck next time!";

        guessInput.disabled = true;
        document.querySelector("#guess-input button").disabled = true;

    } else {

        document.getElementById("game-message").textContent =
            "Keep going!";
    }

    if (data.status === "WON") {
        alert("🎉 Congratulations! You guessed the word!");
        guessInput.disabled = true;
        document.querySelector("#guess-input button").disabled = true;

    } else if (data.status === "LOST") {
        alert("Better luck next time!");
        guessInput.disabled = true;
        document.querySelector("#guess-input button").disabled = true;

    }
}


function displayGuess(guess, results) {

    const guessesDiv = document.getElementById("guesses");

    const row = document.createElement("div");
    row.classList.add("guess-row");

    for (let i = 0; i < 5; i++) {

        const letter = document.createElement("div");

        letter.classList.add("letter");
        letter.classList.add(results[i].toLowerCase());

        letter.textContent = guess[i];

        row.appendChild(letter);
    }

    guessesDiv.appendChild(row);
}

async function register() {

    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    const response = await fetch("http://localhost:8080/auth/register", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password,
            confirmPassword: confirmPassword
        })
    });

    if (!response.ok) {
        const message = await response.text();
        document.getElementById("register-message").textContent = message;
        return;
    }

    const data = await response.json();

    token = data.token;

    document.getElementById("register-section").classList.add("hidden");
    document.getElementById("game-section").classList.remove("hidden");

    startGame();
}
function showRegister() {
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("register-section").classList.remove("hidden");
}
async function logout() {

    await fetch("http://localhost:8080/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    // Clear UI
    document.getElementById("game-section").classList.add("hidden");
    document.getElementById("login-section").classList.remove("hidden");
    document.getElementById("admin-section").classList.add("hidden");
    document.getElementById("guesses").innerHTML = "";
    document.getElementById("game-message").textContent = "";
    document.getElementById("guess").value = "";


    document.getElementById("login-message").textContent = "";
}
async function checkLogin() {

    const response = await fetch("http://localhost:8080/auth/me", {
        method: "GET",
        credentials: "include"
    });

    if (!response.ok) {
        // No valid cookie → stay on login page
        return;
    }

    const data = await response.json();

    // User is already logged in
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("register-section").classList.add("hidden");
    document.getElementById("game-section").classList.remove("hidden");
    if (data.role === "ADMIN") {
    document.getElementById("admin-section").classList.remove("hidden");
    }
    await loadCurrentGame();
}
    // Now restore the current game
async function loadCurrentGame() {

    const response = await fetch(
        "http://localhost:8080/games/current",
        {
            credentials: "include"
        }
    );

    console.log("CURRENT GAME STATUS:", response.status);

    if (!response.ok) {
        console.log("CURRENT GAME ERROR:", await response.text());
        return;
    }

    const data = await response.json();

    console.log("CURRENT GAME DATA:", data);

    const guessesContainer = document.getElementById("guesses");
    guessesContainer.innerHTML = "";

    for (let i = 0; i < data.guesses.length; i++) {

        console.log(
            "RENDERING:",
            data.guesses[i],
            data.results[i]
        );

        displayGuess(
            data.guesses[i],
            data.results[i]
        );
    }
}
async function showUserReport() {
    const playerId = prompt("Enter player ID:");

    if (!playerId) {
        return;
    }

    const date = new Date().toISOString().split("T")[0];

    const response = await fetch(
        `http://localhost:8080/admin/user-report/${playerId}?date=${date}`,
        {
            credentials: "include"
        }
    );

    const data = await response.json();

    document.getElementById("admin-report").innerHTML = `
        <p>Date: ${data.date}</p>
        <p>Words tried: ${data.noOfWordsTried}</p>
        <p>Correct guesses: ${data.noOfCorrectGuesses}</p>
    `;
}
async function showDailyReport() {
    const date = new Date().toISOString().split("T")[0];

    const response = await fetch(
        `http://localhost:8080/admin/daily-report?date=${date}`,
        {
            credentials: "include"
        }
    );

    const data = await response.json();

    document.getElementById("admin-report").innerHTML = `
        <p>Total Users: ${data.noOfUsers}</p>
        <p>Users Today: ${data.noOfUsersToday}
        <p>Correct guesses: ${data.noOfCorrectGuesses}</p>
    `;
}
console.log("SCRIPT LOADED");
checkLogin();