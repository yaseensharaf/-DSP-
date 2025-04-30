// Wait for the document to load
document.addEventListener('DOMContentLoaded', function () {
    // Dark mode switch
    var modeSwitch = document.querySelector('.mode-switch');
    
    // Check localStorage on page load and set the initial mode
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark');
        modeSwitch.classList.add('active');
    } else {
        // Ensure we start with light mode if no preference is stored
        document.documentElement.classList.remove('dark');
        modeSwitch.classList.remove('active');
        // Set default to light mode in localStorage if not set
        if (!localStorage.getItem('darkMode')) {
            localStorage.setItem('darkMode', 'false');
        }
    }
    
    // Toggle mode when switch is clicked
    modeSwitch.addEventListener('click', function () {
        document.documentElement.classList.toggle('dark');
        modeSwitch.classList.toggle('active');
        localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
    });
});

function showProductImage(productName) {
    fetch(`/product_image/${encodeURIComponent(productName)}`)
        .then(response => response.json())
        .then(data => {
            console.log("Data from product_image route:", data);
            if (data.error) {
                alert(data.error);
                return;
            }
            document.getElementById('image-title').innerText = `Sales Forecast For ${productName}`;
            const img = document.getElementById('product-image');
            img.src = data.image_url;
            img.style.display = 'block';
            document.getElementById('image-container').style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching the product image.');
        });
}
function goBackToList() {
    const imageContainer = document.getElementById('image-container');
    const productImage = document.getElementById('product-image');
    const imageTitle = document.getElementById('image-title');

    imageContainer.style.display = 'none';
    productImage.src = '';
    imageTitle.innerText = '';
}


function filterProjects() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const storeFilter = document.getElementById('store-filter').value.toLowerCase();
    const allProjects = Array.from(document.querySelectorAll('.project-box-wrapper'));

    allProjects.forEach(project => {
        const productName = project.dataset.productName.toLowerCase();
        const category = project.dataset.category.toLowerCase();
        const store = project.dataset.store.toLowerCase();

        const matchesSearch = productName.includes(searchTerm) || category.includes(searchTerm);
        const matchesStore = storeFilter === 'all' || store === storeFilter;

        project.style.display = (matchesSearch && matchesStore) ? 'block' : 'none';
    });
}

document.getElementById('search-input').addEventListener('input', filterProjects);
document.getElementById('store-filter').addEventListener('change', filterProjects);

// Toggle sidebar on mobile
document.querySelector('.sidebar-toggle').addEventListener('click', () => {
    document.querySelector('.app-sidebar').classList.toggle('active');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 720 && !e.target.closest('.app-sidebar') && !e.target.closest('.sidebar-toggle')) {
        document.querySelector('.app-sidebar').classList.remove('active');
    }
});