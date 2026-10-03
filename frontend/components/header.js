// Listen when the site is loaded. Then setup the header.
document.addEventListener("DOMContentLoaded", async () => { // Wait for the DOM to be fully loaded before executing the code

    // Get the header container in the HTML
    const headerContainer = document.getElementById("header");

    if (!headerContainer) {
        return;
    }

    // Fetch the header HTML and insert it into the header container
    const response = await fetch("/components/header.html");
    const headerHTML = await response.text();
    headerContainer.innerHTML = headerHTML;

    setupLanguageMenu(); // Set up the language menu functionality
    setupProfileMenu(); // Set up the profile menu functionality

    // Dispatch a custom event to signal that the header has been loaded
    document.dispatchEvent(new Event("headerLoaded"));
});

// Configure the language dropdown
function setupLanguageMenu() {

    // Get the language button and dropdown elements
    const button =
        document.getElementById("language-button");

    const dropdown =
        document.getElementById("language-dropdown");


    if (!button || !dropdown) {
        return;
    }

    // Listen for clicks on the language button to toggle the dropdown
    button.addEventListener("click", () => {

        const profileDropdown =
            document.getElementById("profile-dropdown");

        profileDropdown.classList.remove("show");

        dropdown.classList.toggle("show");

    });

    // Get all the language buttons in the dropdown
    const languageButtons =
        dropdown.querySelectorAll("[data-language]");

    // Add click event listeners to each language button   
    languageButtons.forEach(languageButton => {

        languageButton.addEventListener("click", async () => {
            // Get the selected language and update the DB/cookies
            const language = languageButton.dataset.language;
            await setLanguage(language);
            location.reload();
        });
    });

}

// Configure the profile dropdown
function setupProfileMenu() {

    // Get the profile button and dropdown elements
    const button =
        document.getElementById("profile-button");

    const dropdown =
        document.getElementById("profile-dropdown");


    if (!button || !dropdown) {
        return;
    }

    // Listen for clicks on the profile button to toggle the dropdown
    button.addEventListener("click", () => {

        const languageDropdown =
            document.getElementById("language-dropdown");

        languageDropdown.classList.remove("show");

        dropdown.classList.toggle("show");

    });

}