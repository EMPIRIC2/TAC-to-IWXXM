// Renamed to auth.js - handles both login and registration
const API_BASE = (typeof window !== 'undefined' && window.METAR_API_BASE) ? window.METAR_API_BASE : '';

function switchTab(tab) {
  const loginSection = document.getElementById('loginSection');
  const registerSection = document.getElementById('registerSection');
  const tabs = document.querySelectorAll('.tab-btn');
  
  tabs.forEach(btn => btn.classList.remove('active'));
  
  if (tab === 'login') {
    loginSection.classList.add('active');
    registerSection.classList.remove('active');
    tabs[0].classList.add('active');
  } else {
    loginSection.classList.remove('active');
    registerSection.classList.add('active');
    tabs[1].classList.add('active');
  }
}

// Login Form Handler
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.textContent = '';
  
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  
  try {
    const resp = await fetch(API_BASE + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    if (!resp.ok) {
      const error = await resp.json();
      throw new Error(error.detail || 'Invalid credentials');
    }
    
    const data = await resp.json();
    sessionStorage.setItem('authToken', data.access_token);
    sessionStorage.setItem('userName', data.user.name);
    window.location.href = '/';
  } catch (err) {
    loginError.textContent = 'Login failed: ' + err.message;
  }
});

// Register Form Handler
const registerForm = document.getElementById('registerForm');
const registerError = document.getElementById('registerError');
const registerSuccess = document.getElementById('registerSuccess');

registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  registerError.textContent = '';
  registerSuccess.textContent = '';
  
  const userData = {
    name: document.getElementById('regName').value.trim(),
    email: document.getElementById('regEmail').value.trim(),
    address: document.getElementById('regAddress').value.trim(),
    username: document.getElementById('regUsername').value.trim(),
    password: document.getElementById('regPassword').value
  };
  
  try {
    const resp = await fetch(API_BASE + '/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    
    if (!resp.ok) {
      const error = await resp.json();
      throw new Error(error.detail || 'Registration failed');
    }
    
    registerSuccess.textContent = 'Registration successful! Switching to login...';
    registerForm.reset();
    
    // Auto-switch to login after 1.5 seconds
    setTimeout(() => switchTab('login'), 1500);
  } catch (err) {
    registerError.textContent = 'Registration failed: ' + err.message;
  }
});
