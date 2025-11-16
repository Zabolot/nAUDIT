# 📋 Testing Instructions - nAUDIT v2.7.1 with Logging

**Created:** 2025-11-15  
**Version:** 2.7.1  
**Focus:** Verify error handling and logging enhancements

---

## 🎯 Test Objective

Verify that nAUDIT v2.7.1 can:
1. ✅ Analyze projects WITH errors (no crashes)
2. ✅ Display all errors in the UI
3. ✅ Log all operations to file
4. ✅ Show GPU optimization level
5. ✅ Provide useful error messages

---

## 🚀 Quick Start Testing

### Step 1: Run Diagnostic (2 min)
```powershell
cd G:\CODING\nAUDIT
python diagnose_v2_7.py
```

**Expected Output:**
```
✅ Logging initialized
✅ GPU Detection working (Optimization Level: MEDIUM)
✅ AuditEngine loaded
✅ Tree Widget loaded
✅ Graph Visualizer loaded
```

### Step 2: Open GUI
```powershell
cd G:\CODING\nAUDIT\dist
.\nAUDIT.exe
```

**Expected:**
- GUI opens without crashes
- Console shows startup messages with [INFO] tags
- Colorized logging output appears

### Step 3: Test with Error Project
1. In GUI, click "Select Project Folder"
2. Navigate to: `G:\CODING\nAUDIT\test_project_with_errors`
3. Click "Analyze" or "Start Audit"
4. **CRITICAL:** Watch for:
   - ✅ No crash during analysis
   - ✅ Errors appear in tree view
   - ✅ No error dialog (should complete successfully)
   - ✅ Status shows number of issues found

### Step 4: Check Logs
```powershell
# View log file location
Get-Item $env:USERPROFILE\.naudit\logs

# View latest log (last 100 lines)
Get-ChildItem $env:USERPROFILE\.naudit\logs -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { Get-Content $_.FullName -Tail 100 }

# View specific errors
Get-Content (Get-ChildItem $env:USERPROFILE\.naudit\logs -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName | Select-String "ERROR"
```

**Expected Log Content:**
```
[2025-11-15 23:15:38] INFO     [main_window_v4:320] Starting audit for: G:\test_project_with_errors
[2025-11-15 23:15:39] DEBUG    [tree_widget:182] Found code_issues: 5 items
[2025-11-15 23:15:39] INFO     [tree_widget:238] Processed code issues: 5
[2025-11-15 23:15:40] INFO     [main_window_v4:340] Audit completed successfully
```

---

## 📊 Expected Test Results

### Test Project: `test_project_with_errors`

**Files:**
- `file_with_syntax_error.py` - 1 error (missing closing paren)
- `file_with_import_errors.py` - 3 errors (unresolved imports)
- `file_with_type_errors.py` - 2 errors (type mismatches)
- `clean_file.py` - 0 errors

**Expected Analysis Result:**
```
Total Code Issues: 6
Total Security Issues: 0
Total Files: 4
Processed Files: 4
Analysis Time: ~2-5 seconds
```

### GUI Display
- Tree view should show:
  - ✅ file_with_syntax_error.py (1 issue)
  - ✅ file_with_import_errors.py (3 issues)
  - ✅ file_with_type_errors.py (2 issues)
  - ✅ clean_file.py (0 issues)

- Status bar should show:
  - ✅ "Analysis completed" (green)
  - ✅ Issues count displayed
  - ✅ No error messages

---

## 🔍 Detailed Test Scenarios

### Scenario 1: Analysis Completion (PASS/FAIL)

**Steps:**
1. Start nAUDIT
2. Select `test_project_with_errors`
3. Click "Analyze"
4. Wait for completion

**Pass Criteria:**
- ✅ No crash
- ✅ No error dialog
- ✅ Tree populated with issues
- ✅ Status shows "Analysis completed"
- ✅ Issue count correct (6 total)

**If FAIL:**
- Check log file for exceptions
- Look for "ERROR" lines in logs
- Report exact error message

---

### Scenario 2: Log File Generation (PASS/FAIL)

**Steps:**
1. Complete analysis from Scenario 1
2. Open log file location:
   ```powershell
   explorer $env:USERPROFILE\.naudit\logs
   ```
3. Open latest log file in text editor
4. Search for "Starting audit"

**Pass Criteria:**
- ✅ Log file exists
- ✅ Contains timestamps: `[2025-11-15 HH:MM:SS]`
- ✅ Contains INFO/DEBUG/ERROR levels
- ✅ Shows analysis start and completion
- ✅ Shows issue processing

**Sample Log Lines:**
```
[2025-11-15 23:15:38] INFO     [run_naudit_gui:35] nAUDIT v2.7 GUI Started
[2025-11-15 23:15:40] DEBUG    [main_window_v4:320] Audit button clicked
[2025-11-15 23:15:41] INFO     [main_window_v4:40] Starting audit for: G:\test_project_with_errors
[2025-11-15 23:15:42] DEBUG    [tree_widget:182] Found code_issues: 6 items
[2025-11-15 23:15:42] INFO     [tree_widget:238] Processing issue #1: SyntaxError...
[2025-11-15 23:15:42] INFO     [main_window_v4:340] Analysis complete: 6 issues found
```

**If FAIL:**
- Check if log directory exists
- Verify permissions on ~/.naudit/logs
- Check Windows Event Viewer for app crashes

---

### Scenario 3: Error Message Recovery (PASS/FAIL)

