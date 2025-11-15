# 🧪 nAUDIT v2.7 - Testing Guide

**Версия:** v2.7 (Enhancement Release)  
**Статус:** Ready for Functional Testing  
**Exe Location:** `G:\CODING\nAUDIT\dist\nAUDIT.exe` (268.8 MB)

---

## 📋 Functional Testing Checklist

### ✅ Phase 1: Launch & GPU Detection (5 min)

```bash
cd G:\CODING\nAUDIT\dist
.\nAUDIT.exe
```

**Expected Behavior:**
- [ ] Application launches without errors
- [ ] Main window appears with all GUI elements
- [ ] Console shows GPU detection info (if available)
- [ ] Console shows optimization level (HIGH/MEDIUM/LOW)

**Example Console Output:**
```
[INFO] nAUDIT v2.7 Started
[GPU] GPU Available: True
[GPU] Model: NVIDIA GeForce RTX 3090
[GPU] Memory: 24576 MB
[GPU] Optimization Level: HIGH
```

**What to Check:**
1. Application launches
2. UI responsive
3. No GPU-related errors
4. Optimization level detected

---

### ✅ Phase 2: Error Display in Tree (10 min)

**Test Scenario:** Audit a project and verify errors show in tree view

**Steps:**
1. Click "Select Project Folder"
2. Choose a project with known issues (test project)
3. Click "Start Audit"
4. Wait for analysis to complete
5. Check tree view for errors

**Expected Behavior:**
- [ ] Tree view shows "Code Issues" category
- [ ] Tree view shows "Security Issues" category
- [ ] Error count matches console output
- [ ] Expanding issues shows individual errors
- [ ] Each error has message, file, line number

**Visual Check:**
```
Project Tree
├─ 📁 Controllers
├─ 📁 Models
├─ ⚠️ Code Issues (5)
│  ├─ Unused variable 'x' in auth.py:25
│  ├─ Function too long in models.py:10
│  └─ ...
├─ 🔴 Security Issues (2)
│  ├─ SQL injection in query.py:45
│  └─ ...
```

**What to Check:**
1. Errors appear in tree (not just console)
2. Error count is accurate
3. Tree is interactive (can expand/collapse)
4. Error details are correct

---

### ✅ Phase 3: Hierarchical Clustering (15 min)

**Test Scenario:** Load project with nested folders and verify clustering

**Steps:**
1. Click "Select Project Folder"
2. Choose a project with structure like:
   ```
   src/
   ├─ controllers/
   │  ├─ auth/
   │  │  ├─ login.py
   │  │  └─ register.py
   │  └─ core/
   │     └─ main.py
   ├─ models/
   │  ├─ validators/
   │  │  └─ user.py
   │  └─ core.py
   ```
3. Switch to "PyVis" or "Plotly" tab
4. Observe graph visualization
5. Look for folder clustering

**Expected Behavior - PYVIS Tab:**
- [ ] Nodes grouped by top-level folder (src/)
- [ ] Subfolders clustered (controllers/, models/)
- [ ] Sub-subfolders visible (auth/, core/, validators/)
- [ ] Files organized within subfolder clusters
- [ ] Colors distinguish folder levels
- [ ] Can zoom/pan/interact

**Visual Example:**
```
BEFORE (v2.6 - Flat):
● ● ● ● ● ● ● ● ●
● ● ● ● ● ● ● ● ●
Random positions, no hierarchy

AFTER (v2.7 - Hierarchical):
┌─────────────────┐
│  controllers/   │
│ ┌─────┬─────┐  │
│ │ auth│core │  │
│ │●●●  │● ● │  │
│ └─────┴─────┘  │
└─────────────────┘
Organized by folder levels
```

**What to Check:**
1. Nodes are visually clustered by folder
2. Folder structure is clear
3. Subfolder organization works
4. Layout is readable (not overcrowded)

---

### ✅ Phase 4: Performance Test (15 min)

**Test Scenario 1: Small Project (100-500 files)**
- [ ] Graph renders in < 5 seconds
- [ ] No UI freezing
- [ ] Zoom/pan responsive
- [ ] Colors visible

**Test Scenario 2: Medium Project (500-2000 files)**
- [ ] Graph renders in < 10 seconds
- [ ] Animations smooth (if enabled)
- [ ] Memory usage reasonable (< 2GB)
- [ ] No crashes

**Test Scenario 3: Large Project (2000+ files)**
- [ ] Graph renders in < 30 seconds
- [ ] System remains responsive
- [ ] Memory usage monitored
- [ ] No crashes or hangs

**Performance Metrics (Track These):**
```
Small Project (500 files):
├─ v2.6: 8-12 seconds
├─ v2.7 (HIGH): 3-5 seconds ← 60-70% improvement
├─ v2.7 (MEDIUM): 6-8 seconds ← 33% improvement
└─ v2.7 (LOW): 10-15 seconds

Large Project (5000+ files):
├─ v2.6: Crash or hang
├─ v2.7 (HIGH): 15-20 seconds ← Works!
├─ v2.7 (MEDIUM): 25-30 seconds ← Works!
└─ v2.7 (LOW): 45-60 seconds ← Works!
```

**What to Check:**
1. Rendering time acceptable
2. UI remains responsive during render
3. No memory leaks (check with Task Manager)
4. System can handle large projects

---

### ✅ Phase 5: GPU Optimization Verification (10 min)

