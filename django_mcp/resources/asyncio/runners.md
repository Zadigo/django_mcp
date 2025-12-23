# Runners

## Runners[¶](https://docs.python.org/3/library/asyncio-runner.html#runners "Link to this heading")

**Source code:** [Lib/asyncio/runners.py](https://github.com/python/cpython/tree/3.14/Lib/asyncio/runners.py)

This section outlines high-level asyncio primitives to run asyncio code.

They are built on top of an [event loop](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio-event-loop) with the aim to simplify async code usage for common wide-spread scenarios.

## [Running an asyncio Program](https://docs.python.org/3/library/asyncio-runner.html#id1)[¶](https://docs.python.org/3/library/asyncio-runner.html#running-an-asyncio-program "Link to this heading")

asyncio.run( *coro* ,  *** ,  *debug=None* ,  *loop_factory=None* )[¶](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run)Execute *coro* in an asyncio event loop and return the result.

The argument can be any awaitable object.

This function runs the awaitable, taking care of managing the asyncio event loop,  *finalizing asynchronous generators* , and closing the executor.

This function cannot be called when another asyncio event loop is running in the same thread.

If *debug* is `True`, the event loop will be run in debug mode. `False` disables debug mode explicitly. `None` is used to respect the global [Debug Mode](https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode) settings.

If *loop_factory* is not `None`, it is used to create a new event loop; otherwise [`asyncio.new_event_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.new_event_loop "asyncio.new_event_loop") is used. The loop is closed at the end. This function should be used as a main entry point for asyncio programs, and should ideally only be called once. It is recommended to use *loop_factory* to configure the event loop instead of policies. Passing [`asyncio.EventLoop`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.EventLoop "asyncio.EventLoop") allows running asyncio without the policy system.

The executor is given a timeout duration of 5 minutes to shutdown. If the executor hasn’t finished within that duration, a warning is emitted and the executor is closed.

Example:

```python
async def main():
    await asyncio.sleep(1)
    print('hello')

asyncio.run(main())
```

> [!TIP]
> Added in version 3.7.
>
> Changed in version 3.10: *debug* is `None` by default to respect the global debug mode settings.
> 
> Changed in version 3.12: Added *loop_factory* parameter.
>
> Changed in version 3.14: *coro* can be any awaitable object.

> [!NOTE]
> The `asyncio` policy system is deprecated and will be removed in Python 3.16; from there on, an explicit *loop_factory* is needed to configure the event loop.

## [Runner context manager](https://docs.python.org/3/library/asyncio-runner.html#id2)[¶](https://docs.python.org/3/library/asyncio-runner.html#runner-context-manager "Link to this heading")

classasyncio.Runner( *** ,  *debug=None* ,  *loop_factory=None* )[¶](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner)A context manager that simplifies *multiple* async function calls in the same context.

Sometimes several top-level async functions should be called in the same [event loop](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio-event-loop) and [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context "contextvars.Context").

If *debug* is `True`, the event loop will be run in debug mode. `False` disables debug mode explicitly. `None` is used to respect the global [Debug Mode](https://docs.python.org/3/library/asyncio-dev.html#asyncio-debug-mode) settings.

*loop_factory* could be used for overriding the loop creation. It is the responsibility of the *loop_factory* to set the created loop as the current one. By default [`asyncio.new_event_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.new_event_loop "asyncio.new_event_loop") is used and set as current event loop with [`asyncio.set_event_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.set_event_loop "asyncio.set_event_loop") if *loop_factory* is `None`.

Basically, [`asyncio.run()`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run "asyncio.run") example can be rewritten with the runner usage:

```python 
async def main():
    await asyncio.sleep(1)
    print('hello')

with asyncio.Runner() as runner:
    runner.run(main())
```

> [!TIP]
> Added in version 3.11.

---

[`run(coro, *, context=None)`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner.run)Execute *coro* in the embedded event loop.
: The argument can be any awaitable object.
: If the argument is a coroutine, it is wrapped in a Task.
: An optional keyword-only *context* argument allows specifying a custom [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context "contextvars.Context") for the code to run in. The runner’s default context is used if context is `None`.
: Returns the awaitable’s result or raises an exception.
: This function cannot be called when another asyncio event loop is running in the same thread.

Changed in version 3.14: *coro* can be any awaitable object.

close()[¶](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner.close)Close the runner.

Finalize asynchronous generators, shutdown default executor, close the event loop and release embedded [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context "contextvars.Context").

get_loop()[¶](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner.get_loop)Return the event loop associated with the runner instance.

> [!NOTE]
> [`Runner`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner "asyncio.Runner") uses the lazy initialization strategy, its constructor doesn’t initialize underlying low-level structures.

Embedded *loop* and *context* are created at the [`with`](https://docs.python.org/3/reference/compound_stmts.html#with) body entering or the first call of [`run()`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.run "asyncio.run") or [`get_loop()`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner.get_loop "asyncio.Runner.get_loop").

## [Handling Keyboard Interruption](https://docs.python.org/3/library/asyncio-runner.html#id3)[¶](https://docs.python.org/3/library/asyncio-runner.html#handling-keyboard-interruption "Link to this heading")

Added in version 3.11.

When [`signal.SIGINT`](https://docs.python.org/3/library/signal.html#signal.SIGINT "signal.SIGINT") is raised by Ctrl-C, [`KeyboardInterrupt`](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt "KeyboardInterrupt") exception is raised in the main thread by default. However this doesn’t work with [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio "asyncio: Asynchronous I/O.") because it can interrupt asyncio internals and can hang the program from exiting.

To mitigate this issue, [`asyncio`](https://docs.python.org/3/library/asyncio.html#module-asyncio "asyncio: Asynchronous I/O.") handles [`signal.SIGINT`](https://docs.python.org/3/library/signal.html#signal.SIGINT "signal.SIGINT") as follows:

1. [`asyncio.Runner.run()`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner.run "asyncio.Runner.run") installs a custom [`signal.SIGINT`](https://docs.python.org/3/library/signal.html#signal.SIGINT "signal.SIGINT") handler before any user code is executed and removes it when exiting from the function.
2. The [`Runner`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner "asyncio.Runner") creates the main task for the passed coroutine for its execution.
3. When [`signal.SIGINT`](https://docs.python.org/3/library/signal.html#signal.SIGINT "signal.SIGINT") is raised by Ctrl-C, the custom signal handler cancels the main task by calling [`asyncio.Task.cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel "asyncio.Task.cancel") which raises [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError "asyncio.CancelledError") inside the main task. This causes the Python stack to unwind, `try/except` and `try/finally` blocks can be used for resource cleanup. After the main task is cancelled, [`asyncio.Runner.run()`](https://docs.python.org/3/library/asyncio-runner.html#asyncio.Runner.run "asyncio.Runner.run") raises [`KeyboardInterrupt`](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt "KeyboardInterrupt").
4. A user could write a tight loop which cannot be interrupted by [`asyncio.Task.cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel "asyncio.Task.cancel"), in which case the second following Ctrl-C immediately raises the [`KeyboardInterrupt`](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt "KeyboardInterrupt") without cancelling the main task.
