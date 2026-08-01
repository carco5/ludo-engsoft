# forum-cli: read and post comments on the course forum from the terminal

Use this skill whenever the user asks you to post, read or check anything on the
course forum.

The tool is `./forum-cli` in this folder — a command-line program, so you reach it
with the `run_command` tool and nothing else. There is no forum tool in your tool
list; the shell is how you post. Run `./forum-cli --help` if you need to see the
exact options — that is cheaper than carrying them around.

To post a comment, call `run_command` with exactly this shape:

```
./forum-cli post <THREAD_ID> --body "<the comment>"
```

The week-3 thread is thread **1**. Quote the comment body so the shell keeps it
in one piece. The command prints a confirmation line with the timestamp; report
that line back to the user and stop — one post is one command, do not repeat it.

To check what is already there: `./forum-cli read <THREAD_ID>`.
