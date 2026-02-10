document.addEventListener('DOMContentLoaded', async () => {
  // Get session_id from URL
  const urlParams = new URLSearchParams(window.location.search);
  const sessionId = urlParams.get('session_id');

  if (!sessionId) {
    console.warn('No session_id found in URL');
    showError('No payment session information found.');
    return;
  }

  // Fill hidden input with sessionId (for customer portal form)
  const sessionIdInput = document.getElementById('sessionId');
  if (sessionIdInput) {
    sessionIdInput.value = sessionId;
  } else {
    console.warn('Hidden input #sessionId not found in DOM');
  }

  // Find the <pre> element to display session details
  const preElement = document.querySelector('pre');
  if (!preElement) {
    console.warn('No <pre> element found to display session data');
    return;
  }

  preElement.textContent = 'Loading payment details...';

  try {
    const response = await fetch(`/checkout-session?sessionId=${encodeURIComponent(sessionId)}`);

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status} ${response.statusText}`);
    }

    const session = await response.json();

    // Session data received — now we can check status
    if (session.payment_status === 'paid') {
      preElement.innerHTML = `
        <strong>Thank you!</strong><br><br>
        Your payment was successful.<br>
        Plan: ${session.line_items?.data?.[0]?.price?.nickname || 'Subscription'}<br>
        Amount: $${(session.amount_total / 100).toFixed(2)}<br>
        Email: ${session.customer_email || 'N/A'}<br>
        Subscription ID: ${session.subscription || 'N/A'}<br><br>
        Your subscription is now active!
      `;
      preElement.style.color = '#2e7d32'; // green color
    } else {
      // If not paid, show full JSON for debugging
      preElement.textContent = JSON.stringify(session, null, 2);
      preElement.style.color = '#d32f2f'; // red color — something is wrong
    }

  } catch (err) {
    console.error('Error loading session:', err);

    preElement.style.color = '#d32f2f';
    preElement.textContent =
      'Failed to load payment details.\n\n' +
      (err.message || 'Unknown error') +
      '\n\nPlease contact support if the issue persists.';
  }
});

// Simple helper function to show errors
function showError(message) {
  const pre = document.querySelector('pre');
  if (pre) {
    pre.style.color = '#d32f2f';
    pre.textContent = message;
  }
}