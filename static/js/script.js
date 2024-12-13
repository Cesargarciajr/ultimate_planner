// Select the dropdown items and the button
const dropdownItems = document.querySelectorAll('.dropdown-item');
const dropdownButton = document.getElementById('dropdownMenuButton');

// Loop through the dropdown items
dropdownItems.forEach(item => {
    item.addEventListener('click', function() {
        // Set the text of the button to the clicked item's text
        dropdownButton.textContent = item.textContent;
    });
});