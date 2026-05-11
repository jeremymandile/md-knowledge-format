/**
 * OpenClaw LESSONS.md Plugin Pack
 *
 * Usage in openclaw.yaml:
 *
 *   hooks:
 *     pre_tool_call:
 *       - name: lesson-guard
 *         command: "python ./node_modules/@md-knowledge-format/openclaw-lessons/lesson_guard.py"
 *     post_failure:
 *       - name: lesson-reporter
 *         command: "python ./node_modules/@md-knowledge-format/openclaw-lessons/lesson_reporter.py"
 *     scheduled:
 *       - name: lesson-digest
 *         command: "python ./node_modules/@md-knowledge-format/openclaw-lessons/lesson_digest.py"
 *         schedule: "0 9 * * 1"  # Every Monday at 9 AM
 */

const path = require("path");

function pluginPath(name) {
  return path.join(__dirname, `${name}.py`);
}

module.exports = {
  guard: pluginPath("lesson_guard"),
  reporter: pluginPath("lesson_reporter"),
  digest: pluginPath("lesson_digest"),
};
