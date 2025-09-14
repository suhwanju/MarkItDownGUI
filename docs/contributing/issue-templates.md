# Issue Templates

Standardized templates for reporting bugs, requesting features, and other project contributions.

## Table of Contents

- [Bug Report Template](#bug-report-template)
- [Feature Request Template](#feature-request-template)
- [Documentation Issue Template](#documentation-issue-template)
- [Performance Issue Template](#performance-issue-template)
- [Security Issue Template](#security-issue-template)
- [Question Template](#question-template)

## Bug Report Template

Use this template when reporting bugs, errors, or unexpected behavior.

```markdown
---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] Brief description of the issue'
labels: bug, needs-triage
assignees: ''
---

## Bug Description
**Clear and concise description of what the bug is.**

## Steps to Reproduce
**Detailed steps to reproduce the behavior:**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
**Clear and concise description of what you expected to happen.**

## Actual Behavior
**What actually happened instead.**

## Environment Information
**Please complete the following information:**
- **OS**: [e.g. Windows 11, macOS 13.0, Ubuntu 22.04]
- **MarkItDown GUI Version**: [e.g. 1.0.0]
- **Python Version**: [e.g. 3.11.0]
- **Installation Method**: [e.g. pip, standalone executable, from source]

## Sample Files
**If applicable, please provide:**
- [ ] Sample input file(s) that reproduce the issue
- [ ] Expected output
- [ ] Actual output produced

**Note**: Please remove any sensitive or personal information from sample files.

## Screenshots/Videos
**If applicable, add screenshots or videos to help explain the problem.**

## Log Files
**If available, please attach relevant log files or error messages:**
```
Paste log content here or attach log files
```

## Additional Context
**Add any other context, workarounds, or related issues.**

## Checklist
**Please check all that apply:**
- [ ] I have searched existing issues for similar problems
- [ ] I have tested with the latest version
- [ ] I have provided all requested information
- [ ] I have removed sensitive information from attachments
```

## Feature Request Template

Use this template when requesting new features or enhancements.

```markdown
---
name: Feature Request
about: Suggest a new feature or enhancement
title: '[FEATURE] Brief description of the feature'
labels: enhancement, needs-triage
assignees: ''
---

## Feature Summary
**Brief, clear description of the feature you'd like to see added.**

## Problem/Use Case
**Describe the problem this feature would solve or the use case it addresses:**
- What are you trying to accomplish?
- What challenges are you currently facing?
- How would this feature help you or other users?

## Proposed Solution
**Detailed description of how you envision the feature working:**
- How should it behave?
- What should the user interface look like?
- How should it integrate with existing functionality?

## Alternative Solutions
**Describe any alternative approaches you've considered:**
- Other ways to solve the same problem
- Workarounds you're currently using
- Similar features in other applications

## Additional Context
**Any other context, mockups, or examples that would be helpful:**
- Screenshots or mockups of desired functionality
- Examples from other applications
- Links to relevant documentation or specifications

## Impact Assessment
**Please estimate the impact of this feature:**
- **User Benefit**: [High/Medium/Low] - How much would this help users?
- **Usage Frequency**: [High/Medium/Low] - How often would this be used?
- **Implementation Complexity**: [High/Medium/Low/Unknown] - How difficult might this be to implement?

## Acceptance Criteria
**What should be true when this feature is complete?**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Checklist
- [ ] I have searched existing feature requests for similar ideas
- [ ] I have clearly described the problem this feature solves
- [ ] I have provided enough detail for the development team to understand the request
- [ ] I have considered how this fits with existing functionality
```

## Documentation Issue Template

Use this template for issues with documentation, including errors, missing information, or suggestions for improvement.

```markdown
---
name: Documentation Issue
about: Report documentation problems or suggest improvements
title: '[DOCS] Brief description of the documentation issue'
labels: documentation, needs-triage
assignees: ''
---

## Documentation Issue Type
**What type of documentation issue is this?**
- [ ] Error or incorrect information
- [ ] Missing information
- [ ] Unclear or confusing content
- [ ] Outdated information
- [ ] Suggestion for improvement
- [ ] New documentation needed

## Location
**Where is the documentation issue located?**
- **File/Page**: [e.g. user-guide/installation.md, API reference page]
- **Section**: [e.g. "Installation on Windows", "Configuration API"]
- **Line Numbers**: [if applicable]
- **URL**: [if web-based documentation]

## Current Content
**What does the documentation currently say? (copy relevant text)**
```
Current documentation content here
```

## Issue Description
**What's wrong or unclear about the current documentation?**

## Suggested Improvement
**What should the documentation say instead? (if applicable)**
```
Suggested content here
```

## Additional Context
**Any additional context that would help improve the documentation:**
- Your level of experience with the software
- What you were trying to accomplish when you found this issue
- Any external references that might be helpful

## Audience Impact
**Who would benefit from this documentation improvement?**
- [ ] New users
- [ ] Experienced users
- [ ] Developers
- [ ] System administrators
- [ ] All users

## Priority
**How important is this documentation fix?**
- [ ] Critical - Prevents users from completing essential tasks
- [ ] High - Causes significant confusion or inefficiency
- [ ] Medium - Minor improvement that would be helpful
- [ ] Low - Nice to have but not urgent
```

## Performance Issue Template

Use this template for performance-related problems including slow operations, high memory usage, or resource consumption issues.

```markdown
---
name: Performance Issue
about: Report performance problems or resource usage issues
title: '[PERFORMANCE] Brief description of the performance issue'
labels: performance, needs-triage
assignees: ''
---

## Performance Issue Description
**Clear description of the performance problem:**

## Performance Symptoms
**What performance symptoms are you experiencing?**
- [ ] Slow file conversion
- [ ] High CPU usage
- [ ] High memory usage
- [ ] Application freezing/hanging
- [ ] Long startup time
- [ ] Slow UI responsiveness
- [ ] Other: _______________

## Performance Measurements
**If possible, provide specific measurements:**
- **Operation Time**: [e.g. "PDF conversion takes 45 seconds"]
- **Memory Usage**: [e.g. "Uses 2GB RAM for 50MB file"]
- **CPU Usage**: [e.g. "100% CPU usage during conversion"]
- **File Sizes**: [e.g. "Input file: 25MB, Processing time: 2 minutes"]

## Environment Information
- **OS**: [e.g. Windows 11, macOS 13.0, Ubuntu 22.04]
- **MarkItDown GUI Version**: [e.g. 1.0.0]
- **System Specs**: 
  - CPU: [e.g. Intel i7-10700K, Apple M1]
  - RAM: [e.g. 16GB]
  - Storage: [e.g. SSD, HDD]
- **Available System Resources**: [e.g. 8GB free RAM, 50% CPU usage by other apps]

## Reproduction Steps
**Steps to reproduce the performance issue:**
1. Launch application
2. Load specific type/size of file
3. Perform specific operation
4. Observe performance metrics

## Expected Performance
**What performance would you expect for this operation?**

## Sample Files
**If applicable, please provide information about files that exhibit the issue:**
- **File Type**: [e.g. PDF, DOCX]
- **File Size**: [e.g. 25MB]
- **File Characteristics**: [e.g. 100 pages, many images, complex formatting]
- **Sample File Available**: [Yes/No - remove sensitive content]

## Workarounds
**Are there any workarounds you've found that improve performance?**

## System Resource Monitoring
**If you've monitored system resources, please provide details:**
```
Resource usage information here (Task Manager, Activity Monitor, htop output)
```

## Additional Context
**Any other relevant information:**
- Does this happen with all files or specific types?
- Has performance degraded over time?
- Are there specific settings that affect performance?
```

## Security Issue Template

**⚠️ Important**: For critical security vulnerabilities, please report privately to security@markitdown-gui.org instead of creating a public issue.

```markdown
---
name: Security Issue
about: Report non-critical security concerns (use email for critical vulnerabilities)
title: '[SECURITY] Brief description of the security concern'
labels: security, needs-triage
assignees: ''
---

## ⚠️ Security Issue Notice
**Before submitting this issue, please confirm:**
- [ ] This is NOT a critical security vulnerability that could be exploited
- [ ] I understand that critical vulnerabilities should be reported privately to security@markitdown-gui.org
- [ ] This issue involves security best practices, minor concerns, or questions about security features

## Security Concern Type
**What type of security concern is this?**
- [ ] Security best practice suggestion
- [ ] Minor security improvement
- [ ] Security feature request
- [ ] Question about security features
- [ ] Non-critical security observation

## Description
**Clear description of the security concern or suggestion:**

## Potential Impact
**What is the potential security impact?**
- [ ] Information disclosure
- [ ] Unauthorized access
- [ ] Data integrity
- [ ] Privacy concern
- [ ] Other: _______________

**Impact Level**:
- [ ] Low - Minor security improvement
- [ ] Medium - Notable security concern
- [ ] High - Significant security issue (consider private reporting)

## Affected Components
**Which parts of the application are affected?**
- [ ] File processing
- [ ] Configuration system
- [ ] User interface
- [ ] Logging system
- [ ] Network communication
- [ ] File system operations
- [ ] Other: _______________

## Suggested Improvements
**What improvements or changes would address this concern?**

## Environment Information
- **OS**: [e.g. Windows 11, macOS 13.0, Ubuntu 22.04]
- **MarkItDown GUI Version**: [e.g. 1.0.0]
- **Installation Method**: [e.g. pip, standalone executable]
- **User Privileges**: [e.g. standard user, administrator]

## Additional Context
**Any other relevant information about this security concern:**
```

## Question Template

Use this template for general questions about usage, features, or troubleshooting that don't fit other categories.

```markdown
---
name: Question
about: Ask a question about MarkItDown GUI
title: '[QUESTION] Brief description of your question'
labels: question, needs-triage
assignees: ''
---

## Question Category
**What type of question is this?**
- [ ] How to use a specific feature
- [ ] Troubleshooting help
- [ ] Best practices
- [ ] Integration with other tools
- [ ] Configuration question
- [ ] General usage question

## Your Question
**What would you like to know?**

## What You've Tried
**What have you already tried to find the answer?**
- [ ] Searched the documentation
- [ ] Searched existing issues
- [ ] Tried different approaches
- [ ] Asked in community forums

**Specific attempts:**

## Environment Information
**If relevant to your question:**
- **OS**: [e.g. Windows 11, macOS 13.0, Ubuntu 22.04]
- **MarkItDown GUI Version**: [e.g. 1.0.0]
- **Installation Method**: [e.g. pip, standalone executable]

## Use Case
**What are you trying to accomplish? (helps provide better answers)**

## Expected Outcome
**What result are you hoping to achieve?**

## Additional Context
**Any other information that might be relevant to your question:**
```

---

## Issue Guidelines

### Before Creating an Issue

1. **Search First**: Check if your issue already exists
2. **Use Latest Version**: Test with the most recent release
3. **Choose Right Template**: Use the template that best matches your issue type
4. **Provide Complete Information**: Fill out all relevant sections
5. **Remove Sensitive Data**: Never include passwords, personal information, or proprietary content

### Issue Lifecycle

1. **Triage**: Maintainers will review and label your issue
2. **Investigation**: Team or community investigates the issue
3. **Resolution**: Solution is implemented and tested
4. **Closure**: Issue is closed with explanation
5. **Follow-up**: Verify the fix works for your use case

### Contributing to Issue Resolution

- **Provide Additional Information**: If maintainers request more details
- **Test Solutions**: Help test proposed fixes or workarounds  
- **Update Status**: Let us know if your issue changes or is resolved
- **Help Others**: Share your experience with similar issues

---

**Related Documentation:**
- 🤝 [Contributing Guide](contributing.md) - General contribution guidelines
- 🔄 [Development Workflow](workflow.md) - Development process
- 📋 [Code Review Guidelines](code-review.md) - Review standards
- 🚀 [Release Process](release-process.md) - How releases are managed