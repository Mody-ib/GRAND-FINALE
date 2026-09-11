function renderMealInSlot(slotElement, recipe) {
    const mealElement = document.createElement('div');
    mealElement.className = 'scheduled-meal';
    mealElement.innerHTML = `
        <span>${recipe.title}</span>
        <button class="remove-btn">&times;</button>
    `;
    
    mealElement.querySelector('.remove-btn').addEventListener('click', () => {
        mealElement.remove();
    });

    slotElement.appendChild(mealElement);
}

function renderShoppingList(categorizedItems) {
    const listContainer = document.getElementById('shopping-list');
    if (!listContainer) return;
    
    listContainer.innerHTML = '';

    for (const [aisle, items] of Object.entries(categorizedItems)) {
        const aisleSection = document.createElement('div');
        aisleSection.className = 'aisle-group';
        
        const aisleTitle = document.createElement('h4');
        aisleTitle.textContent = aisle;
        aisleSection.appendChild(aisleTitle);

        const itemList = document.createElement('ul');
        items.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <label>
                    <input type="checkbox" />
                    ${item.qty} ${item.item}
                </label>
            `;
            itemList.appendChild(li);
        });

        aisleSection.appendChild(itemList);
        listContainer.appendChild(aisleSection);
    }
}