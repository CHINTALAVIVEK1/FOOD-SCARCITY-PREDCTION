// Get all collapsible buttons
const collapsibles = document.querySelectorAll(".collapsible");

// Add click event to each button
collapsibles.forEach(button => {
    button.addEventListener("click", function () {
        let content = this.nextElementSibling; // Get the next sibling (content list)

        if (content.style.display === "block") {
            content.style.display = "none"; // Hide if already visible
        } else {
            content.style.display = "block"; // Show if hidden
        }
    });
});
// Toggle Chatbot Window
function toggleChatbot() {
    var chatContainer = document.getElementById("chatContainer");
    chatContainer.style.display = chatContainer.style.display === "flex" ? "none" : "flex";
}

// Handle Enter Key Press
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

// Send Message to Chatbot
function sendMessage() {
    var userInput = document.getElementById("userInput").value.trim();
    var chatBody = document.getElementById("chatBody");

    if (userInput === "") return;

    // Display User Message
    var userMessage = document.createElement("p");
    userMessage.className = "user-message";
    userMessage.textContent = userInput;
    chatBody.appendChild(userMessage);

    // Get Bot Response
    var botMessage = document.createElement("p");
    botMessage.className = "bot-message";
    botMessage.textContent = getBotResponse(userInput.toLowerCase());
    chatBody.appendChild(botMessage);

    // Scroll to Bottom
    chatBody.scrollTop = chatBody.scrollHeight;

    // Clear Input Field
    document.getElementById("userInput").value = "";
}

// Simple Bot Response Logic
function getBotResponse(input) {
    // Crop Recommendations Based on Season
    const cropRecommendations = {
        summer: "Mango, Tomato, Watermelon, Maize",
        winter: "Carrots, Spinach, Mustard, Peas",
        monsoon: "Rice, Millets, Turmeric, Soybean"
    };

    // Recipe Suggestions Based on Crop
    const recipeSuggestions = {
        mango: "Try making Mango Smoothie or Mango Pickle!",
        tomato: "Try making Tomato Soup or Pasta Sauce!",
        carrot: "Try making Carrot Halwa or Carrot Salad!",
        rice: "Try making Fried Rice or Lemon Rice!"
    };

    // Responses
    if (input.includes("which crop") || input.includes("plant")) {
        if (input.includes("summer")) return `For summer, you can plant: ${cropRecommendations.summer}`;
        if (input.includes("winter")) return `For winter, you can plant: ${cropRecommendations.winter}`;
        if (input.includes("monsoon")) return `For monsoon, you can plant: ${cropRecommendations.monsoon}`;
        return "Please specify the season (summer, winter, or monsoon).";
    }

    if (input.includes("recipe") || input.includes("cook")) {
        let words = input.split(" ");
        for (let word of words) {
            if (recipeSuggestions[word]) return recipeSuggestions[word];
        }
        return "Please specify a crop to get a recipe suggestion!";
    }

    if (input.includes("hello") || input.includes("hi")) {
        return "Hello! How can I assist you today?";
    }

    if (input.includes("thank")) {
        return "You're welcome! 😊";
    }

    return "I'm not sure about that. Try asking about crops, seasons, or recipes!";
}
