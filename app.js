const modal = document.getElementById('auth-modal');
document.getElementById('open-login-btn')?.addEventListener('click', () => modal.classList.add('open'));
document.getElementById('open-signup-btn')?.addEventListener('click', () => modal.classList.add('open'));
document.getElementById('close-modal-btn')?.addEventListener('click', () => modal.classList.remove('open'));

const loginTab = document.getElementById('login-tab-btn');
const signupTab = document.getElementById('signup-tab-btn');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');

loginTab?.addEventListener('click', () => {
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
});

signupTab?.addEventListener('click', () => {
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
});

const avatarBtn = document.getElementById('user-avatar-btn');
const dropdown = document.getElementById('account-dropdown');
avatarBtn?.addEventListener('click', () => dropdown.classList.toggle('show'));

document.addEventListener('DOMContentLoaded', () => {
    let selectedMeals = [];

    document.querySelectorAll('.meal-card').forEach(card => {
        card.addEventListener('dragstart', (e) => {
            const recipeData = {
                id: e.target.dataset.id,
                title: e.target.dataset.title,
                ingredients: JSON.parse(e.target.dataset.ingredients || '[]')
            };
            e.dataTransfer.setData('application/json', JSON.stringify(recipeData));
        });
    });

    document.querySelectorAll('.day-slot').forEach(slot => {
        slot.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        slot.addEventListener('drop', (e) => {
            e.preventDefault();
            const recipeData = JSON.parse(e.dataTransfer.getData('application/json'));
            const day = e.target.closest('.day-slot').dataset.day;
            
            selectedMeals.push({ day, ...recipeData });
            renderMealInSlot(slot, recipeData);
            updateShoppingList(selectedMeals);
        });
    });
});

async function updateShoppingList(meals) {
    const response = await fetch('/api/generate-shopping-list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meals })
    });
    const data = await response.json();
    renderShoppingList(data.shopping_list);
}