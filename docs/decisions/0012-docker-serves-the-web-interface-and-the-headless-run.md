# 12. Docker serves the web interface and the headless run

Date: 2026-10-14
Status: accepted

## Context

The author asked for the project to be containerised. A desktop graphical tool in a container
is usually awkward, because the window needs a display from the host.

It is worth being honest about what containerisation actually buys here, because for a small
Python tool a lock file and one install command already deliver most of the reproducibility.

## Decision

The image exists for the two things a container genuinely does better than a local install:

- **The headless run.** `docker run ... evaluate case.toml` needs no display, no Python on the
  host and no dependency resolution. This is the reproducibility path and the CI path.
- **The web interface.** Flet can serve over HTTP, so the container publishes a port and the
  reviewer opens a browser. No X server, no display forwarding.

Desktop window mode is not supported inside the container.

## Alternatives considered and rejected

- **X11 socket forwarding to run the desktop window from the container.** Rejected: it differs
  on every host operating system, is fragile on Windows and macOS, and the web mode gives the
  same interface with none of it.
- **A VNC or noVNC sidecar.** Rejected: a second server and a browser based remote desktop, to
  avoid a browser based interface that already exists.
- **No Dockerfile, just a lock file.** The honest minimum, and it is what most reviewers would
  actually use. Rejected only because the container is also the thing that makes the web
  interface and the headless run demonstrable in one command on a machine with no Python; the
  lock file is provided as well, not instead.
- **Claiming the container makes results bit for bit reproducible.** Not claimed. It pins the
  interpreter, the libraries and the operating system libraries, which is most of the way
  there. See record 0006.

## Consequences

The entry point has to dispatch between the headless command and the web server, which the
existing `poolhx gui --web --host --port` subcommand already does.
