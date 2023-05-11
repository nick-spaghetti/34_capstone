const toggleSwitch = document.querySelector('input[type="checkbox"]');

if (localStorage.getItem('darkModeEnabled')) {
    document.body.className = 'dark';
    toggleSwitch.checked = true;
}

toggleSwitch.addEventListener('click', (e) => {
    const checked = toggleSwitch.checked;
    if (checked) {
        localStorage.setItem('darkModeEnabled', true);

    } else {
        localStorage.removeItem('darkModeEnabled');
    }
    document.body.className = checked ? 'dark' : "";
});