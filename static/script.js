/* Fetch prices and update the form */
document.addEventListener('DOMContentLoaded', () => {
  fetch('/config')
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      document.getElementById('monthlyPrice').value = data.monthlyPrice || '';
      document.getElementById('yearlyPrice').value   = data.yearlyPrice   || '';
    })
    .catch(err => {
      console.error('Failed to load prices:', err);
      document.getElementById('error-message').textContent = 
        'Unable to load plans. Please refresh the page.';
    });
});