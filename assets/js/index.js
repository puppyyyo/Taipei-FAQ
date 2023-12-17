const form = document.getElementById('searchForm');
const searchResultBox = document.getElementById('search-result-box');
const searchForm = document.querySelector('.search-form');

const unitElement = document.getElementById('unit-info');
const addressElement = document.getElementById('address-info');
const phoneElement = document.getElementById('phone-info');
const faxElement = document.getElementById('fax-info');
const serviceElement = document.getElementById('service-info');

function fillInfo (element, dataField, notFoundMessage) {
    if (data.unit_info && data.unit_info[dataField]) {
        element.innerText = data.unit_info[dataField];
    } else {
        element.innerText = notFoundMessage;
    }
};

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const searchInput = document.getElementById('search-query').value.trim();

    if (searchInput) {
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json',},
                body: JSON.stringify({ query: searchInput }),
            });

            if (response.ok) {
                const data = await response.json();

                console.log(data);

                fillInfo(addressElement, 'address', 'Address not found');
                fillInfo(phoneElement, 'phone', 'Phone not found');
                fillInfo(faxElement, 'fax', 'Fax not found');
                fillInfo(serviceElement, 'service', 'Service time not found');

                if (data.unit_info && data.unit_info['link']) {
                    unitElement.innerHTML = '';
                    const link = document.createElement('a');
                    link.href = data.unit_info['link'];
                    link.target = '_blank';
                    link.textContent = data.unit_info['unit']; 
                    unitElement.appendChild(link);
                  }
                  
            } else {
                unitElement.innerText = 'Search failed';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    } else {
        unitElement.innerText = 'Please enter a search query';
    }

    searchResultBox.style.display = 'block';
});