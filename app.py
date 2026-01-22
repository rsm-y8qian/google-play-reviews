import json
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st


REPO_ROOT = Path(__file__).resolve().parent
RUNS_ROOT = REPO_ROOT / "outputs" / "runs"


def find_latest_run_summary(runs_root: Path) -> Path | None:
    """
    Find the most recently modified run_summary.json under outputs/runs/**/.
    """
    if not runs_root.exists():
        return None

    candidates = list(runs_root.rglob("run_summary.json"))
    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def run_pipeline(url: str, batch_limit: int | None, config: str | None):
    """
    Run pipeline as a subprocess and stream logs live.
    """
    cmd = [sys.executable, "-m", "pipelines.run_pipeline", "--url", url]

    if batch_limit is not None:
        cmd += ["--batch_limit", str(batch_limit)]

    if config:
        cmd += ["--config", config]

    # Start process
    proc = subprocess.Popen(
        cmd,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    return proc, cmd


st.set_page_config(page_title="Google Play Reviews UI", layout="centered")
st.title("Google Play Reviews Pipeline UI")

st.caption("Paste a Google Play app link, click Start, and watch the pipeline run.")

url = st.text_input(
    "Google Play URL",
    placeholder="https://play.google.com/store/apps/details?id=com.openai.chatgpt&hl=en&gl=US",
)

col1, col2 = st.columns(2)
with col1:
    batch_limit = st.number_input("batch_limit (this run)", min_value=50, max_value=5000, value=600, step=50)
with col2:
    config = st.text_input("config (optional)", value="config.yaml")

start = st.button("Start", type="primary")

st.divider()
log_box = st.empty()
summary_box = st.empty()
paths_box = st.empty()

if start:
    if not url.strip():
        st.error("Please paste a Google Play URL first.")
        st.stop()

    # Snapshot "latest summary" before running (so we can detect a new one)
    before = find_latest_run_summary(RUNS_ROOT)
    before_mtime = before.stat().st_mtime if before else 0.0

    st.write("Launching pipeline...")
    proc, cmd = run_pipeline(url=url.strip(), batch_limit=int(batch_limit), config=config.strip())
    st.code(" ".join(cmd), language="bash")

    logs = []
    log_box.code("", language="text")

    # Stream logs live
    while True:
        line = proc.stdout.readline() if proc.stdout else ""
        if line:
            logs.append(line.rstrip("\n"))
            # keep last N lines to avoid UI getting too heavy
            tail = "\n".join(logs[-300:])
            log_box.code(tail, language="text")
        else:
            # No line available
            if proc.poll() is not None:
                break
            time.sleep(0.05)

    rc = proc.returncode
    if rc != 0:
        st.error(f"Pipeline failed (exit code {rc}). See logs above.")
    else:
        st.success("Pipeline finished successfully.")

    # Find new summary
    after = find_latest_run_summary(RUNS_ROOT)
    if after and after.stat().st_mtime > before_mtime:
        try:
            summary = json.loads(after.read_text(encoding="utf-8"))
            summary_box.subheader("Run Summary")
            summary_box.json(summary)

            # Show where files are saved
            outputs = summary.get("outputs", {})
            app = summary.get("app", {})
            paths_box.subheader("Saved Files")
            paths_box.write(f"**App slug:** `{app.get('slug')}`")
            paths_box.write(f"**Raw CSV:** `{outputs.get('raw_csv')}`")
            paths_box.write(f"**Processed:** `{outputs.get('processed_file')}`")
            paths_box.write(f"**Run summary:** `{outputs.get('summary_path')}`")

            # (Optional) quick open hint
            st.info("You can copy the paths above to open files in VS Code / Explorer.")
        except Exception as e:
            st.warning(f"Found summary at {after}, but failed to parse JSON: {e}")
    else:
        st.warning("Could not locate a new run_summary.json under outputs/runs/.")
