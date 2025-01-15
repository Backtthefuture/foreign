async function generateName() {
    const englishName = document.getElementById('englishName').value.trim();
    if (!englishName) {
        alert('Please enter your English name');
        return;
    }

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: englishName })
        });

        const data = await response.json();
        if (data.error) {
            alert(data.error);
            return;
        }

        displayResults(data.names);
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating names');
    }
}

function displayResults(names) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    names.forEach((name, index) => {
        const nameCard = document.createElement('div');
        nameCard.className = 'name-card';
        nameCard.innerHTML = `
            <h2>Option ${index + 1}: ${name.chinese_name}</h2>
            <div class="pinyin">Pinyin: ${name.pinyin}</div>
            <div class="meaning">
                <strong>Meaning:</strong> ${name.meaning}
            </div>
            <div class="cultural-explanation">
                <strong>Cultural Explanation:</strong><br>
                ${name.cultural_explanation}
            </div>
            <div class="personality">
                <strong>Personality Traits:</strong><br>
                ${name.personality_traits}
            </div>
            <div class="english-explanation">
                <strong>English Explanation:</strong><br>
                ${name.english_explanation}
            </div>
        `;
        resultsDiv.appendChild(nameCard);
    });
}
