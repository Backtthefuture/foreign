async function generateName() {
    const englishName = document.getElementById('englishName').value.trim();
    if (!englishName) {
        alert('Please enter your English name');
        return;
    }

    // 显示加载动画
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    loadingDiv.style.display = 'block';

    // 开始加载动画
    const steps = document.querySelectorAll('.loading-step');
    let currentStep = 0;
    
    const animateSteps = async () => {
        if (currentStep > 0) {
            steps[currentStep - 1].classList.remove('active');
            steps[currentStep - 1].classList.add('completed');
        }
        if (currentStep < steps.length) {
            steps[currentStep].classList.add('active');
            currentStep++;
            await new Promise(resolve => setTimeout(resolve, 1000));
            return animateSteps();
        }
    };

    try {
        // 启动加载动画
        animateSteps();

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

        // 等待最后一个动画完成
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 隐藏加载动画
        loadingDiv.style.display = 'none';
        // 重置加载状态
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });

        displayResults(data.names);
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating names');
        loadingDiv.style.display = 'none';
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
            <div class="english-explanation">
                <strong>English Explanation:</strong><br>
                ${name.english_explanation}
            </div>
        `;
        resultsDiv.appendChild(nameCard);
    });
}
