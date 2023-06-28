#!/usr/bin/env python3
import os
import re

from colorama import Fore, Style
from git import Repo
from tabulate import tabulate

root_folder = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    ".."
)


def belongs_to_roost(file):
    with open(os.path.join(root_folder, file, ".git/config"), "r") as f:
        return "joinroost" in f.read()


folders = [file for file in os.listdir(root_folder)
           if os.path.isdir(os.path.join(root_folder, file))
           and os.path.exists(os.path.join(root_folder, file, ".git"))
           and belongs_to_roost(file)]

results = []


def boolean_marker(value):
    return "*" if value else ""


def method_name():
    try:
        return len(
            [ref for ref in repo.git.rev_list('--left-right', '@{upstream}...') if ref.startswith(">")])
    except:
        return 0


for folder in folders:
    folder_path = os.path.join(root_folder, folder)
    repo = Repo(folder_path)

    if "origin" in repo.remotes:
        remote_refs = [re.sub("^origin/", "", ref.name) for ref in repo.remotes.origin.refs]

        if os.path.exists(os.path.join(folder_path, "pom.xml")):
            language = "Java"
        elif os.path.exists(os.path.join(folder_path, "package.json")):
            language = "JS"
        else:
            language = ""

        branch = repo.active_branch.name
        is_service = os.path.exists(os.path.join(folder_path, "Dockerfile"))
        is_story = branch not in ["develop", "main", "master"]
        new_branch = branch not in remote_refs
        ahead = 0 if new_branch else method_name()
        needs_push = ahead > 0 or new_branch
        needs_work = is_story or repo.is_dirty() or needs_push
        score = repo.is_dirty() * 90 + needs_push * 100 + is_story * 10

        details = {
            "Name": folder,
            "Language": language,
            "Service": boolean_marker(is_service),
            "Story": boolean_marker(is_story),
            "Dirty": boolean_marker(repo.is_dirty()),
            "Needs push": ahead or boolean_marker(new_branch),
            "Needs work": Fore.YELLOW + boolean_marker(needs_work) + Fore.RESET,
            "Branch": branch
        }

        if not needs_work:
            details = {key: "{}{}{}".format(Style.DIM, value, Style.NORMAL) for (key, value) in details.items()}

        result = {
            "score": score,
            "name": folder,
            "details": details
        }
        results.append(result)

sorted_results = [result["details"] for result in
                  sorted(results, key=lambda r: "{:05d} {}".format(99999 - r["score"], r["name"]))]

print(tabulate([result.values() for result in sorted_results], results[0]["details"].keys(), tablefmt="github"))
