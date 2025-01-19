export function initDashboard() {
  // Initialize all dashboard components
  initSleepStats();
  initSoundAnalysis();
  initNightlyOverview();
  initSoundClassification();
}

function initSleepStats() {
  const statsContent = document.getElementById('sleep-stats');
  const sleepData = analyzeSleepPattern();
  
  statsContent.innerHTML = `
    <div class="stat-item">
      <h4>Sleep Duration</h4>
      <p>${sleepData.duration} hours</p>
    </div>
    <div class="stat-item">
      <h4>Sleep Quality</h4>
      <p>${sleepData.quality}%</p>
    </div>
    <div class="stat-item">
      <h4>Number of Wakings</h4>
      <p>${sleepData.wakings}</p>
    </div>
  `;
}

function initSoundAnalysis() {
  const ctx = document.getElementById('soundChart').getContext('2d');
  const soundData = getSoundData();
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: soundData.times,
      datasets: [{
        label: 'Sound Level (dB)',
        data: soundData.levels,
        borderColor: '#4A90E2',
        fill: false,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Sound Level Throughout Night'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const soundType = getSoundType(context.raw);
              return `${context.raw}dB - ${soundType}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Sound Level (dB)'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        }
      }
    }
  });
}

function initNightlyOverview() {
  const ctx = document.getElementById('nightlyOverview').getContext('2d');
  const nightData = getNightlyData();
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: nightData.timeSlots,
      datasets: [{
        label: 'Sleep State',
        data: nightData.sleepStates,
        backgroundColor: '#27AE60',
        borderColor: '#27AE60'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Nightly Sleep Pattern'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 1,
          ticks: {
            callback: function(value) {
              return value === 0 ? 'Awake' : 'Asleep';
            }
          }
        }
      }
    }
  });
}

function initSoundClassification() {
  const ctx = document.getElementById('soundClassification').getContext('2d');
  const classificationData = getSoundClassification();
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Crying', 'Babbling', 'Ambient Noise', 'Other'],
      datasets: [{
        data: classificationData,
        backgroundColor: [
          '#FF6B6B',
          '#4ECDC4',
          '#45B7D1',
          '#96CEB4'
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Sound Classification Distribution'
        }
      }
    }
  });
}

// Helper functions
function analyzeSleepPattern() {
  // Simulated sleep analysis
  return {
    duration: 8.5,
    quality: 85,
    wakings: 3
  };
}

function getSoundData() {
  // Simulated 24-hour sound data
  const times = Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`);
  const levels = Array.from({length: 24}, () => Math.floor(Math.random() * 40 + 20));
  
  return { times, levels };
}

function getSoundType(level) {
  if (level > 50) return 'Crying';
  if (level > 40) return 'Babbling';
  return 'Ambient';
}

function getNightlyData() {
  const timeSlots = Array.from({length: 48}, (_, i) => {
    const hour = Math.floor(i/2).toString().padStart(2, '0');
    const minute = (i % 2) * 30;
    return `${hour}:${minute.toString().padStart(2, '0')}`;
  });
  
  const sleepStates = generateSleepStates(48);
  return { timeSlots, sleepStates };
}

function generateSleepStates(length) {
  return Array.from({length}, (_, i) => {
    // Simulate typical sleep pattern (more likely to be asleep at night)
    const hour = Math.floor(i/2);
    const nighttime = (hour >= 19 || hour <= 6);
    return nighttime ? (Math.random() > 0.1 ? 1 : 0) : (Math.random() > 0.8 ? 1 : 0);
  });
}

function getSoundClassification() {
  // Simulated sound classification distribution
  return [15, 25, 45, 15];
}