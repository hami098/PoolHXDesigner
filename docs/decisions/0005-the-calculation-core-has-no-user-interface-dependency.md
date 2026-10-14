# 5. The calculation core has no user interface dependency

Date: 2026-10-14
Status: accepted

## Context

In the 2022 version the physics and the widgets were the same code. `runprocess4` read
`choose_passd.get()` from a dropdown, computed Reynolds numbers, and opened a
`messagebox.showwarning` about the correlation's validity range, all in one function. A single
formula could not be tested without constructing a Tk window; verifying the old numbers for
this rewrite required monkey patching `mainloop` and `messagebox`.

The author also chose Flet for the new interface, which carries a Flutter engine and is by
far the heaviest thing in the project, against a stated preference for few dependencies.

## Decision

Nothing under `src/pool_heat_exchanger_designer/` outside `user_interface/` may import a user
interface library. The core speaks in frozen dataclasses and raises `DesignError` subclasses;
it never renders and never pops a dialog. Correlation validity is **returned as data**
(`correlation_applied_inside_validated_range`) rather than announced in a modal.

Flet is declared as an optional extra, so `pip install pool-heat-exchanger-designer` installs
numpy and pandas and a working command line, and nothing else.

There are **two** interface extras rather than one, because Flet 1.0 splits its renderer into
separate distributions: `flet-desktop` carries a per platform Flutter binary, `flet-web`
carries the compiled web client plus FastAPI and uvicorn, and the base `flet` package
contains neither. `flet` deals with a missing client by shelling out to `pip install` at
startup and calling `exit(1)` if that fails, which in a container with no outbound network
and a non root user is a hard stop with a confusing message. So:

    pip install ".[desktop-interface]"   # flet[desktop], for the window
    pip install ".[web-interface]"       # flet[web], for the http server and the container

`require_the_client_package` checks for the right client before `flet.run` is called and
raises `GraphicalInterfaceUnavailableError` naming the extra to install, so the failure is a
one line message rather than a failed network install.

## Alternatives considered and rejected

- **Flet as a required dependency.** Simpler packaging, one install path. Rejected: it would
  make a Flutter engine mandatory for a headless container run that never draws a pixel, and
  it would contradict the dependency budget for no gain.
- **One combined `gui` extra pulling `flet[desktop,web]`.** Simpler to document, one command
  covers both modes. Rejected because it puts a roughly 16 MB Flutter desktop binary into a
  container image that only ever serves HTTP, and because the two extras name the two
  deployment paths, which is self documenting.
- **Letting Flet install its own client at first run.** Rejected: it turns the first launch into
  a network operation, it writes into the environment at runtime, and it fails opaquely for a
  non root user in a container.
- **Keeping tkinter, which is in the standard library.** Zero dependencies, and it would have
  been the cheapest answer to the dependency question. Rejected because tkinter in a container
  needs an X server, which makes the Docker requirement unpleasant, and because the author
  wants one codebase that can also be served as a web page.
- **An abstract presenter interface between the core and the interface.** Rejected as
  premature: there is one interface today. The seam that matters is the dataclass boundary,
  and the rule of three applies.

## Consequences

The interface layer has to translate `DesignError` into something a user reads, and has to
decide how to show a correlation that was applied out of range. That translation is interface
work, which is where it belongs.
