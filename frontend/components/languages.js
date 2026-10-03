// This script handles language selection and translation for the website.
async function getLanguage() {

    // Retrieves the cookie string and splits it into individual cookies
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        // Trims whitespace and splits the cookie into name and value
        const [name, value] = cookie.trim().split("=");
        // Checks if the cookie name is "language" and returns its value if found
        if (name === "language") {
            return value;
        }

    }

    // If the cookie is not found, fetches the language from the server
    try {
        // Connects to the endpoint for retrieving language
        const response = await fetch("/api/languages");
        if (!response.ok) {
            return "en"; // Default to English if the response is not OK
        }
        
        const data = await response.json();
        
        return data.language
    } catch (error) {
        // Logs any errors that occur during the fetch operation
        console.error("Error fetching language:", error);
        return "en"; // Default to English in case of an error
    }
}

// This function updates the language preference on the server and cookie
async function setLanguage(language) {
    
    try {
        // Connects to the endpoint for updating language
        const response = await fetch("/api/languages", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                language: language
            })
        });

        // Checks if the response is not OK and logs an error if so
        if (!response.ok) {
            console.error("Could not update language");
            return;
        }

        return true; // Returns true if the language was successfully updated

    } catch (error) {
        // Logs any errors that occur during the fetch operation
        console.error("Error updating language:", error);

    }
}

// This function sets up the language
async function initLanguage() {

    // Get the current page name
    let page = window.location.pathname.split("/").pop();

    if (!page || page === "") {
        page = "index.html";
    }

    const pageName = page.replace(".html", "");

    // Translation files that should be loaded
    const translationFiles = [
        "/translations/header.csv",
        `/translations/${pageName}.csv`
    ];

    // Load all CSV files and parse them into JavaScript objects
    const csvFiles = await Promise.all(
        translationFiles.map(file => loadCSV(file))
    );

    // Combine all translations in one object
    const translations = {};

    csvFiles.forEach(csv => {
        Object.assign(translations, csv);
    });

    // Get selected language
    const language = await getLanguage();

    // Translate the page
    translatePage(translations, language);

    // Return translations and language
    return {
        translations,
        language
    };
}

// This function waits till the header is loaded
document.addEventListener("DOMContentLoaded", async () => {

    // If the page has a header, wait for it to load
    if (document.getElementById("header")) {
        await new Promise(resolve => {
            document.addEventListener("headerLoaded", resolve, { once: true });
        });
    }

    // Initialize translations
    await initLanguage();
});

// This function returns the csv as a text
async function loadCSV(file) {
    // Fetches the CSV file from the specified path
    const response = await fetch(file);

    // Checks if the response is not OK and logs an error if so
    if (!response.ok) {
        console.error(`Could not load translation file: ${file}`);
        return {};
    }

    // Returns the parsed CSV data as an object
    const csvText = await response.text();
    return parseCSV(csvText);
}

// Convert CSV text to a JavaScript object
function parseCSV(csvText) {

    const lines = csvText.trim().split("\n");

    // Gets the language names from the first line
    const headers = parseCSVLine(lines[0]);

    const translations = {};

    for (let i = 1; i < lines.length; i++) {

        const values = parseCSVLine(lines[i]);

        const key = values[0];

        translations[key] = {};

        for (let j = 1; j < headers.length; j++) {

            translations[key][headers[j]] = values[j];

        }
    }

    return translations;
}

function parseCSVLine(line) {

    const values = [];
    let currentValue = "";
    let insideQuotes = false;

    // Goes through each character in the line    
    for (let i = 0; i < line.length; i++) {

        const character = line[i];

        // Handles quoted values and commas
        if (character === '"') {

            // If the character is a quote, check if it's an escaped quote
            if (insideQuotes && line[i + 1] === '"') {
                currentValue += '"';
                i++;
            } else {
                insideQuotes = !insideQuotes;
            }
        
        // If the character is a comma and we're not inside quotes, it indicates the end of a value
        } else if (character === ',' && !insideQuotes) {
            values.push(currentValue);
            currentValue = "";
        } else {
            currentValue += character;
        }
    }

    values.push(currentValue);
    return values;
}

// This function translates the page
function translatePage(translations, language) {

    // Selects all elements that have the data-i18n attribute
    const elements = document.querySelectorAll("[data-i18n]");

    // Goes over each element and updates its text
    elements.forEach(element => {

        // Gets the translation key from the data-i18n attribute
        const key = element.dataset.i18n;

        // Checks if the translation exists. If it is, updates the text
        if (translations[key] && translations[key][language]) {

            // Check if the element has a placeholder attribute
            if (element.hasAttribute("placeholder")) {
                element.placeholder = translations[key][language];
            } else {
                element.textContent = translations[key][language];
            }
        }
    });
}

// Function to show debug messages to the user but translated
function showMessage(Element, messageKey, type) {
    const messageElement = document.getElementById(Element);
    messageElement.textContent = ""; // Clear any existing text content

    messageElement.setAttribute("data-i18n", messageKey); // Set the data-i18n attribute for translation
    messageElement.classList.remove("success", "error"); // Remove any existing classes
    messageElement.classList.add(type); // Add the appropriate class based on the type (success or error)
    initLanguage(); // Re-initialize the language after setting the message
}