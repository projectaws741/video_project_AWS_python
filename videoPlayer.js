document.addEventListener("DOMContentLoaded", function() {
    const links = document.querySelectorAll('ul li a.stream-link');
    const videoPlayer = document.getElementById('videoPlayer');
    const videoSource = document.getElementById('videoSource');

    links.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            videoSource.setAttribute('src', this.href);
            videoPlayer.load();
            videoPlayer.play();
        });
    });
});
