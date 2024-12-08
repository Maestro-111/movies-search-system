document.querySelector('form').addEventListener('submit', function() {
    document.getElementById('loading').style.display = 'block';
});

document.addEventListener("DOMContentLoaded", function () {

    const imageInput = document.getElementById("image");
    const uploadMessage = document.getElementById("upload-message");

    imageInput.addEventListener("change", function () {
        if (imageInput.files && imageInput.files.length > 0) {
            // Display the message
            uploadMessage.style.display = "block";
        } else {
            // Hide the message if no file is selected
            uploadMessage.style.display = "none";
        }
    });
});
