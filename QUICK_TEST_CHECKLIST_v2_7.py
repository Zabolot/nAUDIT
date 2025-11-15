#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Reference - nAUDIT v2.7 Testing Checklist
Быстрая проверка всех новых функций
"""

QUICK_CHECKLIST = """
╔══════════════════════════════════════════════════════════════════╗
║          nAUDIT v2.7 - QUICK TESTING CHECKLIST                  ║
╚══════════════════════════════════════════════════════════════════╝

BEFORE YOU START:
  1. Exe location: G:\\CODING\\nAUDIT\\dist\\nAUDIT.exe
  2. Test project: Any Python project (should have errors)
  3. Check docs: TESTING_GUIDE_v2_7.md for detailed instructions

─────────────────────────────────────────────────────────────────

PHASE 1: LAUNCH & GPU DETECTION (5 min)
─────────────────────────────────────────────────────────────────

[ ] 1. Launch nAUDIT.exe
      Expected: App opens without errors

[ ] 2. Check console for GPU info
      Expected: Shows GPU detection or graceful fallback
      
      Sample output:
      [GPU] GPU Available: True
      [GPU] Model: NVIDIA GeForce RTX 3090
      [GPU] Optimization Level: HIGH

[ ] 3. Check main window loaded
      Expected: All GUI elements visible

─────────────────────────────────────────────────────────────────

PHASE 2: ERROR DISPLAY (10 min)
─────────────────────────────────────────────────────────────────

[ ] 1. Select a test project folder
      Expected: Folder browser opens

[ ] 2. Click \"Start Audit\"
      Expected: Analysis begins

[ ] 3. Wait for completion
      Expected: Progress bar completes

[ ] 4. Check Tree View for Errors
      Expected: \"Code Issues\" category shows errors
      
      Check:
      - Count matches console
      - Can expand/collapse items
      - Error details visible (file, line, message)

[ ] 5. Check Security Issues
      Expected: \"Security Issues\" also displayed

─────────────────────────────────────────────────────────────────

PHASE 3: HIERARCHICAL CLUSTERING (15 min)
─────────────────────────────────────────────────────────────────

[ ] 1. Use project with nested folders
      Example: src/controllers/auth/, src/models/validators/

[ ] 2. Switch to PyVis or Plotly tab
      Expected: Graph visualization appears

[ ] 3. Look for folder clustering
      Expected: Files grouped by folder hierarchy
      
      Visual check:
      - Top-level folders separate
      - Subfolders visible
      - Files organized by folder
      - Not just random positions

[ ] 4. Zoom/Pan in graph
      Expected: Can interact with visualization

[ ] 5. Verify multi-level organization
      Expected: src/ → controllers/ → auth/ visible

─────────────────────────────────────────────────────────────────

PHASE 4: PERFORMANCE (15 min)
─────────────────────────────────────────────────────────────────

[ ] 1. Test with small project (100-500 files)
      [ ] Renders in < 5 seconds
      [ ] Responsive UI
      [ ] No freezing

[ ] 2. Test with medium project (500-2000 files)
      [ ] Renders in < 10 seconds
      [ ] Animations smooth
      [ ] Memory reasonable

[ ] 3. Test with large project (2000+ files)
      [ ] Renders in < 30 seconds
      [ ] System responsive
      [ ] No crashes

─────────────────────────────────────────────────────────────────

PHASE 5: GPU OPTIMIZATION (10 min)
─────────────────────────────────────────────────────────────────

[ ] 1. Check detected optimization level
      Expected: HIGH/MEDIUM/LOW based on system
      
      Mapping:
      GPU + 16GB+ RAM → HIGH
      8GB+ RAM → MEDIUM
      < 8GB RAM → LOW

[ ] 2. Verify performance matches level
      [ ] HIGH: Fast rendering (60-70% improvement)
      [ ] MEDIUM: Good performance
      [ ] LOW: Graceful but slower

[ ] 3. Monitor system resources (Task Manager)
      [ ] CPU usage reasonable
      [ ] Memory stable
      [ ] No spikes/crashes

─────────────────────────────────────────────────────────────────

PHASE 6: BACKWARD COMPATIBILITY (10 min)
─────────────────────────────────────────────────────────────────

[ ] 1. Load old project report (v2.6 era)
      Expected: Still loads without errors

[ ] 2. Verify data still accessible
      Expected: All info visible and correct

[ ] 3. Check no new errors/warnings
      Expected: Backward compatible

[ ] 4. Test all old features still work
      Expected: No regressions

─────────────────────────────────────────────────────────────────

SUMMARY CHECKLIST
─────────────────────────────────────────────────────────────────

NEW FEATURES:
  [ ] GPU Detection working
  [ ] Optimization level correct (HIGH/MEDIUM/LOW)
  [ ] Hierarchical clustering visible
  [ ] Error display working in tree

PERFORMANCE:
  [ ] Small projects fast (< 5 sec)
  [ ] Large projects work (< 30 sec)
  [ ] System remains responsive
  [ ] Memory usage normal

QUALITY:
  [ ] No crashes
  [ ] No error messages
  [ ] Old projects still work
  [ ] All features responsive

─────────────────────────────────────────────────────────────────

IF ALL TESTS PASS:
  ✅ Ready for GitHub release
  ✅ Create TEST_REPORT_v2_7_[DATE].md
  ✅ Push to GitHub with v2.7 tag

IF ANY TEST FAILS:
  ❌ Document issue with steps to reproduce
  ❌ Note system info (GPU, RAM, project size)
  ❌ Create bug report

─────────────────────────────────────────────────────────────────

USEFUL COMMANDS:
─────────────────────────────────────────────────────────────────

Check GPU:
  from n_audit.gui.gpu_detector import GPUDetector
  r = GPUDetector.get_system_resources()
  print(f'GPU: {r.gpu_available}')
  print(f'Level: {r.get_optimization_level()}')

View System Info:
  Open Task Manager (Ctrl+Shift+Esc)
  - Performance tab: See GPU, RAM, CPU
  - App history: Monitor nAUDIT resource usage

Time Graph Rendering:
  1. Start audit
  2. Note time in console when analysis starts
  3. Note time when graph appears
  4. Calculate: appearance_time - start_time

─────────────────────────────────────────────────────────────────

TIPS:
─────────────────────────────────────────────────────────────────

- Test on different projects (small, medium, large)
- Try with different GPU availability (if possible)
- Check both PyVis and Plotly tabs
- Expand tree items to see full error details
- Use zoom/pan features in graph
- Monitor console for any warnings/errors

─────────────────────────────────────────────────────────────────

Time Estimate: 60 minutes total (6 phases × 10 min avg)

Good luck! 🍀

═══════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(QUICK_CHECKLIST)
    print("\nSave this output to: TEST_CHECKLIST_QUICK_v2_7.txt")
    print("Follow the checklist while testing!")
