/**
 * Bike Rental Demand Prediction - Frontend Interactivity & API Client
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('predictionForm');
  const submitBtn = document.getElementById('submitBtn');
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');

  const resultsPlaceholder = document.getElementById('resultsPlaceholder');
  const resultsContent = document.getElementById('resultsContent');
  const resultCountEl = document.getElementById('resultCount');
  const rawPredEl = document.getElementById('rawPred');
  const demandBadgeEl = document.getElementById('demandBadge');
  const resultSeasonEl = document.getElementById('resultSeason');
  const resultTempEl = document.getElementById('resultTemp');
  const resultHourEl = document.getElementById('resultHour');

  // Preset configuration datasets
  const presets = {
    summerPeak: {
      Date: '2025-07-15',
      Hour: 18,
      Temperature: 28.5,
      Humidity: 45,
      'Wind speed': 2.5,
      Visibility: 1950,
      'Dew point temperature': 16.0,
      'Solar Radiation': 2.45,
      Rainfall: 0.0,
      Snowfall: 0.0,
      Seasons: 'Summer',
      Holiday: 'No Holiday',
      'Functioning Day': 'Yes'
    },
    rainyAutumn: {
      Date: '2025-10-10',
      Hour: 21,
      Temperature: 11.2,
      Humidity: 88,
      'Wind speed': 4.2,
      Visibility: 850,
      'Dew point temperature': 9.1,
      'Solar Radiation': 0.0,
      Rainfall: 4.5,
      Snowfall: 0.0,
      Seasons: 'Autumn',
      Holiday: 'No Holiday',
      'Functioning Day': 'Yes'
    },
    freezingWinter: {
      Date: '2025-01-20',
      Hour: 8,
      Temperature: -6.5,
      Humidity: 70,
      'Wind speed': 5.8,
      Visibility: 1200,
      'Dew point temperature': -11.0,
      'Solar Radiation': 0.15,
      Rainfall: 0.0,
      Snowfall: 1.2,
      Seasons: 'Winter',
      Holiday: 'Holiday',
      'Functioning Day': 'No'
    }
  };

  // Populate default date with today's date if empty
  const dateInput = document.getElementById('Date');
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }

  // Handle Preset Buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const presetKey = e.currentTarget.getAttribute('data-preset');
      if (presets[presetKey]) {
        loadPresetData(presets[presetKey]);
      }
    });
  });

  function loadPresetData(data) {
    Object.keys(data).forEach(key => {
      const input = document.getElementById(key);
      if (input) {
        input.value = data[key];
        input.dispatchEvent(new Event('change'));
      }
    });
  }

  // Client side validation rules
  function validateForm() {
    let isValid = true;
    const inputs = form.querySelectorAll('.input-control');

    inputs.forEach(input => {
      const group = input.closest('.field-group');
      const val = input.value.trim();
      const type = input.getAttribute('type');

      let fieldError = false;

      if (!val && input.hasAttribute('required')) {
        fieldError = true;
      } else if (type === 'number') {
        const numVal = parseFloat(val);
        const min = input.getAttribute('min');
        const max = input.getAttribute('max');

        if (isNaN(numVal)) {
          fieldError = true;
        } else if (min !== null && numVal < parseFloat(min)) {
          fieldError = true;
        } else if (max !== null && numVal > parseFloat(max)) {
          fieldError = true;
        }
      }

      if (fieldError) {
        group.classList.add('has-error');
        isValid = false;
      } else {
        group.classList.remove('has-error');
      }
    });

    return isValid;
  }

  // Remove error state on user typing
  form.querySelectorAll('.input-control').forEach(input => {
    input.addEventListener('input', () => {
      const group = input.closest('.field-group');
      group.classList.remove('has-error');
    });
  });

  // Handle Form Submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Prepare JSON payload matching BikePredictionInput schema
    const payload = {
      Date: document.getElementById('Date').value,
      Hour: parseInt(document.getElementById('Hour').value, 10),
      Temperature: parseFloat(document.getElementById('Temperature').value),
      Humidity: parseFloat(document.getElementById('Humidity').value),
      "Wind speed": parseFloat(document.getElementById('Wind speed').value),
      Visibility: parseFloat(document.getElementById('Visibility').value),
      "Dew point temperature": parseFloat(document.getElementById('Dew point temperature').value),
      "Solar Radiation": parseFloat(document.getElementById('Solar Radiation').value),
      Rainfall: parseFloat(document.getElementById('Rainfall').value),
      Snowfall: parseFloat(document.getElementById('Snowfall').value),
      Seasons: document.getElementById('Seasons').value,
      Holiday: document.getElementById('Holiday').value,
      "Functioning Day": document.getElementById('Functioning Day').value
    };

    // UI Loading state
    submitBtn.disabled = true;
    btnSpinner.style.display = 'inline-block';
    btnText.textContent = 'Analyzing & Predicting...';

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Prediction request failed');
      }

      const result = await response.json();
      displayPredictionResult(result, payload);

    } catch (err) {
      alert(`Prediction Error: ${err.message}`);
    } finally {
      submitBtn.disabled = false;
      btnSpinner.style.display = 'none';
      btnText.textContent = 'Predict Bike Rental Demand';
    }
  });

  function displayPredictionResult(result, inputs) {
    resultsPlaceholder.style.display = 'none';
    resultsContent.style.display = 'flex';

    const finalCount = result.predicted_rented_bike_count;
    const rawVal = result.raw_prediction;
    const demandLevel = result.demand_level;

    // Counter animation
    animateCounter(resultCountEl, 0, finalCount, 800);
    rawPredEl.textContent = `Raw Model Output: ${rawVal} bikes`;

    // Demand badge styling
    demandBadgeEl.textContent = demandLevel;
    demandBadgeEl.className = 'demand-badge';

    if (demandLevel.includes('Peak')) demandBadgeEl.classList.add('demand-peak');
    else if (demandLevel.includes('High')) demandBadgeEl.classList.add('demand-high');
    else if (demandLevel.includes('Moderate')) demandBadgeEl.classList.add('demand-moderate');
    else if (demandLevel.includes('No Operation') || demandLevel.includes('Zero')) demandBadgeEl.classList.add('demand-closed');
    else demandBadgeEl.classList.add('demand-low');

    // Context summary
    resultSeasonEl.textContent = inputs.Seasons;
    resultTempEl.textContent = `${inputs.Temperature} °C`;
    resultHourEl.textContent = `${inputs.Hour}:00 hrs`;
  }

  function animateCounter(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const current = Math.floor(progress * (end - start) + start);
      element.textContent = current.toLocaleString();
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }
});
