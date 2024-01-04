#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import os
from pathlib import Path

import typer

from metagpt.config import CONFIG

app = typer.Typer()


current_script_dir = os.path.dirname(os.path.abspath(__file__))
print(current_script_dir)

# Construct the path to the target file
test_file_path = os.path.join(current_script_dir, '../app/test_idea_files/input.txt')
print(test_file_path)
idea = None

with open(test_file_path, "r") as file:
    idea = file.read().strip()

@app.command()
def startup(
    idea: str = typer.Argument(default=idea, help="Your innovative idea, such as 'Create a 2048 game.'"),
    investment: float = typer.Option(default=3.0, help="Dollar amount to invest in the AI company."),
    n_round: int = typer.Option(default=5, help="Number of rounds for the simulation."),
    code_review: bool = typer.Option(default=True, help="Whether to use code review."),
    run_tests: bool = typer.Option(default=False, help="Whether to enable QA for adding & running tests."),
    implement: bool = typer.Option(default=True, help="Enable or disable code implementation."),
    project_name: str = typer.Option(default="beachhead", help="Project name set to 'beachhead'."),
    inc: bool = typer.Option(default=False, help="Incremental mode. Use it to coop with existing repo."),
    project_path: str = typer.Option(
        default="",
        help="Specify the directory path of the old version project to fulfill the " "incremental requirements.",
    ),
    reqa_file: str = typer.Option(default="", help="Specify the source file name for rewriting the quality test code."),
    max_auto_summarize_code: int = typer.Option(
        default=-1,
        help="The maximum number of times the 'SummarizeCode' action is automatically invoked, with -1 indicating unlimited. This parameter is used for debugging the workflow.",
    ),
):
    """Run a startup. Be a boss."""
    from metagpt.roles import (
        Architect,
        Engineer,
        ProductManager,
        ProjectManager,
        QaEngineer,
    )
    from metagpt.team import Team

    # Use in the PrepareDocuments action according to Section 2.2.3.5.1 of RFC 135.
    CONFIG.project_name = "beachhead"  # Setting project name to 'beachhead'
    CONFIG.project_path = Path.cwd() / "beachhead"  # Setting project path to a 'beachhead' directory in the current working directory
    if project_path:
        inc = True
        project_name = project_name or Path(project_path).name
    CONFIG.project_name = project_name
    CONFIG.inc = inc
    CONFIG.reqa_file = reqa_file
    CONFIG.max_auto_summarize_code = max_auto_summarize_code

    company = Team()
    company.hire(
        [
            ProductManager(),
            Architect(),
            ProjectManager(),
        ]
    )

    if implement or code_review:
        company.hire([Engineer(n_borg=5, use_code_review=code_review)])

    if run_tests:
        company.hire([QaEngineer()])

    company.invest(investment)
    company.run_project(idea)
    asyncio.run(company.run(n_round=n_round))


if __name__ == "__main__":
    app()
