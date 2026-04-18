## Description
- **Task:** (e.g., Task 1: Input Sanitization)
- **Changes:** Added check for null/empty strings in `auth.js`.

## Purpose
To prevent the application from crashing when receiving unexpected input from the client.

## Testing Performed
- [ ] Ran `npm test` and all tests passed.
- [ ] Added a new test case for empty passwords in `tests/auth.test.js`.
- [ ] Manually verified with `node src/index.js`.

## Screenshots / Logs
```text
All tests passed!
