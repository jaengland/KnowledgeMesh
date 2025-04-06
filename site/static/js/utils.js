export const selectFn = (el, all = false) => {
    el = el.trim();
    return all ? [...document.querySelectorAll(el)] : document.querySelector(el);
};

export const generateAndPlaceResults = (jsonArray, selectFn) => {
    // Parse the JSON array if it's a string
    const items = typeof jsonArray === 'string' ? JSON.parse(jsonArray) : jsonArray;

    // Select the container where tiles will be appended
    const container = selectFn('.resultsContainer');
    console.log(container);

    // Clear the container before appending new results
    container.innerHTML = '';
    
    // Create and append tiles for each item
    items.forEach(item => {
        const result = document.createElement('div');
        result.className = 'resultContainer';
        var tagstring = item.tags.join(", ");
        result.innerHTML = `
            <div class="titleURL">
                <a target="_blank" href="${item.url}">
                  <div class="result-title"><h4>${item.title}</h4></div>
                  <div class="result-url">${item.url}</div>
                </a>
                <div class="result-description"><p>${item.description}</p></div>
                <div class="result-footer">
                  <div class="result-tags">Tags: ${tagstring}</div>
                </div>
            </div>
        `;

        container.appendChild(result);
    });
};