**Steps:**
1. In file explorer, delete one file from test project
   ```powershell
   Remove-Item G:\CODING\nAUDIT\test_project_with_errors\src\clean_file.py
   ```
2. Select the modified test project in nAUDIT
3. Click "Analyze"
4. Check for proper error handling

**Pass Criteria:**
- ✅ Analysis still completes
- ✅ Remaining files are analyzed (5 instead of 6)
- ✅ No crash even with missing file
- ✅ Log shows what happened

**If FAIL:**
- Program crashes = bug in error handling
- Check logs for exception details

**Restore File:**
```powershell
cd G:\CODING\nAUDIT
python -c "
with open('test_project_with_errors/src/clean_file.py', 'w') as f:
    f.write('# Restored clean file\n')
"
```

---

### Scenario 4: GPU Detection Display (PASS/FAIL)

**Steps:**
1. Run diagnostic tool:
   ```powershell
   python diagnose_v2_7.py
   ```
2. Look for GPU detection section
3. Note the Optimization Level

**Pass Criteria:**
- ✅ Optimization Level shown (HIGH/MEDIUM/LOW)
- ✅ GPU status shown (True/False)
- ✅ CPU cores displayed
- ✅ RAM information shown

**Expected for Your System:**
```
OS: Windows
CPU Cores: 16
Total RAM: 31.8 GB
Available RAM: ~15-20 GB
GPU Available: False
Optimization Level: MEDIUM
```

**If Different:**
- Note the optimization level
- Check if it matches system capabilities
- Report any inconsistencies

---

### Scenario 5: Large Project Analysis (OPTIONAL - 10+ min)

**Steps:**
1. Select a large real project (1000+ files)
2. Click "Analyze"
3. Monitor:
   - GUI responsiveness
   - Memory usage
   - Analysis time
   - Log file growth

**Monitor Commands:**
```powershell
# Watch log file in real-time
Get-Content (Get-ChildItem $env:USERPROFILE\.naudit\logs -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName -Wait

# Check current CPU/Memory (while analyzing)
Get-Process nAUDIT | Select-Object CPU, WorkingSet
```

**Pass Criteria:**
- ✅ Completes without crashing
- ✅ Memory usage stays reasonable
- ✅ Issues displayed correctly
- ✅ Log file updated throughout

---

## ⏱️ Test Timeline

| Step | Time | Task |
|------|------|------|
| Setup | 5 min | Prepare test project, read instructions |
| Test 1 | 2 min | Run diagnostic |
| Test 2 | 5 min | Open GUI and analyze test project |
| Test 3 | 3 min | Check log files |
| Test 4 | 2 min | Verify GPU info |
| Test 5 | 3 min | Document results |
| **Total** | **~20 min** | **All tests** |

---

## 📝 Test Results Template

```
TEST RESULTS - nAUDIT v2.7.1 LOGGING & ERROR HANDLING
=====================================================

Date: [YOUR DATE]
Tester: [YOUR NAME]
System: Windows 10/11, [CPU/RAM]

SCENARIO 1: Analysis Completion
Status: [ ] PASS [ ] FAIL
Notes: ___________________________________

SCENARIO 2: Log File Generation
Status: [ ] PASS [ ] FAIL
Log Location: _____________________________
Log File Size: ______________________________
Sample Errors Found: ________________________

SCENARIO 3: Error Recovery
Status: [ ] PASS [ ] FAIL
Notes: ___________________________________

SCENARIO 4: GPU Detection
Status: [ ] PASS [ ] FAIL
Optimization Level: _________________________
GPU Detected: [ ] YES [ ] NO

SCENARIO 5: Large Project (Optional)
Status: [ ] PASS [ ] FAIL [ ] SKIPPED
Analysis Time: ______________________________
Final Issue Count: ___________________________

OVERALL RESULT: [ ] ALL PASS [ ] SOME FAIL

Issues Found: _______________________________
_____________________________________________

Recommendations: ____________________________
_____________________________________________
```

---

## 🆘 Troubleshooting

### "Program crashed with no error message"
**Solution:**
1. Check log file for stack trace
2. Look for "ERROR" or "CRITICAL" lines
3. Report the exact line from logs

### "No log file created"
**Solution:**
1. Verify directory exists: `$env:USERPROFILE\.naudit\logs`
2. Create manually if missing:
   ```powershell
   mkdir $env:USERPROFILE\.naudit\logs -Force
   ```
3. Run diagnostic again

### "Errors don't appear in tree"
**Solution:**
1. Check log for "populate_from_report" messages
2. Verify issue format is correct
3. Look for exception traces in log

### "GPU shows as unavailable"
**Solution:**
1. This is expected if no GPU
2. Check Optimization Level (should be MEDIUM for good RAM)
3. If should have GPU, check PyTorch installation

---

## ✅ Sign-Off Checklist

- [ ] Diagnostic tool runs successfully
- [ ] GUI starts without crashes
- [ ] Test project analyzes correctly
- [ ] All 6 errors detected
- [ ] Log file contains proper entries
- [ ] GPU level shows correctly
- [ ] Error handling works
- [ ] Ready for production

---

## 📞 Report Issues

If you find problems:

1. **Reproduce** the exact steps
2. **Collect** the log file from `~/.naudit/logs/`
3. **Document**:
   - What you did
   - What happened
   - What you expected
   - Last 50 lines from log file
4. **Report** with all information above

---

**Version:** 2.7.1  
**Status:** Ready for Testing  
**Date:** 2025-11-15
