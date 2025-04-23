function showPopup(event, content) {
    const popup = document.getElementById('popup');
    popup.innerHTML = content;
    popup.style.display = 'block';
    popup.style.left = event.pageX + 10 + 'px';
    popup.style.top = event.pageY + 10 + 'px';
}

function hidePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}
