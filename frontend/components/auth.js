// Hide the page until the session is verified
document.documentElement.classList.add("checking-session");

(async () => {

    try {

        // Verify the session by making a request to the backend
        const response = await fetch("/api/");

        // If session invalid, the backend will redirect to the login page
        if (response.redirected) {
            window.location.replace(response.url);
            return;
        }

        // If the session is valid, remove the "checking-session" class to show the page
        if (response.status === 200) {
            document.documentElement.classList.remove("checking-session");
            return;
        }

    } catch (error) {
        // If there's an error (e.g., network issue), log it and redirect to the login page
        window.location.replace("/login.html");
        console.error("Error verifying session:", error);
    }

})();