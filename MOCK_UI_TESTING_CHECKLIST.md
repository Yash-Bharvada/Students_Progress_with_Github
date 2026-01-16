# Mock UI Testing Checklist

This document provides a comprehensive testing checklist for the Mock UI Testing Interface. Use this to verify all functionality works correctly before marking the implementation as complete.

## Prerequisites

Before starting testing:
- [ ] Backend server is running (default: http://localhost:8000)
- [ ] Backend has GitHub OAuth configured
- [ ] You have access to GitHub accounts for testing (mentor and student roles)
- [ ] Browser console is open for debugging (F12)

## Test Environment Setup

### Browser Testing
Test in the following browsers:
- [ ] Chrome/Edge (Chromium-based)
- [ ] Firefox
- [ ] Safari (if available)

### Backend Configuration
- [ ] Backend URL is correctly set in the UI
- [ ] Health check passes successfully
- [ ] Backend responds to /auth/me endpoint

---

## 1. Configuration and Setup Testing

### Backend URL Configuration
- [ ] Default URL (http://localhost:8000) loads correctly
- [ ] Can update backend URL to a different value
- [ ] Updated URL persists after page reload
- [ ] Invalid URL format shows error message
- [ ] Health check button works and shows backend status

**Test Steps:**
1. Open mock-ui.html in browser
2. Verify default URL is displayed
3. Change URL to http://localhost:8001 and click Update
4. Reload page and verify URL persists
5. Try invalid URL (e.g., "not-a-url") and verify error
6. Click Health Check and verify response

---

## 2. GitHub OAuth Authentication Testing

### OAuth Login Flow (Mentor)
- [ ] "Login with GitHub" button redirects to GitHub OAuth
- [ ] After GitHub authorization, redirects back to mock UI
- [ ] JWT token is extracted from callback
- [ ] Token is stored in localStorage
- [ ] User profile is fetched from /auth/me
- [ ] User information displays correctly (username, role, email, GitHub ID)
- [ ] Token displays in "Current Token" textarea
- [ ] Role badge shows "MENTOR"
- [ ] Mentor-only sections become visible

**Test Steps:**
1. Click "Login with GitHub"
2. Authorize the application on GitHub
3. Verify redirect back to mock UI
4. Check that user info displays correctly
5. Verify token is shown in textarea
6. Check localStorage for 'auth_token' and 'current_user'
7. Verify mentor sections are visible

### OAuth Login Flow (Student)
- [ ] Student must be enrolled by mentor first
- [ ] "Login with GitHub" works for enrolled student
- [ ] Student role is correctly assigned
- [ ] Student-only sections become visible
- [ ] Mentor-only sections are hidden

**Test Steps:**
1. First, login as mentor and enroll a student
2. Logout
3. Login with the enrolled student's GitHub account
4. Verify student role and sections

### OAuth Callback Handling
- [ ] Token parameter in URL is extracted correctly
- [ ] Error parameter in URL shows error message
- [ ] URL is cleaned up after callback (no token in URL bar)
- [ ] Return URL is restored after OAuth

**Test Steps:**
1. Manually test callback by visiting: mock-ui.html?token=fake_token
2. Verify error handling: mock-ui.html?error=access_denied
3. Check that URL is cleaned after processing

---

## 3. Manual Token Entry Testing

### Token Input and Validation
- [ ] Can paste JWT token into manual token textarea
- [ ] "Use Token" button validates token format
- [ ] Invalid token format shows error (not 3 parts)
- [ ] Valid token is stored in localStorage
- [ ] Token validation calls /auth/me endpoint
- [ ] User profile is fetched and displayed
- [ ] Manual token input clears after successful use

**Test Steps:**
1. Get a valid JWT token from backend
2. Paste into "Paste JWT Token" textarea
3. Click "Use Token"
4. Verify user profile loads
5. Try invalid token (e.g., "not.a.token") and verify error
6. Try empty token and verify error

---

## 4. Token Management Testing

### Token Display and Copy
- [ ] Current token displays in readonly textarea
- [ ] "Copy Token" button copies token to clipboard
- [ ] Visual feedback shows "Token copied to clipboard!"
- [ ] Token updates when authentication state changes

**Test Steps:**
1. Login and verify token displays
2. Click "Copy Token"
3. Verify clipboard contains token (paste elsewhere)
4. Verify visual feedback appears

### Token Expiration Warnings
- [ ] Token expiration is decoded from JWT
- [ ] Warning shows when token expires within 5 minutes
- [ ] Warning shows when token has already expired
- [ ] Warning message includes time remaining
- [ ] No warning for valid tokens with >5 minutes remaining
- [ ] Automatic monitoring checks every 10 seconds

**Test Steps:**
1. Use a token that expires soon (if available)
2. Verify warning appears
3. Use a fresh token and verify no warning
4. Wait and observe automatic monitoring

---

## 5. Logout Testing

### Logout Functionality
- [ ] "Logout" button shows confirmation dialog
- [ ] Clicking "OK" clears JWT token from localStorage
- [ ] Clicking "OK" clears current user from localStorage
- [ ] UI updates to logged-out state
- [ ] User info section hides
- [ ] Token display section hides
- [ ] Role-based sections hide
- [ ] Auth status shows "Not logged in"

**Test Steps:**
1. Login as any user
2. Click "Logout"
3. Confirm in dialog
4. Verify all state is cleared
5. Check localStorage (should not have auth_token or current_user)
6. Verify UI shows logged-out state

---

## 6. Student Enrollment Testing (Mentor Only)

### Enroll Student
- [ ] Section is visible only for mentors
- [ ] Can enter GitHub username and email
- [ ] "Enroll Student" button validates required fields
- [ ] Empty username shows error
- [ ] Empty email shows error
- [ ] Invalid email format shows error
- [ ] Valid enrollment creates student in backend
- [ ] Success message shows student information
- [ ] Form fields clear after successful enrollment
- [ ] Enrolled students list updates automatically

**Test Steps:**
1. Login as mentor
2. Enter username: "test_student1"
3. Enter email: "test1@example.com"
4. Click "Enroll Student"
5. Verify success message
6. Verify form clears
7. Verify student appears in enrolled list
8. Try empty fields and verify errors
9. Try invalid email (e.g., "not-an-email") and verify error

### Enrolled Students List
- [ ] "Refresh List" button fetches students from backend
- [ ] List shows all students enrolled by current mentor
- [ ] Each student shows: username, GitHub ID, email
- [ ] Each student shows "Can login via GitHub OAuth" status
- [ ] Empty state shows "No students enrolled yet"
- [ ] List updates after enrolling new student

**Test Steps:**
1. Click "Refresh List"
2. Verify students display correctly
3. Enroll a new student
4. Verify list updates automatically
5. Logout and login as different mentor
6. Verify only their enrolled students show

### GraphQL Query Editor
- [ ] "Show/Edit enrollStudent Mutation" button works
- [ ] Query editor displays with current mutation
- [ ] Can edit the mutation text
- [ ] "Reset to Default" restores original mutation
- [ ] "Hide Query" button hides the editor
- [ ] Edited query is used when enrolling student

**Test Steps:**
1. Click "Show/Edit enrollStudent Mutation"
2. Verify mutation displays
3. Edit the mutation (add/remove fields)
4. Enroll a student and verify edited query is used
5. Click "Reset to Default"
6. Verify original mutation is restored

---

## 7. Repository Management Testing (Mentor Only)

### Create Repository
- [ ] Section is visible only for mentors
- [ ] Can enter repository name and URL
- [ ] "Create Repository" button validates required fields
- [ ] Empty name shows error
- [ ] Empty URL shows error
- [ ] Invalid URL format shows error (must start with http:// or https://)
- [ ] Valid creation creates repository in backend
- [ ] Success message shows repository ID
- [ ] Form fields clear after successful creation

**Test Steps:**
1. Login as mentor
2. Enter name: "test-repo"
3. Enter URL: "https://github.com/user/test-repo"
4. Click "Create Repository"
5. Verify success message with repository ID
6. Save the repository ID for later tests
7. Try empty fields and verify errors
8. Try invalid URL (e.g., "not-a-url") and verify error

### GraphQL Query Editor
- [ ] "Show/Edit createRepository Mutation" button works
- [ ] Can edit and use custom mutation
- [ ] Reset to default works

**Test Steps:**
1. Click "Show/Edit createRepository Mutation"
2. Edit the mutation
3. Create a repository with edited mutation
4. Reset to default

---

## 8. GraphQL Queries Testing

### Get My Profile
- [ ] "Get My Profile" button executes getMe query
- [ ] Response shows user profile information
- [ ] All fields display correctly (id, username, email, role, etc.)
- [ ] Works for both mentor and student roles

**Test Steps:**
1. Login as mentor
2. Click "Get My Profile"
3. Verify response shows mentor profile
4. Logout and login as student
5. Click "Get My Profile"
6. Verify response shows student profile

### Get Repositories
- [ ] "Get Repositories" button executes getRepositories query
- [ ] Response shows list of all repositories
- [ ] Each repository shows: id, name, url, createdBy, createdAt
- [ ] Works for both mentor and student roles

**Test Steps:**
1. Login as any user
2. Click "Get Repositories"
3. Verify response shows repository list
4. Verify repository IDs match those created earlier

### Get My Metrics (Student Only)
- [ ] Button is visible for students
- [ ] Executes getMyContributionMetrics query
- [ ] Response shows student's contribution metrics
- [ ] Shows all metrics fields correctly

**Test Steps:**
1. Login as student
2. First save some metrics (see section 9)
3. Click "Get My Metrics"
4. Verify response shows saved metrics

### Get My AI Feedback
- [ ] Button works for all authenticated users
- [ ] Executes getMyAIFeedback query
- [ ] Response shows AI feedback list
- [ ] Shows quality score, strengths, issues, suggestions

**Test Steps:**
1. Login as any user
2. First generate some feedback (see section 10)
3. Click "Get My AI Feedback"
4. Verify response shows feedback

### Get All Metrics for Repo (Mentor Only)
- [ ] Section is visible only for mentors
- [ ] Can enter repository ID
- [ ] "Get All Metrics for Repo" button validates repo ID
- [ ] Empty repo ID shows error
- [ ] Valid query returns all student metrics for that repository
- [ ] Response shows metrics for all students

**Test Steps:**
1. Login as mentor
2. Enter a valid repository ID
3. Click "Get All Metrics for Repo"
4. Verify response shows all student metrics
5. Try empty repo ID and verify error

### GraphQL Query Editors
- [ ] All query editor buttons work
- [ ] Can edit each query independently
- [ ] Reset to default works for each query
- [ ] Edited queries are used when executing

**Test Steps:**
1. Test each "Show/Edit Query" button
2. Edit a query and execute it
3. Verify edited query is used
4. Reset and verify default is restored

---

## 9. Contribution Metrics Testing (Student Only)

### Save Metrics
- [ ] Section is visible only for students
- [ ] Can enter all required fields (repo ID, commits, PRs, issues, consistency)
- [ ] "Save Metrics" button validates all fields
- [ ] Empty fields show appropriate errors
- [ ] Invalid numeric values show errors
- [ ] Consistency score must be between 0.0 and 1.0
- [ ] Negative numbers show errors
- [ ] Valid metrics are saved to backend
- [ ] Success message shows saved metrics
- [ ] Form fields clear after successful save

**Test Steps:**
1. Login as student
2. Enter repository ID (from mentor's created repo)
3. Enter commits: 50
4. Enter PRs: 10
5. Enter issues: 5
6. Enter consistency: 0.85
7. Click "Save Metrics"
8. Verify success message
9. Verify form clears
10. Try invalid values:
    - Empty fields
    - Negative numbers
    - Consistency > 1.0
    - Consistency < 0.0
    - Non-numeric values

### GraphQL Query Editor
- [ ] "Show/Edit saveContributionMetrics Mutation" works
- [ ] Can edit and use custom mutation
- [ ] Reset to default works

**Test Steps:**
1. Click "Show/Edit saveContributionMetrics Mutation"
2. Edit the mutation
3. Save metrics with edited mutation
4. Reset to default

---

## 10. AI Feedback Generation Testing

### Generate Feedback (Student)
- [ ] Student can generate feedback for themselves
- [ ] Can enter repository ID
- [ ] Student GitHub ID field can be left empty
- [ ] "Generate AI Feedback" button validates repo ID
- [ ] Empty repo ID shows error
- [ ] Valid generation creates feedback in backend
- [ ] Success message shows quality score, strengths, issues, suggestions
- [ ] Form fields clear after successful generation

**Test Steps:**
1. Login as student
2. Enter repository ID
3. Leave Student GitHub ID empty
4. Click "Generate AI Feedback"
5. Verify success message with feedback details
6. Try empty repo ID and verify error

### Generate Feedback (Mentor)
- [ ] Mentor must specify student GitHub ID
- [ ] Empty student GitHub ID shows error for mentors
- [ ] Valid generation creates feedback for specified student
- [ ] Success message shows feedback details

**Test Steps:**
1. Login as mentor
2. Enter repository ID
3. Leave Student GitHub ID empty
4. Click "Generate AI Feedback"
5. Verify error about required student GitHub ID
6. Enter a student's GitHub ID
7. Click "Generate AI Feedback"
8. Verify success message

### GraphQL Query Editor
- [ ] "Show/Edit generateAIFeedback Mutation" works
- [ ] Can edit and use custom mutation
- [ ] Reset to default works

**Test Steps:**
1. Click "Show/Edit generateAIFeedback Mutation"
2. Edit the mutation
3. Generate feedback with edited mutation
4. Reset to default

---

## 11. Candidate Search Testing

### Find Candidates
- [ ] Available to all authenticated users
- [ ] Can enter job description in textarea
- [ ] "Find Candidates" button validates job description
- [ ] Empty job description shows error
- [ ] Valid search returns matching candidates
- [ ] Response shows: username, email, match score, verified skills
- [ ] Match scores are between 0.0 and 1.0
- [ ] Results are sorted by match score (highest first)
- [ ] "No candidates found" message when no matches

**Test Steps:**
1. Login as any user
2. Enter job description:
   ```
   Looking for a Python developer with FastAPI experience, 
   strong database skills (PostgreSQL, MongoDB), and knowledge 
   of GraphQL. Must have experience with REST APIs and 
   authentication systems.
   ```
3. Click "Find Candidates"
4. Verify response shows candidates
5. Verify match scores and skills
6. Try empty job description and verify error
7. Try very specific requirements and verify "No candidates found"

### GraphQL Query Editor
- [ ] "Show/Edit findCandidates Query" works
- [ ] Can edit and use custom query
- [ ] Reset to default works

**Test Steps:**
1. Click "Show/Edit findCandidates Query"
2. Edit the query
3. Search with edited query
4. Reset to default

---

## 12. Response Display Testing

### Response Formatting
- [ ] All successful operations show green text
- [ ] All error operations show red text
- [ ] JSON responses are properly indented (2 spaces)
- [ ] Long responses are scrollable
- [ ] "Clear Results" button clears the response area
- [ ] Default message shows when no operations executed

**Test Steps:**
1. Execute any successful operation
2. Verify green text and proper JSON formatting
3. Execute an operation that fails (e.g., invalid token)
4. Verify red text and error message
5. Click "Clear Results"
6. Verify default message appears

### Loading States
- [ ] Loading spinner shows during API calls
- [ ] Loading message updates based on operation
- [ ] Loading spinner hides when operation completes
- [ ] Loading spinner hides on error

**Test Steps:**
1. Execute any operation
2. Observe loading spinner appears
3. Verify loading message is appropriate
4. Verify spinner disappears when complete

---

## 13. Role-Based Access Control Testing

### Mentor Role
- [ ] Student Enrollment section is visible
- [ ] Repository Management section is visible
- [ ] Contribution Metrics section is hidden
- [ ] Mentor Queries section is visible
- [ ] Can access all mentor-only features

**Test Steps:**
1. Login as mentor
2. Verify visible sections
3. Try to use all mentor features
4. Verify all work correctly

### Student Role
- [ ] Student Enrollment section is hidden
- [ ] Repository Management section is hidden
- [ ] Contribution Metrics section is visible
- [ ] Mentor Queries section is hidden
- [ ] Can access all student-only features

**Test Steps:**
1. Login as student
2. Verify visible sections
3. Try to use all student features
4. Verify all work correctly

### Not Logged In
- [ ] All role-specific sections are hidden
- [ ] Only authentication section is accessible
- [ ] GraphQL queries section is visible but operations require auth

**Test Steps:**
1. Logout or open fresh page
2. Verify all role sections are hidden
3. Try to execute a query without auth
4. Verify error about authentication

---

## 14. Error Handling Testing

### Network Errors
- [ ] Backend offline shows appropriate error
- [ ] Timeout shows appropriate error
- [ ] Connection refused shows appropriate error

**Test Steps:**
1. Stop the backend server
2. Try any operation
3. Verify error message about backend connection
4. Start backend and verify operations work again

### Authentication Errors
- [ ] Invalid token shows 401 error
- [ ] Expired token shows appropriate error
- [ ] Missing token shows authentication required error

**Test Steps:**
1. Use an invalid token
2. Try any authenticated operation
3. Verify 401 error
4. Logout and try operation
5. Verify authentication required error

### Validation Errors
- [ ] Empty required fields show validation errors
- [ ] Invalid formats show validation errors
- [ ] Out-of-range values show validation errors

**Test Steps:**
1. Try each form with empty fields
2. Try invalid formats (email, URL, numbers)
3. Try out-of-range values (consistency score)
4. Verify all show appropriate errors

### GraphQL Errors
- [ ] GraphQL syntax errors show in response
- [ ] GraphQL validation errors show in response
- [ ] GraphQL execution errors show in response

**Test Steps:**
1. Edit a query to have syntax error
2. Execute and verify error message
3. Edit a query to request non-existent field
4. Execute and verify error message

---

## 15. Help Documentation Testing

### Help Sections
- [ ] All sections have help documentation
- [ ] Help sections are collapsible
- [ ] Click header to expand/collapse
- [ ] Toggle icon changes (+ / −)
- [ ] Help content is clear and accurate
- [ ] Examples are provided
- [ ] Step-by-step instructions are clear

**Test Steps:**
1. Go through each section
2. Click help header to expand
3. Read through documentation
4. Verify examples are accurate
5. Click header again to collapse
6. Verify toggle icon changes

### Quick Start Guide
- [ ] Quick Start section is visible at top
- [ ] Provides overview of testing workflow
- [ ] Explains role-based access
- [ ] Gives helpful tips

**Test Steps:**
1. Read Quick Start guide
2. Verify information is accurate
3. Follow the workflow described
4. Verify it works as documented

---

## 16. LocalStorage Persistence Testing

### Data Persistence
- [ ] JWT token persists across page reloads
- [ ] Current user persists across page reloads
- [ ] Backend URL persists across page reloads
- [ ] Custom queries persist in memory (not localStorage)

**Test Steps:**
1. Login and verify token is stored
2. Reload page
3. Verify still logged in
4. Change backend URL
5. Reload page
6. Verify URL persists
7. Edit a query
8. Reload page
9. Verify query resets to default (not persisted)

### Storage Cleanup
- [ ] Logout clears auth_token
- [ ] Logout clears current_user
- [ ] Backend URL is not cleared on logout

**Test Steps:**
1. Login
2. Check localStorage (should have auth_token and current_user)
3. Logout
4. Check localStorage (should not have auth_token or current_user)
5. Verify backend URL still in localStorage

---

## 17. Complete Workflow Testing

### Mentor Workflow
- [ ] Login as mentor via GitHub OAuth
- [ ] Enroll a student
- [ ] Create a repository
- [ ] View all repositories
- [ ] Wait for student to save metrics
- [ ] View all metrics for repository
- [ ] Generate AI feedback for student
- [ ] View AI feedback
- [ ] Search for candidates
- [ ] Logout

**Test Steps:**
1. Follow the complete mentor workflow
2. Verify each step works
3. Verify data flows correctly between steps

### Student Workflow
- [ ] Get enrolled by mentor (prerequisite)
- [ ] Login as student via GitHub OAuth
- [ ] View my profile
- [ ] View repositories
- [ ] Save contribution metrics
- [ ] View my metrics
- [ ] Generate AI feedback for myself
- [ ] View my AI feedback
- [ ] Search for candidates
- [ ] Logout

**Test Steps:**
1. Follow the complete student workflow
2. Verify each step works
3. Verify data flows correctly between steps

---

## 18. Browser Compatibility Testing

### Chrome/Edge Testing
- [ ] All features work in Chrome
- [ ] UI renders correctly
- [ ] No console errors
- [ ] OAuth flow works
- [ ] LocalStorage works

### Firefox Testing
- [ ] All features work in Firefox
- [ ] UI renders correctly
- [ ] No console errors
- [ ] OAuth flow works
- [ ] LocalStorage works

### Safari Testing (if available)
- [ ] All features work in Safari
- [ ] UI renders correctly
- [ ] No console errors
- [ ] OAuth flow works
- [ ] LocalStorage works

**Test Steps:**
1. Open mock-ui.html in each browser
2. Run through key workflows
3. Check console for errors
4. Verify UI looks correct
5. Test OAuth flow
6. Test LocalStorage persistence

---

## 19. Responsive Design Testing

### Desktop (1200px+)
- [ ] Layout is centered
- [ ] All sections are readable
- [ ] Buttons are properly sized
- [ ] Forms are well-spaced

### Tablet (800px - 1200px)
- [ ] Layout adjusts appropriately
- [ ] All content is accessible
- [ ] No horizontal scrolling

### Mobile (600px - 800px)
- [ ] Layout stacks vertically
- [ ] All content is readable
- [ ] Forms are usable
- [ ] Buttons are tappable

**Test Steps:**
1. Resize browser window to different widths
2. Verify layout adjusts appropriately
3. Test all features at different sizes
4. Use browser dev tools responsive mode

---

## 20. Security Testing

### Token Security
- [ ] Token is stored in localStorage (not sessionStorage)
- [ ] Token is included in Authorization header
- [ ] Token is not exposed in URL after OAuth
- [ ] Token expiration is checked

### Input Validation
- [ ] All user inputs are validated
- [ ] XSS attempts are prevented (browser handles this)
- [ ] SQL injection is not applicable (GraphQL)

**Test Steps:**
1. Inspect localStorage and verify token storage
2. Use browser network tab to verify Authorization header
3. Check URL after OAuth (should not contain token)
4. Try XSS payloads in text fields (e.g., `<script>alert('xss')</script>`)
5. Verify they are treated as plain text

---

## Test Summary

### Critical Issues Found
List any critical issues that prevent core functionality:
- 

### Non-Critical Issues Found
List any minor issues or improvements:
- 

### Browser-Specific Issues
List any issues specific to certain browsers:
- 

### Recommendations
List any recommendations for improvements:
- 

---

## Sign-Off

- [ ] All critical tests passed
- [ ] All major workflows tested
- [ ] Documentation is accurate
- [ ] Ready for production use

**Tested By:** _______________
**Date:** _______________
**Browsers Tested:** _______________
**Backend Version:** _______________

