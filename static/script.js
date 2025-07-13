import { initializeApp } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, updateProfile } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";
import { GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";
// Firebase configuration
// Replace with your Firebase project configuration

const firebaseConfig = {
  apiKey: "AIzaSyBc0JkWWpOSEQD2iR1oumW0cUtlNOAorXU",
  authDomain: "taskmanagement-78cbf.firebaseapp.com",
  projectId: "taskmanagement-78cbf",
  appId: "1:808721156073:web:c06b08ce752c9f2709ad78"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

window.switchAuthForm = (type) => {
  document.getElementById('loginForm').style.display = type === 'login' ? 'flex' : 'none';
  document.getElementById('signupForm').style.display = type === 'signup' ? 'flex' : 'none';
};

// Login
document.getElementById('loginForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  signInWithEmailAndPassword(auth, email, password)
    .then(() => {
      alert("Login successful!");
      window.location.href = "/index"; // go to home
    })
    .catch((error) => {
      alert("Login failed: " + error.message);
    });
});

// Sign Up
document.getElementById('signupForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const name = document.getElementById('signupName').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;

  createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      return updateProfile(userCredential.user, {
        displayName: name
      });
    })
    .then(() => {
      alert("Sign-up successful!");
      window.location.href = "/index";
    })
    .catch((error) => {
      alert("Sign-up failed: " + error.message);
    });
});

const email = document.getElementById('loginEmail');
const password = document.getElementById('loginPassword');
const submitButton = document.getElementById('loginSubmit');
email.addEventListener('input', () => {
  if (email.value && password.value) {
    submitButton.disabled = false;
  } else {
    submitButton.disabled = true;
  }
});
document.getElementById('googleSignIn').addEventListener('click', () => {
  const provider = new GoogleAuthProvider();
  signInWithPopup(auth, provider)
    .then((result) => {
      const user = result.user;
      alert("✅ Signed in with Google: " + user.displayName);
      window.location.href = "/index";
    })
    .catch((error) => {
      alert("❌ Google sign-in error: " + error.message);
    });
});
// Initialize Firebase services