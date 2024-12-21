// Show loading indicator for anchor tag clicks
document.querySelectorAll('.loading-link').forEach(function(anchor) {
    anchor.addEventListener('click', function() {
        document.getElementById('loading').style.display = 'block';
    });
});

// Show loading indicator for form submissions
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
        document.getElementById('loading').style.display = 'block';
    });
});
