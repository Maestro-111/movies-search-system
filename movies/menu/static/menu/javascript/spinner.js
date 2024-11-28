// Function to show loading spinner
function showLoading(form) {
    document.getElementById("loading-spinner").style.display = "block";
}

// Add hover effect to buttons
document.querySelectorAll('.menu-button').forEach(button => {
    button.addEventListener('mouseover', () => {
        button.style.transform = "scale(1.05)";
    });
    button.addEventListener('mouseout', () => {
        button.style.transform = "scale(1)";
    });
});
