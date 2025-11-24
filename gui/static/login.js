const API_BASE = (typeof window !== 'undefined' && window.METAR_API_BASE) ? window.METAR_API_BASE : '';
const form = document.getElementById('loginForm');
const msg = document.getElementById('loginMsg');
const requestResetBtn = document.getElementById('requestReset');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  msg.textContent = '';
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  try {
    const resp = await fetch(API_BASE + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!resp.ok) {
      throw new Error('Invalid credentials');
    }
    const data = await resp.json();
    // Store token in sessionStorage for simplicity
    sessionStorage.setItem('authToken', data.access_token);
    window.location.href = '/';
  } catch (err) {
    msg.style.color = 'tomato';
    msg.textContent = 'Login failed: ' + err.message;
  }
});

requestResetBtn.addEventListener('click', async () => {
  const username = document.getElementById('username').value.trim();
  if (!username) {
    msg.style.color = 'tomato';
    msg.textContent = 'Enter username (we will look up email)';
    return;
  }
  // Fetch user to get email (could be improved by dedicated endpoint)
  try {
    const probe = await fetch(API_BASE + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password: 'INVALID-PROBE' })
    });
    if (probe.ok) {
      msg.textContent = 'Already logged in?';
      return;
    }
  } catch (_) {}
  // Ask for email directly
  const email = prompt('Enter your account email for reset link:');
  if (!email) return;
  try {
    const resp = await fetch(API_BASE + '/auth/password-reset/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await resp.json();
    msg.style.color = 'green';
    msg.textContent = data.message;
  } catch (err) {
    msg.style.color = 'tomato';
    msg.textContent = 'Reset request failed';
  }
});

// Redirect to login if trying to access protected page without token
if (window.location.pathname === '/' && !sessionStorage.getItem('authToken')) {
  window.location.href = '/static/login.html';
}