**If GPU Available (CUDA):**
1. Run audit on large project
2. Monitor GPU usage (nvidia-smi or GPU-Z)
3. Verify GPU is being used
4. Check optimization level = HIGH

**If GPU NOT Available:**
1. Verify optimization level = MEDIUM or LOW
2. Check that system doesn't try to use GPU
3. Verify graceful fallback works

**What to Check:**
1. Correct optimization level detected
2. Performance matches optimization level
3. No GPU errors or fallback crashes

---

### ✅ Phase 6: Backward Compatibility (10 min)

**Test Old Projects (v2.5-v2.6 reports):**
- [ ] Old reports still work
- [ ] Error display works with both formats
- [ ] No data loss
- [ ] No conversion errors

**Test New Features Don't Break Anything:**
- [ ] Error analysis still works
- [ ] Graph visualization still works
- [ ] Tree view still works
- [ ] All menus/buttons work

**What to Check:**
1. Can load old project reports
2. Old data still accessible
3. No new errors/warnings
4. Features work as before

---

## 📊 Issue Tracking Template

If you find issues, document them here:

```
### Issue #N: [Title]

**Severity:** High/Medium/Low
**Feature:** GPU/Clustering/Error Display
**Steps to Reproduce:**
1. ...
2. ...

**Expected:** ...
**Actual:** ...
**Console Output:** (paste here)
**System Info:** 
  - OS: Windows 10/11
  - RAM: X GB
  - GPU: [if applicable]
  - nAUDIT Version: v2.7
```

---

## ✨ Success Criteria

### All Tests PASS if:
- ✅ Application launches without crashes
- ✅ GPU detection works (or graceful fallback)
- ✅ Errors display in tree view
- ✅ Hierarchical clustering visible in graph
- ✅ Performance acceptable
- ✅ No new bugs introduced
- ✅ Old reports still work

### Known Limitations (Not Issues):
- ⚠️ Very large projects (10000+ files) may take > 60 seconds
- ⚠️ GPU support requires NVIDIA GPU (AMD/Intel gracefully fallback)
- ⚠️ Memory usage depends on project size (normal)

---

## 🐛 Debugging Commands

If you encounter issues:

### Check GPU Detection
```bash
cd G:\CODING\nAUDIT
.\v.naudit\Scripts\Activate.ps1
python -c "from n_audit.gui.gpu_detector import GPUDetector; r = GPUDetector.get_system_resources(); print(f'GPU: {r.gpu_available}'); print(f'Level: {r.get_optimization_level()}')"
```

### Check Tree Widget Integration
```bash
python -c "from n_audit.gui.tree_widget import ErrorTreeWidget; print('Tree widget OK')"
```

### Check Graph Visualizer Integration
```bash
python -c "from n_audit.gui.graph_visualizer_v2_6 import GraphVisualizerWidget; print('Graph visualizer OK')"
```

### Run Pre-build Tests
```bash
python pre_build_integration_test.py
python pre_build_qa_checks.py
```

---

## 📈 Expected Results Summary

| Feature | v2.6 | v2.7 | Status |
|---------|------|------|--------|
| GPU Detection | ❌ | ✅ | NEW |
| Performance (HIGH sys) | 8-12s | 3-5s | 60% BETTER |
| Performance (LOW sys) | 50s+ | 45-60s | GRACEFUL |
| Error Display | ❌ BROKEN | ✅ FIXED | FIXED |
| Hierarchical Clustering | ❌ | ✅ | NEW |
| Large Projects (5000+) | 💥 CRASH | ✅ WORKS | FIXED |

---

## 🎯 Test Report Template

Save results as `TEST_REPORT_v2_7_[DATE].md`:

```markdown
# nAUDIT v2.7 - Testing Report

**Date:** [Today]
**Tester:** [Name]
**System:** Windows 10/11, [RAM]GB RAM, [GPU info]

## Test Results

### Phase 1: Launch & GPU Detection
- [ ] PASS
- [ ] FAIL (explain)

### Phase 2: Error Display
- [ ] PASS
- [ ] FAIL (explain)

### Phase 3: Hierarchical Clustering
- [ ] PASS
- [ ] FAIL (explain)

### Phase 4: Performance
- [ ] PASS
- [ ] FAIL (explain)

### Phase 5: GPU Optimization
- [ ] PASS
- [ ] FAIL (explain)

### Phase 6: Backward Compatibility
- [ ] PASS
- [ ] FAIL (explain)

## Summary
Total: [X] PASS, [Y] FAIL

## Issues Found
(List any bugs or problems)

## Notes
(Any additional observations)
```

---

## ✅ Final Verification

After all tests, confirm:

1. ✅ Did GPU detection work? (HIGH/MEDIUM/LOW)
2. ✅ Did errors show in tree widget?
3. ✅ Did hierarchical clustering improve layout?
4. ✅ Was performance acceptable?
5. ✅ Did everything work without crashes?

If YES to all: **🟢 READY FOR RELEASE**

If NO to any: **🔴 NEEDS FIXES**

---

## 🚀 Next Steps After Testing

### If All Tests PASS:
1. Create test report
2. Document results
3. Ready for GitHub release
4. Announce v2.7 features

### If Tests FAIL:
1. Document issues
2. Create bug fix branch
3. Fix issues
4. Re-run tests
5. Repeat until PASS

---

**Testing Status:** 🟡 PENDING  
**Start Time:** [Your time]  
**Estimated Duration:** ~60 minutes  
**Good luck! 🍀**
