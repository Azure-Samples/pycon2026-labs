# GitHub Copilot CLI Workshop

You've inherited a broken Python quiz game. Use **GitHub Copilot CLI** to document the functions, write tests, and track down the bug!

---

## Before You Start

Open the terminal and start an interactive GitHub Copilot CLI session:

```bash
copilot
```

If prompted to **trust the files in this folder**, select `Yes`.

> 💡 You'll be chatting with Copilot in natural language from here on. It may ask to use tools (like running shell commands or editing files) — **review and approve each one**.

---

## Choose a Model (1 min)

Before starting, switch Copilot to a model that's well-suited for this task.

1. In the CLI, enter `/model`.
1. Select `Claude Haiku 4.5`.
1. Press **Enter**.

> 💡 Not every task needs the most powerful model. Adding docstrings and writing straightforward tests is well within the capabilities of a smaller, faster model — saving cost without sacrificing quality. Part of working effectively with AI is knowing how to choose the right tool for the job.

---

## Understand the Code (2 min)

The project has three files: `quiz.py`, `utils.py`, and `questions.py`. None of the functions have docstrings, making it harder to follow what each function does.

Ask Copilot to fix that: `Add docstrings to every function in @quiz.py and @utils.py that's missing one.`

> 💡 When typing the file name, a list of matching files will appear. Press **Tab** to select one.

Review the changes Copilot proposes before approving. Once done, take a quick look at the docstrings — do they match what you'd expect each function to do?

---

## Plan a Test Suite (3 min)

Now that the code is documented, switch Copilot to **plan** mode before asking it to write tests.

1. In the CLI, press **`Shift + Tab`** to toggle into plan mode.
1. Submit the prompt: `Create a pytest test suite for the code in the @lab-ghcp-cli/ folder. Write tests for check_answer, calculate_score, format_result, and display_score. Cover normal cases and edge cases. Save the test file as lab-ghcp-cli/test_quiz.py.`

    > Copilot will ask clarifying questions and build a plan. Copilot will likely notice the oustanding bug in the code. If prompted to create a test that'll identify the bug/fail due to the bug), select to do so. 

1. Once Copilot completes the plan, **read the plan carefully** before approving execution. 
1. Once you are ready to approve the plan, choose to `Accept plan and build on default permissions`.
1. Once you approve the plan, Copilot will create a `test_quiz.py` file. If Copilot doesn't request to run the test, you can do so manually:

    ```bash
    ! python -m pytest lab-ghcp-cli/test_quiz.py -v
    ```

    **Note**: You can execute a command in your local shell with the **!** command, bypassing Copilot.
1. Did all the tests pass? If not, which one failed, and why?

---

## Fix the Bug (2 min)

Let's now fix the bug in the `quiz.py` file.

1. Press **`Shift + Tab`** to switch back to standard mode.
1. In the CLI, tell Copilot what you found: `The tests are failing. Based on the test output, find and fix the bug.`
1. Once Copilot applies the fix, run the tests again:

    ```bash
    ! python -m pytest lab-ghcp-cli/test_quiz.py -v
    ```

1. Did all the tests pass? If not, ask GitHub Copilot to fix the bug.

---

## Take the Python Quiz (2 min)

Try taking the quiz! In a new terminal, run the command:

```bash
python lab-ghcp-cli/quiz.py
```

> 💡 Be sure to run this command in a new terminal, **NOT** in the GitHub Copilot CLI.

---

## Reflection

Think about what just happened:

- The bug was in `calculate_score` — a single character caused every quiz score to be undercounted by one.
- There were no tests, so it shipped undetected.
- The missing docstrings made the code ambiguous — even for an AI.

The workflow you just used, `Document → Plan → Test → Fix`, is the same loop developers use. Copilot just helped you do it in 10 minutes!

---

## 🎟️ Congratulations!

Let our staff know that you've completed the lab so that you can collect your swag!
