let allBugData = [];
let currentBug = null;
let isAnswerRevealed = false;

// DOM Elements
const bugImage = document.getElementById('bug-image');
const questionText = document.getElementById('question-text');
const userInput = document.getElementById('user-input');
const submitButton = document.getElementById('submit-button');
const revealButton = document.getElementById('reveal-button');
const hintButton = document.getElementById('hint-button');
const feedbackArea = document.getElementById('feedback-area');
const orderFilter = document.getElementById('order-filter');
const gameMode = document.getElementById('game-mode');

// Task 3.1: Initialization
async function init() {
    try {
        const response = await fetch('data/bug_data.json');
        if (!response.ok) {
            throw new Error('Failed to load bug data');
        }
        allBugData = await response.json();
        console.log('Bug data loaded:', allBugData);

        populateOrders();
        loadNewCard();
    } catch (error) {
        console.error('Error initializing game:', error);
        feedbackArea.textContent = 'Error loading game data. Please refresh.';
        feedbackArea.className = 'incorrect';
    }
}

function populateOrders() {
    const orders = new Set(allBugData.map(bug => bug.order).filter(o => o && o !== 'Unknown'));
    orders.forEach(order => {
        const option = document.createElement('option');
        option.value = order;
        option.textContent = order;
        orderFilter.appendChild(option);
    });
}

// Task 3.2: loadNewCard() Function
function loadNewCard() {
    if (allBugData.length === 0) return;

    // Filter logic
    const selectedOrder = orderFilter.value;
    let filteredBugs = allBugData;
    if (selectedOrder !== 'all') {
        filteredBugs = allBugData.filter(bug => bug.order === selectedOrder);
    }

    if (filteredBugs.length === 0) {
        alert("No bugs found for this filter!");
        orderFilter.value = 'all';
        filteredBugs = allBugData;
    }

    // Pick random bug
    const randomIndex = Math.floor(Math.random() * filteredBugs.length);
    currentBug = filteredBugs[randomIndex];

    // Reset State
    isAnswerRevealed = false;
    userInput.value = '';
    userInput.disabled = false;
    feedbackArea.textContent = '';
    feedbackArea.className = '';
    submitButton.disabled = false;
    hintButton.disabled = false;

    // Reset Reveal Button to "Reveal Answer" state
    revealButton.textContent = 'Reveal Answer';
    // We handle the logic inside the click handler now, checking state

    // Update UI based on Mode
    const mode = gameMode.value;
    if (mode === 'family') {
        questionText.textContent = `Identify the Family of this ${currentBug.order || 'bug'}!`;
        userInput.placeholder = "Enter family name...";
    } else {
        questionText.textContent = "What is this bug?";
        userInput.placeholder = "Enter common name...";
    }

    // Update Image
    bugImage.src = currentBug.image_url || 'placeholder.png';
    bugImage.alt = "Mystery Bug";

    if (!currentBug.image_url) {
        console.warn(`Bug ID ${currentBug.id} (${currentBug.common_name}) has no image URL.`);
    }
}

// Task 3.3: checkAnswer() Function
function checkAnswer() {
    if (!currentBug || isAnswerRevealed) return;

    const guess = userInput.value.trim();
    if (!guess) return;

    const mode = gameMode.value;
    const normalizedGuess = guess.toLowerCase().replace(/\s+/g, ' ');
    let isCorrect = false;

    if (mode === 'family') {
        const normalizedFamily = (currentBug.family || "").toLowerCase().replace(/\s+/g, ' ');
        if (normalizedGuess === normalizedFamily) {
            isCorrect = true;
        }
    } else {
        const normalizedAnswer = currentBug.common_name.toLowerCase().replace(/\s+/g, ' ');
        const normalizedScientific = currentBug.scientific_name.toLowerCase().replace(/\s+/g, ' ');
        if (normalizedGuess === normalizedAnswer || normalizedGuess === normalizedScientific) {
            isCorrect = true;
        }
    }

    if (isCorrect) {
        feedbackArea.innerHTML = `✅ Correct! <br>Scientific Name: <em>${currentBug.scientific_name}</em><br>Family: ${currentBug.family}<br>${currentBug.key_facts}`;
        feedbackArea.className = 'correct';
        endRound();
    } else {
        feedbackArea.textContent = '❌ Incorrect. Try again or click Hint/Reveal.';
        feedbackArea.className = 'incorrect';
    }
}

// Task 3.4: revealAnswer() Function
function handleRevealClick() {
    if (isAnswerRevealed) {
        // If already revealed, this button acts as "Next Card"
        loadNewCard();
    } else {
        // Reveal logic
        revealInformation();
    }
}

function revealInformation() {
    if (!currentBug) return;

    // Display Correct Answer
    let sourceLinkHtml = "";
    if (currentBug.inat_url) {
        sourceLinkHtml = `<br><a href="${currentBug.inat_url}" target="_blank" class="source-link" style="color: #3498db; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px;">View on iNaturalist ↗</a>`;
    }

    feedbackArea.innerHTML = `<strong>Common Name:</strong> ${currentBug.common_name}<br>` +
        `<strong>Scientific:</strong> <em>${currentBug.scientific_name}</em><br>` +
        `<strong>Family:</strong> ${currentBug.family}<br>` +
        `<strong>Order:</strong> ${currentBug.order}<br>` +
        `<p>${currentBug.key_facts}</p>` +
        sourceLinkHtml;
    feedbackArea.className = 'revealed';

    endRound();
}

function giveHint() {
    if (!currentBug || isAnswerRevealed) return;

    const mode = gameMode.value;
    let hintText = "";

    if (mode === 'family') {
        // Hint: Show Order or first letter of family
        hintText = `Hint: It belongs to the Order ${currentBug.order}. Starts with '${currentBug.family.charAt(0)}'.`;
    } else {
        // Hint: Show Family or first letter of common name
        hintText = `Hint: Family is ${currentBug.family}. Starts with '${currentBug.common_name.charAt(0)}'.`;
    }

    feedbackArea.textContent = hintText;
    feedbackArea.className = 'revealed'; // Use neutral style
}

function endRound() {
    isAnswerRevealed = true;
    userInput.disabled = true;
    submitButton.disabled = true;
    hintButton.disabled = true;

    // Change Reveal button to Next Card
    revealButton.textContent = 'Next Card';
}

// Event Listeners
submitButton.addEventListener('click', checkAnswer);
revealButton.addEventListener('click', handleRevealClick);
hintButton.addEventListener('click', giveHint);

// Control Listeners
orderFilter.addEventListener('change', loadNewCard); // Reload when filter changes
gameMode.addEventListener('change', loadNewCard);    // Reload when mode changes

// Allow "Enter" key to submit
userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        if (isAnswerRevealed) {
            loadNewCard();
        } else {
            checkAnswer();
        }
    }
});

// Start the game on load
window.addEventListener('DOMContentLoaded', init);
