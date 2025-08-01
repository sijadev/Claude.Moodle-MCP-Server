# MoodleClaude Pull Request

## 📋 Description
<!-- Provide a clear and concise description of your changes -->

**Type of Change:**
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation (changes to documentation only)
- [ ] 🧹 Code cleanup (refactoring, formatting, etc.)
- [ ] 🧪 Tests (adding or updating tests)
- [ ] 🔧 Chore (dependency updates, build changes, etc.)

## 🔗 Related Issues
<!-- Link to related issues -->
Closes #(issue_number)
Related to #(issue_number)

## 🧪 Testing
<!-- Describe how you tested your changes -->

### Test Environment
- [ ] Local development environment
- [ ] Docker test suite
- [ ] Integration tests
- [ ] Manual testing with Claude Desktop

### Test Results
- [ ] All existing tests pass
- [ ] New tests added and passing
- [ ] Bug fix validation tests pass
- [ ] Integration tests pass

**Test Commands Used:**
```bash
# Add the commands you used for testing
python tools/run_docker_test_suite_fixed.py
python setup_moodleclaude_v3_fixed.py --validate-only
```

## 🐛 Bug Fix Validation
<!-- If this is a bug fix, complete this section -->

- [ ] This PR addresses a known bug from BUGFIX_DOCUMENTATION.md
- [ ] Bug fix has been tested and verified
- [ ] Regression tests added to prevent future occurrences
- [ ] Documentation updated to reflect the fix

**Bug Fix Details:**
- **Issue:** <!-- Describe the bug -->
- **Root Cause:** <!-- What caused the issue -->
- **Solution:** <!-- How you fixed it -->
- **Validation:** <!-- How you tested the fix -->

## 📱 MCP Server Changes
<!-- If your changes affect the MCP server, complete this section -->

- [ ] MCP server functionality tested with Claude Desktop
- [ ] Token permissions validated
- [ ] Course creation tested (if applicable)
- [ ] Connection stability verified

**MCP Server Test Results:**
```
✅ Server starts successfully
✅ Claude Desktop connects
✅ All tools function correctly
✅ No connection drops during testing
```

## 🐳 Docker Changes
<!-- If your changes affect Docker setup, complete this section -->

- [ ] Docker images build successfully
- [ ] Docker test suite passes
- [ ] Environment variables properly configured
- [ ] Container networking works correctly

## 📚 Documentation
<!-- Documentation changes -->

- [ ] Code changes are documented
- [ ] BUGFIX_DOCUMENTATION.md updated (if applicable)
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Examples updated (if applicable)

## ⚡ Performance Impact
<!-- Assess performance impact of your changes -->

- [ ] No performance impact
- [ ] Minor performance improvement
- [ ] Significant performance improvement
- [ ] Potential performance concerns (explain below)

**Performance Notes:**
<!-- If there are performance implications, describe them -->

## 🔒 Security Considerations
<!-- Security implications of your changes -->

- [ ] No security implications
- [ ] Security improvements included
- [ ] Potential security concerns (explain below)
- [ ] Secrets/tokens handled securely

## 🔄 Migration Requirements
<!-- If this change requires migration steps -->

- [ ] No migration required
- [ ] Automatic migration included
- [ ] Manual migration steps documented below

**Migration Steps:**
```bash
# If manual steps are required, list them here
```

## 📋 Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] No debugging code left in
- [ ] No TODO comments without issues

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Edge cases considered and tested

### Compatibility
- [ ] Changes are backward compatible
- [ ] Python version compatibility maintained
- [ ] Moodle version compatibility maintained
- [ ] Claude Desktop compatibility verified

### Bug Fixes (if applicable)
- [ ] Bug fix addresses root cause
- [ ] Bug fix validated with original reproduction steps
- [ ] Regression tests added
- [ ] Documentation updated

## 🖼️ Screenshots/Logs
<!-- If applicable, add screenshots or logs to help explain your changes -->

**Before:**
<!-- Screenshots or logs showing the issue -->

**After:**
<!-- Screenshots or logs showing the fix -->

## 📝 Additional Notes
<!-- Any additional information that reviewers should know -->

## 🙋‍♂️ Questions for Reviewers
<!-- Specific questions or areas where you'd like feedback -->

---

## For Maintainers

### Review Checklist
- [ ] PR title follows conventional commit format
- [ ] All automated checks pass
- [ ] Code review completed
- [ ] Manual testing performed
- [ ] Documentation review completed
- [ ] Bug fix validation performed (if applicable)
- [ ] Ready for merge