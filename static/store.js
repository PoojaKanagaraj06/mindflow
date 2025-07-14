const firebaseConfig = {
    apiKey: "AIzaSyAxhL77J1VfZJd3rqRyR-AtlPYSnZoXnn4",
    authDomain: "task-mate-90eee.firebaseapp.com",
    projectId: "task-mate-90eee",
    storageBucket: "task-mate-90eee.firebasestorage.app",
    messagingSenderId: "112228413597",
    appId: "1:112228413597:web:9f77d62ecf0478394f6474",
      databaseURL:"https://task-mate-90eee-default-rtdb.firebaseio.com/",
    measurementId: "G-YVTN10T1Q2"
};
// Check if Firebase is already initialized before initializing again
if (!firebase.apps || !firebase.apps.length) {
    // Initialize Firebase only if it's not already initialized
    firebase.initializeApp(firebaseConfig);
} else {
    // Use the existing initialized Firebase instance
    firebase.app();
}
// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Create database reference
const database = firebase.database();
const auth = firebase.auth();

// Save user function with Firebase Authentication
function saveUser(name, email, password) {
    // First create the authentication account
    auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // User created successfully in authentication
            const user = userCredential.user;
            
            // Now store additional user data in the database
            const usersRef = database.ref('users/' + user.uid);
            return usersRef.set({
                name: name,
                email: email,
                createdAt: new Date().toISOString()
            });
        })
        .then(() => {
            console.log("User created successfully");
            alert("Account created successfully!");
            // Optionally switch to login form after signup
            if (typeof switchAuthForm === 'function') {
                switchAuthForm('login');
            }
        })
        .catch((error) => {
            console.error("Error creating user:", error);
            alert("Error creating account: " + error.message);
        });
}

// Login user function with Firebase Authentication
// Modify the loginUser function in store.js
function loginUser(email, password) {
    // Show some loading indication
    console.log("Attempting login with:", email);
    
    auth.signInWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // User signed in successfully
            const user = userCredential.user;
            console.log("User logged in successfully:", user.email);
            alert("Login successful!");
            // Redirect to dashboard or home page
            window.location.href = "/dashboard";
        })
        .catch((error) => {
            console.error("Login error:", error);
            
            // Provide a more user-friendly error message
            let errorMessage = "Login failed. ";
            
            switch(error.code) {
                case 'auth/invalid-email':
                    errorMessage += "Please enter a valid email address.";
                    break;
                case 'auth/user-disabled':
                    errorMessage += "This account has been disabled.";
                    break;
                case 'auth/user-not-found':
                    errorMessage += "No account found with this email.";
                    break;
                case 'auth/wrong-password':
                    errorMessage += "Incorrect password.";
                    break;
                case 'auth/invalid-login-credentials':
                    errorMessage += "Invalid email or password.";
                    break;
                default:
                    errorMessage += error.message;
            }
            
            alert(errorMessage);
        });
}
// Google Sign In
function googleSignIn() {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then((result) => {
            // Google sign-in successful
            const user = result.user;
            
            // Check if user exists in database, if not create entry
            const usersRef = database.ref('users/' + user.uid);
            usersRef.once('value')
                .then((snapshot) => {
                    if (!snapshot.exists()) {
                        // User doesn't exist, create a new entry
                        return usersRef.set({
                            name: user.displayName || 'User',
                            email: user.email,
                            createdAt: new Date().toISOString()
                        });
                    }
                })
                .then(() => {
                    // Redirect to dashboard
                    window.location.href = "/dashboard";
                });
        })
        .catch((error) => {
            console.error("Google sign-in error:", error);
            alert("Google sign-in failed: " + error.message);
        });
}
// Function to fetch and display task statistics
function fetchAndDisplayTaskStats(uid) {
const stats = {
    total: 0,
    completed: 0,
    pending: 0
};
const tasksRef = database.ref('users/' + uid + '/tasks');
tasksRef.once('value')
    .then((snapshot) => {
        snapshot.forEach((child) => {
            stats.total++;
            if (child.val().completed) {
                stats.completed++;
            } else {
                stats.pending++;
            }
        });
        // Display stats in dashboard (dex.html)
        // Make sure you have elements with these IDs in your HTML
        document.getElementById('totalTasks').textContent = stats.total;
        document.getElementById('completedTasks').textContent = stats.completed;
        document.getElementById('pendingTasks').textContent = stats.pending;
    })
    .catch((error) => {
        console.error("Error fetching task stats:", error);
    });
}
// Add event listener for the signup form
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var name = getElementVal('signupName');
            var email = getElementVal('signupEmail');
            var password = getElementVal('signupPassword');
            saveUser(name, email, password);
        });
    }
    
    // Add event listener for login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var email = getElementVal('loginEmail');
            var password = getElementVal('loginPassword');
            loginUser(email, password);
        });
    }
    
    // Add event listener for Google Sign In
    const googleSignInButton = document.getElementById('googleSignIn');
    if (googleSignInButton) {
        googleSignInButton.addEventListener('click', googleSignIn);
    }
});
    
document.addEventListener('DOMContentLoaded', function() {
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var taskTitle = getElementVal('taskTitle');
            var taskDescription = getElementVal('taskDescription');
            saveTask(taskTitle, taskDescription);
            taskForm.reset();
        });
    }
});

// Save task function - now it associates tasks with the current user
// Save task function - now it associates tasks with the current user
function saveTask(title, description) {
    const user = auth.currentUser;
    if (!user) {
        alert("You must be logged in to create tasks");
        return;
    }
    
    // Save to user-specific location to match the loading logic
    const userTasksRef = database.ref('users/' + user.uid + '/tasks');
    const newTask = userTasksRef.push();
    newTask.set({
        userId: user.uid,
        title: title,
        description: description,
        text: title, // Add this for compatibility with index.html
        createdAt: new Date().toISOString(),
        completed: false
    })
    .then(() => {
        console.log("Task saved successfully");
    })
    .catch((error) => {
        console.error("Error saving task:", error);
        alert("Error saving task: " + error.message);
    });
}

function deleteTask(taskId) {
    const user = auth.currentUser;
    if (!user) {
        alert("You must be logged in to delete tasks");
        return;
    }
    
    const taskRef = database.ref('users/' + user.uid + '/tasks/' + taskId);
    taskRef.remove()
    .then(() => {
        console.log("Task deleted successfully");
    })
    .catch((error) => {
        console.error("Error deleting task:", error);
        alert("Error deleting task: " + error.message);
    });
}

const getElementVal = (id) => {
    return document.getElementById(id).value;
}

// Check authentication state
// In store.js, update the auth state listener
// In store.js, update the auth state listener
// Check authentication state
auth.onAuthStateChanged((user) => {
  if (user) {
    // User is signed in
    console.log("User is signed in:", user.email);
    
    // Load tasks when user is authenticated
    const currentPath = window.location.pathname;
    if (currentPath === '/' || currentPath.includes('dashboard')) {
      // Call the loadTasksFromFirebase function if it exists
      if (typeof window.loadTasksFromFirebase === 'function') {
        window.loadTasksFromFirebase();
      }
    }
  } else {
    // User is signed out
    console.log("User is signed out");
    
    // Only redirect from dashboard, not from tasks page
    const currentPath = window.location.pathname;
    if (currentPath.includes('dashboard')) {
      window.location.href = "/login";
    }
  }
});