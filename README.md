# 🌱 Eco Campus Tracker

Eco Campus Tracker is a web-based campus sustainability platform designed to encourage students to participate in eco-friendly activities and contribute towards a greener campus.

The system allows students to create accounts, securely log in, manage their profiles, set personal Eco Point goals, track their progress, and participate in campus sustainability activities.

The project is developed as a collaborative team project using Flask, SQLite, HTML, CSS, JavaScript, and Git/GitHub.

---

## 🎯 Project Objective

The main objective of Eco Campus Tracker is to make campus sustainability more engaging by allowing students to record eco-friendly activities and earn Eco Points.

The platform aims to:

- Encourage students to adopt sustainable habits
- Track participation in eco-friendly activities
- Reward students through Eco Points
- Provide challenges and leaderboards
- Allow administrators to manage and monitor activities
- Display useful campus sustainability statistics
- Create a more interactive and engaging green-campus experience

---

## ✨ Features

### 👨‍🎓 Student Module

The Student Module provides the main student-facing functionality.

#### Registration & Login
- Student registration
- Email validation
- Password strength validation
- Secure password hashing
- Student login
- Login session management
- Automatic session timeout
- Failed login attempt protection
- Temporary account lock after repeated failed attempts
- Remember email option
- Password visibility toggle
- Logout functionality
- Logout confirmation

#### Student Profile
- View student profile
- Display student name, email, and Student ID
- Edit profile information
- Profile input validation
- Change password
- Account status display
- Account deactivation
- Last login tracking

#### Student Dashboard
- Personalized welcome message
- Student ID display
- Eco Points display
- Activity count display
- Pending activity count
- Account overview
- Account status badge
- Dynamic eco motivation messages
- Eco Goal progress
- Modern responsive dashboard interface
- Eco-themed dashboard design
- Responsive mobile layout

#### Eco Goal
- Set a personal Eco Point goal
- Update Eco Point goal
- Validate goal values
- Display current Eco Points
- Display target Eco Points
- Calculate goal progress
- Visual progress bar
- Goal completion message

---

### 🌿 Eco Activities & Eco Points

Students can participate in sustainability-related activities such as:

- 🌳 Tree Planting
- ♻️ Recycling
- 🚲 Cycling / Public Transport
- 💧 Saving Water
- 🚫 Avoiding Plastic
- 🧹 Campus Cleanliness

The activity system is designed to support:

- Activity submission
- Activity status tracking
- Pending activities
- Approved activities
- Rejected activities
- Eco Point allocation
- Prevention of duplicate point awarding

---

### 🏆 Leaderboard & Challenges

The project includes a planned student engagement system consisting of:

#### Leaderboard
- Ranking students based on Eco Points
- Displaying student sustainability performance
- Encouraging healthy participation

#### Challenges
- Sustainability challenges
- Challenge participation
- Challenge management
- Challenge-based student engagement

---

### 🛠️ Admin Module

The Admin Module provides administrative functionality for managing the sustainability platform.

Planned administrative features include:

- Admin login
- Admin authentication
- Protected admin pages
- Admin dashboard
- Student management
- Student search and filtering
- Activity search and filtering
- Activity approval
- Activity rejection
- Student status management
- Automatic Eco Point awarding after approval
- Duplicate point prevention
- Challenge management
- Challenge creation, editing, and deletion
- Student and activity statistics
- Dashboard charts
- Top student statistics
- Validation and error handling

---

## 🔄 System Workflow

The overall system follows this basic workflow:

```text
Student Registration
        ↓
Student Login
        ↓
Student Dashboard
        ↓
Participate in Eco Activity
        ↓
Activity Submitted
        ↓
Pending Approval
        ↓
Admin Reviews Activity
        ↓
 ┌───────────────┐
 │               │
Approve        Reject
 │               │
 ↓               ↓
Eco Points      No Points
Awarded
 │
 ↓
Student Dashboard Updated
 │
 ↓
Leaderboard & Statistics Updated
