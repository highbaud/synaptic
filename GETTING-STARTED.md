# Getting Started with Synaptic (Plain-English Guide)

This guide takes you from nothing to a working "second brain" you can ask questions. It assumes you have never opened a terminal or written a line of code. Every step tells you exactly what to type and what you should see afterward.

It takes about 30 minutes. You need a Windows or Mac computer and nothing else. We will install the rest together.

One thing to relax about before you start: **your notes are just plain text files in a normal folder on your computer.** You can copy that folder to back it up, and nothing you do here can quietly corrupt or lock away your writing. If a step goes wrong, you can delete the folder and start over.

---

## The core idea

There are two parts.

1. **Your notes.** A folder of plain text files. You can read and edit them with any app, including the free note-taking app [Obsidian](https://obsidian.md).
2. **Synaptic.** A small program that reads that folder, organizes it, and answers questions about everything in it.

Think of your notes as a library and Synaptic as a librarian who has read every book and never forgets where anything is.

---

## Step 1: Install Python

Synaptic is written in a programming language called Python, so your computer needs Python installed to run it. This is a one-time setup.

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Click the big yellow **Download Python** button.
3. Run the file you downloaded.
4. **On Windows:** on the first screen of the installer, check the box that says **"Add Python to PATH"** before clicking Install. This matters. It lets you run Python by name later.
5. **On Mac:** just click through the installer normally.

To confirm it worked, do Step 2 (open a terminal), then type this and press Enter:

```
python --version
```

You should see something like `Python 3.12.1`. Any version starting with 3.10 or higher is fine. (On some Macs you may need to type `python3` instead of `python`.)

---

## Step 2: Open a terminal

A terminal is a window where you type commands instead of clicking buttons. It looks plain, but it is just a way to tell your computer what to do one line at a time.

- **Windows:** press the Start button, type **Terminal**, and open it.
- **Mac:** press Cmd+Space, type **Terminal**, and open it.

You will see a blinking cursor. That is where you type. After typing a command, press Enter to run it.

---

## Step 3: Download Synaptic

Get the Synaptic folder onto your computer. The simplest way:

1. Go to the Synaptic page on GitHub.
2. Click the green **Code** button, then **Download ZIP**.
3. Unzip it somewhere easy to find, such as your Documents folder.

Now point your terminal at that folder. In the terminal, type `cd ` (the letters c and d, then a space), then drag the unzipped Synaptic folder onto the terminal window and press Enter. That tells the terminal "work inside this folder."

You can confirm you are in the right place by typing `dir` (Windows) or `ls` (Mac) and pressing Enter. You should see file names like `README.md` and `pyproject.toml`.

---

## Step 4: Install Synaptic

Now install the program. Type these lines one at a time, pressing Enter after each.

First, create a private workspace so this install stays separate from everything else on your computer:

```
python -m venv .venv
```

Then turn that workspace on:

```
.\.venv\Scripts\Activate.ps1      (Windows)
source .venv/bin/activate         (Mac)
```

You will know it worked when you see `(.venv)` appear at the start of your terminal line.

Finally, install Synaptic itself:

```
pip install -e .
```

This prints a lot of text and takes a minute. When it stops and gives you the cursor back, it is done.

---

## Step 5: Create your brain

Run this:

```
synaptic init
```

It asks you a few questions. Press Enter to accept the suggested answer, or type your own.

- The first question is where to keep your notes. The suggested location is fine.
- Then it asks: **personal brain or shared team brain?** For your own notes, type `personal` (or just press Enter, which chooses it for you).
- The rest of the questions ask what you use notes for and what you are working on. Answer honestly in a few words, or press Enter to skip. You can edit these answers later.

When it finishes, Synaptic has created a set of folders for you. This is your vault. It includes an inbox for new notes, folders for projects and reference material, and a `CLAUDE.md` file that holds your answers so the assistant knows who you are.

---

## Step 6: Write your first note

Open the vault folder that `synaptic init` just created (it told you the location on screen). Inside it you will find a folder called `00 - INBOX`. That is where new, unsorted thoughts go.

Create a plain text file in that folder and write something real. It can be anything: a thought, a quote you liked, a decision you made. For example, make a file called `first-note.md` containing:

```
Deliberate practice only works when you get feedback on your mistakes,
not just when you repeat something many times.
```

Save it. You can do this with Obsidian, or with any text editor such as Notepad (Windows) or TextEdit (Mac). Make sure the file ends in `.md`, which just means "a plain text note."

---

## Step 7: Let Synaptic read your notes

Back in the terminal, run:

```
synaptic scan
```

This reads every note in your vault and loads it into a small local database on your computer. You will see a short summary of what it found. This is how Synaptic learns what is in your vault. Run it again any time you add or change notes.

---

## Step 8: Ask a question

Now the payoff. Ask your vault something:

```
synaptic query "what do I know about practice?"
```

Synaptic finds the relevant notes and answers using them. With the note from Step 6, it will tell you what you wrote about feedback and practice, and point to the note it used.

That is the whole loop: **write a note, scan, ask.** Everything else Synaptic does builds on those three steps.

---

## Step 9 (optional): Make it smarter with a free local AI

Everything so far works without any AI at all, using simple built-in matching. To get thoughtful, written-out answers, add a free local AI model that runs on your own computer. Nothing you type ever leaves your machine.

1. Go to [ollama.com/download](https://ollama.com/download) and install Ollama.
2. In your terminal, run:
   ```
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```
   The first is a small, fast AI model. The second helps Synaptic understand what notes mean, not just the words they contain.
3. Now run `synaptic scan`, then `synaptic embed`, then ask a question again. The answers will be noticeably better.

If your computer has 16 GB of memory or more, you can pull `llama3.1:8b` for smarter answers. If it is older or slower, `phi3:mini` is lighter.

---

## Step 10 (optional): Let Claude or Codex use your brain

So far you have talked to Synaptic by typing commands in the terminal. You can also let an AI coding assistant, like Claude Code or Codex, read and answer from your vault for you. Then you just chat with the assistant and it pulls from your own notes.

There are two ways, and you can use either.

1. **Let the assistant run the commands for you.** If you already use Claude Code or Codex, you can simply ask it in plain language, for example "scan my vault" or "ask my vault what I know about deliberate practice," and it runs the same `synaptic` commands you have been typing. Nothing to set up.

2. **Plug Synaptic in as a built-in tool (a one-time setup).** You paste a small block of settings into the assistant's config file once. After that, the assistant can search and answer from your vault on its own, without you touching the terminal. The exact block to copy is in the main README, under [Using Synaptic from Claude Code or Codex](README.md#using-synaptic-from-claude-code-or-codex): there is one block for Claude Code and one for Codex.

Good to know: this works the same whether you use Claude or Codex, and it does not move your notes or send them anywhere new. The assistant is just reading the same local files on your computer that Synaptic already reads.

---

## If something goes wrong

**"synaptic: command not found" or "not recognized."**
Your private workspace is probably turned off. Run the activate command from Step 4 again. You should see `(.venv)` at the start of your terminal line before running Synaptic commands.

**"python is not recognized" (Windows).**
Python was installed without being added to PATH. Reinstall Python and check the "Add Python to PATH" box on the first screen.

**On a Mac, `python` does nothing but `python3` works.**
That is normal on some Macs. Use `python3` wherever this guide says `python`.

**The answer to my question says "no relevant notes found."**
Make sure you saved a note in `00 - INBOX` and ran `synaptic scan` afterward. The scan is what teaches Synaptic about new notes.

**I want to start completely over.**
Delete the vault folder and run `synaptic init` again. Your notes are just files, so nothing is hidden or locked.

---

## You cannot break this

Everything Synaptic touches is a plain text file you can open, read, and delete yourself. To back up your whole brain, copy the vault folder somewhere safe. There is no cloud account to lose access to and no hidden format to get trapped in. That is the point: you own the notes, not the tool.

---

## Where to go next

- **The full README** ([README.md](README.md)) explains how everything works and every command available.
- **Daily and weekly habits** are in the [Everyday use](README.md#everyday-use) section. A few minutes a day is what makes the vault get better over time.
- **The skills** in the `skills/` folder are step-by-step playbooks for specific jobs: processing your inbox, writing strong notes, finding connections, and running a weekly review.
