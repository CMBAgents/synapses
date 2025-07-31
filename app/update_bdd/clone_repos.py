import os
import subprocess
import time
import json
import shutil
import tempfile
import requests
import contextmaker  # ton package python installé

# ==== CONFIG ====

JSON_LIB_PATH = "app/data/libraries.json"  # chemin vers ton fichier json
CHECK_INTERVAL = 10 * 60  # en secondes

OUTPUT_DIR = "/path/to/context_outputs"  # dossier où écrire les outputs
COMMIT_LOG = "commit_log.json"  # fichier pour stocker derniers SHAs

# ==== UTILS ====

def load_repos_from_json(json_path):
    with open(json_path, "r") as f:
        libs = json.load(f)
    repos = []
    for lib in libs:
        url = lib.get("github_url")
        if url:
            repos.append(url)
    return repos

def get_github_latest_commit(repo_url):
    repo_path = repo_url.replace(".git", "").replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/commits"
    r = requests.get(api_url)
    if r.status_code == 200:
        return r.json()[0]["sha"]
    else:
        print(f"Error fetching commits for {repo_url}: {r.status_code}")
        return None

def load_commit_log(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {}

def save_commit_log(path, log):
    with open(path, "w") as f:
        json.dump(log, f)

def run_contextmaker_py(repo_dir, repo_name, output_dir):
    output_file = os.path.join(output_dir, f"{repo_name}_context.txt")
    # Exemple avec contextmaker Python API
    # Adapté selon l'API du package contextmaker
    # Supposons que tu as une fonction contextmaker.generate_context(input_path) -> str
    
    context_text = contextmaker.generate_context(repo_dir)
    with open(output_file, "w") as f:
        f.write(context_text)

def clean_up_dir(dir_path):
    shutil.rmtree(dir_path, ignore_errors=True)

def get_repo_name(repo_url):
    return repo_url.rstrip("/").split("/")[-1].replace(".git", "")

# ==== MAIN LOOP ====

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    commit_log = load_commit_log(COMMIT_LOG)

    while True:
        REPOS = load_repos_from_json(JSON_LIB_PATH)

        for repo_url in REPOS:
            repo_name = get_repo_name(repo_url)
            latest_sha = get_github_latest_commit(repo_url)
            if latest_sha is None:
                continue  # skip if can't fetch

            last_logged_sha = commit_log.get(repo_url)
            if last_logged_sha != latest_sha:
                print(f"[{repo_name}] New commit detected: {latest_sha}")

                tmp_dir = tempfile.mkdtemp()
                try:
                    print(f"[{repo_name}] Cloning into {tmp_dir} ...")
                    subprocess.run(["git", "clone", "--depth", "1", repo_url, tmp_dir], check=True)
                    print(f"[{repo_name}] Running contextmaker ...")
                    run_contextmaker_py(tmp_dir, repo_name, OUTPUT_DIR)
                    print(f"[{repo_name}] Output updated.")
                    commit_log[repo_url] = latest_sha
                    save_commit_log(COMMIT_LOG, commit_log)
                except Exception as e:
                    print(f"[{repo_name}] ERROR: {e}")
                finally:
                    clean_up_dir(tmp_dir)
            else:
                print(f"[{repo_name}] No new commit.")
        print(f"Sleeping for {CHECK_INTERVAL//60} minutes ...\n")
        time.sleep(CHECK_INTERVAL)
