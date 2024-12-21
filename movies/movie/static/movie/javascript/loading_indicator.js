
    // Show loading indicator on form submission
    document.querySelector('form').addEventListener('submit', function () {
        document.getElementById('loading').style.display = 'block';
    });

    // Show loading indicator when clicking on a movie link
    document.addEventListener('DOMContentLoaded', function () {
        const movieLinks = document.querySelectorAll('a'); // Get all anchor tags
        movieLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                document.getElementById('loading').style.display = 'block';
            });
        });

        // Handle file upload display
        const imageInput = document.getElementById("image");
        const uploadMessage = document.getElementById("upload-message");

        imageInput.addEventListener("change", function () {
            if (imageInput.files && imageInput.files.length > 0) {
                uploadMessage.style.display = "block";
            } else {
                uploadMessage.style.display = "none";
            }
        });
    });

