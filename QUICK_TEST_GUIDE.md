# Quick Test Guide - Mock UI Testing Interface

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Backend server running at http://localhost:8000
- GitHub OAuth configured in backend
- Modern browser (Chrome, Firefox, or Safari)

### Basic Test Flow

1. **Open the Mock UI**
   ```
   Open mock-ui.html in your browser
   ```

2. **Run Automated Tests First**
   ```
   Open test_mock_ui_automated.html in your browser
   Click "Run All Tests"
   Verify all 15 tests pass
   ```

3. **Test Authentication**
   - Click "Login with GitHub"
   - Authorize the application
   - Verify you're logged in
   - Check your role (MENTOR or STUDENT)

4. **Test Core Feature (Based on Role)**
   
   **If MENTOR:**
   - Enroll a student (username: test_student, email: test@example.com)
   - Create a repository (name: test-repo, url: https://github.com/user/test-repo)
   - Copy the repository ID from the response
   
   **If STUDENT:**
   - Save contribution metrics (use repo ID from mentor)
   - Generate AI feedback for yourself

5. **Test Logout**
   - Click "Logout"
   - Verify you're logged out
   - Verify localStorage is cleared

## ✅ Essential Tests (15 Minutes)

### 1. Configuration (2 min)
- [ ] Health check passes
- [ ] Can change backend URL
- [ ] URL persists after reload

### 2. Authentication (3 min)
- [ ] GitHub OAuth login works
- [ ] User info displays correctly
- [ ] Token is shown
- [ ] Manual token entry works

### 3. Mentor Features (5 min)
- [ ] Can enroll a student
- [ ] Can create a repository
- [ ] Can view all metrics for a repo
- [ ] Enrolled students list updates

### 4. Student Features (3 min)
- [ ] Can save contribution metrics
- [ ] Can view own metrics
- [ ] Can generate AI feedback

### 5. Common Features (2 min)
- [ ] Can search for candidates
- [ ] Can view repositories
- [ ] Can view own profile

## 🔍 Detailed Testing (1 Hour)

Follow the comprehensive checklist in `MOCK_UI_TESTING_CHECKLIST.md`

## 🐛 Common Issues and Solutions

### Issue: "Backend connection failed"
**Solution:** 
- Verify backend is running: `curl http://localhost:8000/health`
- Check backend URL in mock UI configuration
- Check browser console for CORS errors

### Issue: "OAuth authentication failed"
**Solution:**
- Verify GitHub OAuth is configured in backend
- Check callback URL matches your setup
- Verify GitHub App is active

### Issue: "Token validation failed"
**Solution:**
- Token may be expired - login again
- Token format may be invalid - check it has 3 parts
- Backend /auth/me endpoint may be down

### Issue: "Student cannot login"
**Solution:**
- Student must be enrolled by a mentor first
- Verify student's GitHub username matches enrollment
- Check student's GitHub account is accessible

### Issue: "Query not supported by backend"
**Solution:**
- Some queries (like getEnrolledStudents) may not be implemented
- Check backend GraphQL schema
- Feature may be optional

## 📊 Test Results Template

```
Date: _______________
Tester: _______________
Backend Version: _______________
Browser: _______________

Automated Tests: ___/15 passed
Manual Tests: ___/200 passed

Critical Issues: ___
High Priority Issues: ___
Medium Priority Issues: ___
Low Priority Issues: ___

Overall Status: [ ] PASS [ ] FAIL

Notes:
_________________________________
_________________________________
_________________________________
```

## 🎯 Success Criteria

### Minimum Requirements (Must Pass)
- ✅ Automated tests: 15/15 pass
- ✅ Authentication works (OAuth and manual token)
- ✅ Mentor workflow completes
- ✅ Student workflow completes
- ✅ Role-based access works
- ✅ Error handling works

### Recommended (Should Pass)
- ✅ All GraphQL queries work
- ✅ All mutations work
- ✅ Help documentation is accurate
- ✅ Works in Chrome and Firefox
- ✅ Responsive design works

### Optional (Nice to Have)
- ✅ Works in Safari
- ✅ Token expiration warnings work
- ✅ Query editors work
- ✅ All edge cases handled

## 📝 Quick Commands

### Start Backend (Example)
```bash
cd backend
python -m uvicorn main:app --reload
```

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### View Browser Console
```
Press F12 in browser
Go to Console tab
Look for errors or warnings
```

### Clear Browser Data
```
Press F12 in browser
Go to Application tab (Chrome) or Storage tab (Firefox)
Clear localStorage
Reload page
```

## 🔗 Related Documents

- **Comprehensive Checklist:** `MOCK_UI_TESTING_CHECKLIST.md` (200+ test cases)
- **Automated Tests:** `test_mock_ui_automated.html` (15 automated tests)
- **Testing Summary:** `MOCK_UI_TESTING_SUMMARY.md` (overview and status)
- **Requirements:** `.kiro/specs/mock-ui-testing/requirements.md`
- **Design:** `.kiro/specs/mock-ui-testing/design.md`
- **Tasks:** `.kiro/specs/mock-ui-testing/tasks.md`

## 💡 Tips

1. **Use Browser Console:** Keep it open to see errors and debug issues
2. **Test Incrementally:** Don't try to test everything at once
3. **Document Issues:** Write down any problems you find
4. **Test Both Roles:** Make sure to test as both mentor and student
5. **Test Error Cases:** Don't just test happy paths
6. **Check LocalStorage:** Verify data persists correctly
7. **Test Logout:** Always verify logout clears everything
8. **Use Real Data:** Test with realistic usernames, emails, and values

## 🎓 Testing Best Practices

1. **Start Fresh:** Clear browser cache and localStorage before testing
2. **Test Systematically:** Follow the checklist in order
3. **Document Everything:** Write down what you test and the results
4. **Test Edge Cases:** Try empty fields, invalid data, etc.
5. **Test Error Recovery:** Verify the UI recovers from errors
6. **Test Persistence:** Reload the page and verify state persists
7. **Test Cross-Browser:** Don't assume it works everywhere
8. **Test Responsive:** Try different screen sizes

## ⏱️ Time Estimates

- **Quick Smoke Test:** 5 minutes
- **Essential Tests:** 15 minutes
- **Comprehensive Manual Tests:** 1-2 hours
- **Cross-Browser Testing:** 30 minutes per browser
- **Complete Workflow Testing:** 30 minutes
- **Total Recommended Testing Time:** 3-4 hours

## 📞 Support

If you encounter issues during testing:

1. Check the browser console for errors
2. Review the error handling section in the design document
3. Verify backend is running and accessible
4. Check the common issues section above
5. Review the requirements and design documents
6. Document the issue for later resolution

---

**Remember:** The goal is to verify that all features work correctly and the UI is ready for use. Take your time and be thorough!
