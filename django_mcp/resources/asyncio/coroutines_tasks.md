# Coroutines and Tasks

This section outlines high-level asyncio APIs to work with coroutines and Tasks. Coroutines, Awaitables, Creating Tasks, Task Cancellation, Task Groups, Sleeping, Running Tasks Concurrently, Eager ...

## References

* **Coroutine Source code:** [Lib/asyncio/coroutines.py](https://github.com/python/cpython/tree/3.14/Lib/asyncio/coroutines.py)
* **Tasks Source code:** [Lib/asyncio/tasks.py](https://github.com/python/cpython/tree/3.14/Lib/asyncio/tasks.py)

## Types of Awaitables

We say that an object is **awaitable** if it can be used in an [`await`](https://docs.python.org/3/reference/expressions.html#await) expression. Many asyncio APIs are designed to accept awaitables.

There are three main types of *awaitable* objects:

* Coroutines
* Tasks
* Futures

### Coroutines

Python coroutines can be described in simple words as functions defined with `async def` syntax. When called, they return a coroutine object without actually running the function.

They are *awaitables* and therefore can be awaited from other coroutines:

```python
import asyncio

async def simple_coroutine():
    return 42

async def main():
    print(await simple_coroutine())  # will print "42".

asyncio.run(main())
```

Calling a coroutine nested within another corouting without `await`-ing it will not run the coroutine body but raise a runtime warning as seen below:

```text
RuntimeWarning: coroutine 'my_coroutine' was never awaited
  my_coroutine()
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

> [!IMPORTANT]
> In this documentation the term “coroutine” can be used for two closely related concepts:

### Tasks

*Tasks* are used to schedule coroutines  *concurrently*. Concurrency can be thought of as *running multiple coroutines at the same time in an overlapping manner*.

When a coroutine is wrapped into a *Task* with functions like [`asyncio.create_task()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) the coroutine is automatically scheduled to run soon:

```python
import asyncio

async def scheduled_for_later():
    return 42

async def main():
    # Schedule scheduled_for_later() to run soon concurrently with "main()"
    task = asyncio.create_task(scheduled_for_later())

    # "task" can now be used to cancel "scheduled_for_later()", or
    # can simply be awaited to wait until it is complete:
    await task

asyncio.run(main())
```

In the example below, two coroutines are scheduled concurrently using `asyncio.create_task()` and their results are retrieved using the `result()` method of the Task objects:

```python
import asyncio


async def schedule_for_later():
    return 42


async def schedule_for_later_two():
    return 31


async def main():
    task1 = asyncio.create_task(schedule_for_later())
    task2 = asyncio.create_task(schedule_for_later_two())

    await task1
    await task2

    print(task1.result())  # Output: 42
    print(task2.result())  # Output: 31

asyncio.run(main())
```

### Futures

A [`Future`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future) is a special **low-level** awaitable object that represents an **eventual result** of an asynchronous operation.

In simpler words, a Future is a placeholder for a result that is initially unknown, but will be available at some point in the future.

When a Future object is *awaited* it means that the coroutine will wait until the Future is resolved in some other place.

Future objects in asyncio are needed to allow callback-based code to be used with async/await.

Normally **there is no need** to create Future objects at the application level code.

Future objects, sometimes exposed by libraries and some asyncio APIs, can be awaited:

```python
async def main():
    # Future object is awaited directly
    await function_that_returns_a_future_object()

    # Future object is awaited alongside a coroutine
    await asyncio.gather(
        function_that_returns_a_future_object(),
        some_python_coroutine()
    )
```

A good example of a low-level function that returns a Future object is [`loop.run_in_executor()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor).

## Coroutines

[Coroutines](https://docs.python.org/3/glossary.html#term-coroutine) declared with the async/await syntax is the preferred way of writing asyncio applications. For example, the following snippet of code prints “hello”, waits 1 second, and then prints “world”:

```python
import asyncio

async def main():
    print('hello')
    await asyncio.sleep(1)
    print('world')

asyncio.run(main())
```

> [!WARNING]
> Note that simply calling a coroutine will not schedule it to be executed:
>
> ```python
> main() # This does nothing!
> ```
>
> The output of the above line will be something like:
>
> ```text
> <coroutine object main at 0x1053bb7c8>
> ```

To actually run a coroutine, asyncio provides the following mechanisms:

* [`asyncio.run()`]()
* [`asyncio.create_task()`]()
* [`asyncio.TaskGroup`]()

### Run

`asyncio.run()`

* The function can be used to run the top-level entry point `main()` function (see the above example.)
* Await on a coroutine

The following snippet of code will print “hello” after waiting for 1 second, and then print “world” after waiting for *another* 2 seconds:

```python
async def some_corouting(delay, text):
    await asyncio.sleep(delay)
    print(text)


async def main():
    await some_corouting(4, 'hello')
    await some_corouting(2, 'world')

asyncio.run(main())
```

The coroutines are run sequentially here, so the total wait time is 6 seconds.

Expected output:

```text
hello
world
```

### Create Task

The [`asyncio.create_task()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) function to run coroutines concurrently as asyncio [`Tasks`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task "asyncio.Task").

Let’s modify the above example and run two `say_after` coroutines  *concurrently* :

```python
async def some_corouting(delay, text):
    await asyncio.sleep(delay)
    print(text)


async def main():
    t1 = asyncio.create_task(some_corouting(3, 'hello'))
    t2 = asyncio.create_task(some_corouting(1, 'world'))

    await t1
    await t2

asyncio.run(main())
```

Expected output:

```text
world
hello
```

The total wait time is now only 3 seconds, since both coroutines are run concurrently.

## Tasks

### Creating Tasks

__`asyncio.create_task(coroutine, *, name=None, context=None, eager_start=None,  **kwargs)`__

Wrap the *coroutine* [coroutine](https://docs.python.org/3/library/asyncio-task.html#coroutine) into a [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) and schedule its execution. Return the Task object.

The full function signature is largely the same as that of the [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) constructor (or factory) - all of the keyword arguments to this function are passed through to that interface.

An optional keyword-only *context* argument allows specifying a custom [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context) for the *coroutine* to run in. The current context copy is created when no *context* is provided.

An optional keyword-only *eager_start* argument allows specifying if the task should execute eagerly during the call to create_task, or be scheduled later. If *eager_start* is not passed the mode set by [`loop.set_task_factory()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.set_task_factory "asyncio.loop.set_task_factory") will be used.

The task is executed in the loop returned by [`get_running_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.get_running_loop), [`RuntimeError`](https://docs.python.org/3/library/exceptions.html#RuntimeError) is raised if there is no running loop in current thread.

> [!NOTE]
> [`asyncio.TaskGroup.create_task()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup.create_task) is a new alternative leveraging structural concurrency; it allows for waiting for a group of related tasks with strong safety guarantees.

> [!IMPORTANT]
> Save a reference to the result of this function, to avoid a task disappearing mid-execution. The event loop only keeps weak references to tasks. A task that isn’t referenced elsewhere may get garbage collected at any time, even before it’s done. For reliable “fire-and-forget” background tasks, gather them in a collection:

This example shows how to create and manage multiple background tasks using a set to hold strong references to the tasks (in other word, to prevent them from being garbage collected), ensuring they are not garbage collected before completion:

```python
import asyncio

background_tasks = set()


async def simple_coroutine(param):
    await asyncio.sleep(1)


async def main():
    for i in range(10):
        task = asyncio.create_task(simple_coroutine(param=i))

        # Add task to the set. This creates a strong reference.
        background_tasks.add(task)

        # To prevent keeping references to finished tasks forever,
        # make each task remove its own reference from the set after
        # completion:
        task.add_done_callback(background_tasks.discard)
```

Another example which demonstrates creating multiple tasks to manage their execution concurrently. It will run three instances of `simple_coroutine` concurrently, each fetching data from a different URL:

```python
import asyncio

background_tasks = set()


async def simple_coroutine(url):
    pass


async def main():
    urls = [
        "https://www.example.com",
        "https://www.example.org",
        "https://www.example.net",
    ]

    for url in urls:
        task = asyncio.create_task(simple_coroutine(url))
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

    await asyncio.gather(*background_tasks)
```

Finally, this example illustrates creating and running two tasks concurrently using `asyncio.create_task()`. Each task runs a coroutine that prints a message after a specified delay:

```python
async def some_corouting(delay, text):
    for i in range(3):
        await asyncio.sleep(delay)
        print(f'Task with delay {delay}: {text} ({i})')


async def main():
    t1 = asyncio.create_task(some_corouting(3, 'hello'))
    t2 = asyncio.create_task(some_corouting(1, 'world'))

    await t1
    await t2
```

```text
Task with delay 1: world (0)
Task with delay 1: world (1)
Task with delay 3: hello (0)
Task with delay 1: world (2)
Task with delay 3: hello (1)
Task with delay 3: hello (2)
```

The coroutine with a delay of 1 second prints its message two times before the coroutine with a delay of 3 seconds completes its first print.

> [!IMPORTANT]
> Task Cancellation
>
> Tasks can easily and safely be cancelled. When a task is cancelled, [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) will be raised in the task at the next opportunity.
>
> It is recommended that coroutines use `try/finally` blocks to robustly perform clean-up logic. In case [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) is explicitly caught, it should generally be propagated when clean-up is complete. [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) directly subclasses [`BaseException`](https://docs.python.org/3/library/exceptions.html#BaseException) so most code will not need to be aware of it.
>
> The asyncio components that enable structured concurrency, like [`asyncio.TaskGroup`](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup) and [`asyncio.timeout()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout), are implemented using cancellation internally and might misbehave if a coroutine swallows [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError). Similarly, user code should not generally call [`uncancel`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel). However, in cases when suppressing [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) is truly desired, it is necessary to also call `uncancel()` to completely remove the cancellation state.

### Other ways to run tasks concurrently

#### Gather

_`awaitable asyncio.gather(*aws, return_exceptions=False)`_

Run [awaitable objects](https://docs.python.org/3/library/asyncio-task.html#asyncio-awaitables) in the *aws* sequence  *concurrently* .

> [!NOTE]
> If any awaitable in *aws* is a coroutine, it is automatically scheduled as a Task.
> 
> If all awaitables are completed successfully, the result is an aggregate list of returned values. The order of result values corresponds to the order of awaitables in  *aws* .
> 
> If *return_exceptions* is `False` (default), the first raised exception is immediately propagated to the task that awaits on `gather()`. Other awaitables in the *aws* sequence **won’t be cancelled** and will continue to run.
> 
> If *return_exceptions* is `True`, exceptions are treated the same as successful results, and aggregated in the result list.
> 
> If `gather()` is  *cancelled* , all submitted awaitables (that have not completed yet) are also  *cancelled* .
> 
> If any Task or Future from the *aws* sequence is  *cancelled* , it is treated as if it raised [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) – the `gather()` call is **not** cancelled in this case. This is to prevent the cancellation of one submitted Task/Future to cause other Tasks/Futures to be cancelled.

> [!NOTE]
> A new alternative to create and run tasks concurrently and wait for their completion is [`asyncio.TaskGroup`](#task-groups). *TaskGroup* provides stronger safety guarantees than *gather* for scheduling a nesting of subtasks: if a task (or a subtask, a task scheduled by a task) raises an exception, *TaskGroup* will, while *gather* will not, cancel the remaining scheduled tasks).

Using our database example:

```python
import asyncio


class Database:
    def __init__(self, name):
        self.name = name
        print(f'Instanciated database {self.name}...') # Will print immediately when instance is created

    async def __call__(self, seconds):
        await asyncio.sleep(seconds)
        print(f'  - Database {self.name} initialized in {seconds} seconds.') # Will print after the database is initialized


async def database_one():
    instance = Database('DB1')
    return await instance(5)


async def database_two():
    instance = Database('DB2')
    return await instance(2)


async def main():
    # Gather launches both database initializations concurrently
    # and waits for their completion
    asyncio.gather(database_one(), database_two())
    print('Databases initialized.') # Will print after both databases are initialized
```

> [!IMPORTANT]
> If *return_exceptions* is false, cancelling `gather()` after it has been marked done won’t cancel any submitted awaitables. For instance, gather can be marked done after propagating an exception to the caller, therefore, calling `gather.cancel()` after catching an exception (raised by one of the awaitables) from gather won’t cancel any other awaitables.

#### Task Groups

Task groups combine a task creation API with a convenient and reliable way to wait for all tasks in the group to finish.

__`class asyncio.TaskGroup`__

An [asynchronous context manager](https://docs.python.org/3/reference/datamodel.html#async-context-managers) holding a group of tasks. Tasks can be added to the group using [`create_task()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task). All tasks are awaited when the context manager exits.

__`create_task(coroutine,  *, name=None, context=None, eager_start=None,  **kwargs)`__

Create a task in this task group. The signature matches that of [`asyncio.create_task()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task). If the task group is inactive (e.g. not yet entered, already finished, or in the process of shutting down), we will close the given `coro`.

Example:

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(first_coroutine(...))
        task2 = tg.create_task(second_coroutine(...))

    print(f"Both tasks have completed now: {task1.result()}, {task2.result()}")
```

The ``result()`` method of the tasks can be used to retrieve their results after the task group has finished.

The example below demonstrates creating multiple tasks using `asyncio.TaskGroup` to manage their execution concurrently. It will run three instances of `simple_coroutine` concurrently, each fetching data from a different URL:

```python
import asyncio


async def simple_coroutine(url):
    pass


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(simple_coroutine('https://example.com'))
        tg.create_task(simple_coroutine('https://example.org'))
        tg.create_task(simple_coroutine('https://example.net'))
```

The `async with` statement will wait for all tasks in the group to finish. While waiting, new tasks may still be added to the group (for example, by passing `tg` into one of the coroutines and calling `tg.create_task()` in that coroutine). Once the last task has finished and the `async with` block is exited, no new tasks may be added to the group.

The first time any of the tasks belonging to the group fails with an exception other than [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError), the remaining tasks in the group are cancelled. No further tasks can then be added to the group. At this point, if the body of the `async with` statement is still active (i.e., [`__aexit__()`](https://docs.python.org/3/reference/datamodel.html#object.__aexit__) hasn’t been called yet), the task directly containing the `async with` statement is also cancelled. The resulting [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) will interrupt an `await`, but it will not bubble out of the containing `async with` statement.

Once all tasks have finished, if any tasks have failed with an exception other than [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError), those exceptions are combined in an [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup) or [`BaseExceptionGroup`](https://docs.python.org/3/library/exceptions.html#BaseExceptionGroup) (as appropriate; see their documentation) which is then raised.

Two base exceptions are treated specially: If any task fails with [`KeyboardInterrupt`](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt) or [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit), the task group still cancels the remaining tasks and waits for them, but then the initial [`KeyboardInterrupt`](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt) or [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) is re-raised instead of [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup) or [`BaseExceptionGroup`](https://docs.python.org/3/library/exceptions.html#BaseExceptionGroup).

If the body of the `async with` statement exits with an exception (so [`__aexit__()`](https://docs.python.org/3/reference/datamodel.html#object.__aexit__) is called with an exception set), this is treated the same as if one of the tasks failed: the remaining tasks are cancelled and then waited for, and non-cancellation exceptions are grouped into an exception group and raised. The exception passed into [`__aexit__()`](https://docs.python.org/3/reference/datamodel.html#object.__aexit__), unless it is [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError), is also included in the exception group. The same special case is made for [`KeyboardInterrupt`](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt) and [`SystemExit`](https://docs.python.org/3/library/exceptions.html#SystemExit) as in the previous paragraph.

Task groups are careful not to mix up the internal cancellation used to “wake up” their [`__aexit__()`](https://docs.python.org/3/reference/datamodel.html#object.__aexit__) with cancellation requests for the task in which they are running made by other parties. In particular, when one task group is syntactically nested in another, and both experience an exception in one of their child tasks simultaneously, the inner task group will process its exceptions, and then the outer task group will receive another cancellation and process its own exceptions.

In the case where a task group is cancelled externally and also must raise an [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup), it will call the parent task’s [`cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) method. This ensures that a [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) will be raised at the next [`await`](https://docs.python.org/3/reference/expressions.html#await), so the cancellation is not lost.

Task groups preserve the cancellation count reported by [`asyncio.Task.cancelling()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancelling).

```python
import asyncio


class Database:
    def __init__(self, name):
        self.name = name
        print(f'Instanciated database {self.name}...') # Will print immediately when instance is created

    async def __call__(self, seconds):
        await asyncio.sleep(seconds)
        print(f'  - Database {self.name} initialized in {seconds} seconds.') # Will print after the database is initialized


async def database_one():
    instance = Database('DB1')
    return await instance(5)


async def database_two():
    instance = Database('DB2')
    return await instance(2)


async def main():
    # Using TaskGroup to initialize databases concurrently
    # and wait for their completion
    async with asyncio.TaskGroup() as tg:
        tg.create_task(database_one())
        tg.create_task(database_two())
        print('** Initializing databases...\n') # Will print immediately before databases are initialized
    print('Databases initialized.') # Will print after both databases are initialized
```

The output will be:

```text
** Initializing databases...

Instanciated database DB1...
Instanciated database DB2...
  - Database DB2 initialized in 2 seconds.
  - Database DB1 initialized in 5 seconds.
Databases initialized.
```

#### Terminating a Task Group

While terminating a task group is not natively supported by the standard library, termination can be achieved by adding an exception-raising task to the task group and ignoring the raised exception:

```python
import asyncio
from asyncio import TaskGroup

class TerminateTaskGroup(Exception):
"""Exception raised to terminate a task group."""

async def force_terminate_task_group():
    """Used to force termination of a task group."""
    raise TerminateTaskGroup()

async def job(task_id, sleep_time):
    print(f'Task {task_id}: start')
    await asyncio.sleep(sleep_time)
    print(f'Task {task_id}: done')

async def main():
    try:
        async with TaskGroup() as group:
            # spawn some tasks
            group.create_task(job(1, 0.5))
            group.create_task(job(2, 1.5))
            # sleep for 1 second
            await asyncio.sleep(1)
            # add an exception-raising task to force the group to terminate
            group.create_task(force_terminate_task_group())
    except* TerminateTaskGroup:
        pass

asyncio.run(main())
```

Expected output:

```text
Task 1: start
Task 2: start
Task 1: done
```

### Eager Task Factory

asyncio.eager_task_factory( *loop* ,  *coroutine* ,  *** ,  *name=None* ,  *context=None* )

A task factory for eager task execution.

When using this factory (via [`loop.set_task_factory(asyncio.eager_task_factory)`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.set_task_factory "asyncio.loop.set_task_factory")), coroutines begin execution synchronously during [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) construction. Tasks are only scheduled on the event loop if they block. This can be a performance improvement as the overhead of loop scheduling is avoided for coroutines that complete synchronously.

A common example where this is beneficial is coroutines which employ caching or memoization to avoid actual I/O when possible.

> [!NOTE]
> Immediate execution of the coroutine is a semantic change. If the coroutine returns or raises, the task is never scheduled to the event loop. If the coroutine execution blocks, the task is scheduled to the event loop. This change may introduce behavior changes to existing applications. For example, the application’s task execution order is likely to change.

asyncio.create_eager_task_factory( *custom_task_constructor* )

Create an eager task factory, similar to [`eager_task_factory()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.eager_task_factory "asyncio.eager_task_factory"), using the provided *custom_task_constructor* when creating a new task instead of the default [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task).

*custom_task_constructor* must be a *callable* with the signature matching the signature of [`Task.__init__`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task). The callable must return a [`asyncio.Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task)-compatible object.

This function returns a *callable* intended to be used as a task factory of an event loop via [`loop.set_task_factory(factory)`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.set_task_factory "asyncio.loop.set_task_factory")).

### Shielding From Cancellation

awaitable asyncio.shield(*aw)

Protect an [awaitable object](https://docs.python.org/3/library/asyncio-task.html#asyncio-awaitables) from being [`cancelled`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel).

> [!WARNING]
> If *aw* is a coroutine it is automatically scheduled as a Task.

The statement:

```python
task = asyncio.create_task(something())
res = await shield(task)
```

is equivalent to:

*except* that if the coroutine containing it is cancelled, the Task running in `something()` is not cancelled. From the point of view of `something()`, the cancellation did not happen. Although its caller is still cancelled, so the “await” expression still raises a [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError).

If `something()` is cancelled by other means (i.e. from within itself) that would also cancel `shield()`.

If it is desired to completely ignore cancellation (not recommended) the `shield()` function should be combined with a try/except clause, as follows:

```
task = asyncio.create_task(something())
try:
    res = await shield(task)
except CancelledError:
    res = None
```

Important

Save a reference to tasks passed to this function, to avoid a task disappearing mid-execution. The event loop only keeps weak references to tasks. A task that isn’t referenced elsewhere may get garbage collected at any time, even before it’s done.

Changed in version 3.10: Removed the *loop* parameter.

Deprecated since version 3.10: Deprecation warning is emitted if *aw* is not Future-like object and there is no running event loop.

### Timeouts

#### Timeout

_`asyncio.timeout(*delay)`_

Return an [asynchronous context manager](https://docs.python.org/3/reference/datamodel.html#async-context-managers) that can be used to limit the amount of time spent waiting on something.

*delay* can either be `None`, or a float/int number of seconds to wait. If *delay* is `None`, no time limit will be applied; this can be useful if the delay is unknown when the context manager is created.

In either case, the context manager can be rescheduled after creation using [`Timeout.reschedule()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Timeout.reschedule "asyncio.Timeout.reschedule").

Example:

```python
async def long_task():
    await asyncio.sleep(10)
    return 'Task Complete'


async def main():
    async with asyncio.timeout(5):
        try:
            await long_task()
        except asyncio.CancelledError:
            print('The task timed out!')
```

If `long_task` takes more than 5 seconds to complete, the context manager will cancel the current task and handle the resulting [`asyncio.CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError).

Wrapping the context manager into the try block will transform the `asyncio.CancelledError` into a [`TimeoutError`](https://docs.python.org/3/library/exceptions.html#TimeoutError) which can be caught and handled.

Example of catching [`TimeoutError`](https://docs.python.org/3/library/exceptions.html#TimeoutError):

```python
async def long_task():
    await asyncio.sleep(10)
    return 'Task Complete'


async def main():
    try:
        async with asyncio.timeout(5):
            await long_task()
    except asyncio.TimeoutError:
        print('The task timed out!')
    except Exception as e:
        print(f'An error occurred: {e}')
```

The context manager produced by [`asyncio.timeout()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) can be rescheduled to a different deadline and inspected.

For example

```python
async def main():
    try:
        async with asyncio.timeout(10) as cm:
            # Some code that may take time
            await asyncio.sleep(5)

            # Reschedule the timeout to 3 seconds from now
            new_deadline = asyncio.get_running_loop().time() + 3
            cm.reschedule(new_deadline)

            # More code that may take time
            await asyncio.sleep(5)
    except asyncio.TimeoutError:
        print('The operation timed out.')

    if cm.expired():
        print('The context manager has exceeded its deadline.')
```

> [!NOTE]
> _`classasyncio.Timeout(*when)`_
>
> An [asynchronous context manager](https://docs.python.org/3/reference/datamodel.html#async-context-managers) for cancelling overdue coroutines.
>
> `when` should be an absolute time at which the context should time out, as measured by the event loop’s clock:
>
> when() → [float](https://docs.python.org/3/library/functions.html#float "float")|[None](https://docs.python.org/3/library/constants.html#None "None")
>
> Return the current deadline, or `None` if the current deadline is not set.
>
> reschedule( *when:[float](https://docs.python.org/3/library/functions.html#float "float")|[None](https://docs.python.org/3/library/constants.html#None "None")* )
>
> Reschedule the timeout.
>
> expired() → [bool](https://docs.python.org/3/library/functions.html#bool "bool")
>
> Return whether the context manager has exceeded its deadline (expired).

Timeout context managers can be safely nested.

#### Timeout At

_`asyncio.timeout_at(*when)`_

Similar to [`asyncio.timeout()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout), except *when* is the absolute time to stop waiting, or `None`.

Example:

```python
async def main():
    loop = get_running_loop()
    deadline = loop.time() + 20
    try:
        async with asyncio.timeout_at(deadline):
            await long_running_task()
    except TimeoutError:
        print("The long operation timed out, but we've handled it.")

    print("This statement will run regardless.")
```

#### Wait For

_`asyncasyncio.wait_for(*aws, *timeout)`_

Wait for the *aw* [awaitable](https://docs.python.org/3/library/asyncio-task.html#asyncio-awaitables) to complete with a timeout.

If *aw* is a coroutine it is automatically scheduled as a Task.

*timeout* can either be `None` or a float or int number of seconds to wait for. If *timeout* is `None`, block until the future completes.

If a timeout occurs, it cancels the task and raises [`TimeoutError`](https://docs.python.org/3/library/exceptions.html#TimeoutError).

To avoid the task [`cancellation`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel), wrap it in [`shield()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.shield "asyncio.shield").

The function will wait until the future is actually cancelled, so the total wait time may exceed the  *timeout* . If an exception happens during cancellation, it is propagated.

If the wait is cancelled, the future *aw* is also cancelled.

Example:

```python
async def long_task():
    await asyncio.sleep(10)
    return 'Task Complete'


async def main():
    try:
        await asyncio.wait_for(long_task(), timeout=5)
    except asyncio.TimeoutError:
        print('The task timed out!')
```

### Waiting Primitives

Waiting primitives allow waiting for multiple [`Future`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future) or [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) instances.

#### Wait

_`asyncio.wait(*aws, *, timeout=None, return_when=ALL_COMPLETED)`_

Run [`Future`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future) and [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) instances in the *aws* iterable concurrently and block until the condition specified by  *return_when* .

> [!IMPORTANT]
> The *aws* iterable must not be empty.

Returns two sets of Tasks/Futures: `(done, pending)`.

Usage:

```python
async def long_task():
    await asyncio.sleep(10)
    print('Long Task Complete') # This task will not complete within the timeout


async def another_long_task():
    await asyncio.sleep(5)
    print('Another Long Task Complete')


async def main():
    try:
        t1 = asyncio.create_task(long_task())
        t2 = asyncio.create_task(another_long_task())
        done, pending = await asyncio.wait([t1, t2], timeout=7) # Done and pending contains the set of tasks
    except asyncio.TimeoutError:
        print('The task timed out!')
    else:
        print(f'  - Done tasks: {len(done)}')
        print(f'  - Pending tasks: {len(pending)}')
```

Result:

```text
Another Long Task Complete
  - Done tasks: 1
  - Pending tasks: 1
```

*timeout* (a float or int), if specified, can be used to control the maximum number of seconds to wait before returning.

> [!NOTE]
> Note that this function does not raise [`TimeoutError`](https://docs.python.org/3/library/exceptions.html#TimeoutError). Futures or Tasks that aren’t done when the timeout occurs are simply returned in the second set.

*return_when* indicates when this function should return. It must be one of the following constants:

| Constant                | Description                                                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| asyncio.FIRST_COMPLETED | The function will return when any future finishes or is cancelled.                                                                                           |
| asyncio.FIRST_EXCEPTION | The function will return when any future finishes by raising an exception. If no future raises an exception then it is equivalent to asyncio.FIRST_COMPLETED |
| asyncio.ALL_COMPLETED   | The function will return when all futures finish or are cancelled.                                                                                           |

Unlike [`wait_for()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.wait_for "asyncio.wait_for"), `wait()` does not cancel the futures when a timeout occurs.

#### As Completed

_`asyncio.as_completed(*aws, *, *timeout=None)`_

Run [awaitable objects](https://docs.python.org/3/library/asyncio-task.html#asyncio-awaitables) in the *aws* iterable concurrently. The returned object can be iterated to obtain the results of the awaitables as they finish.

The object returned by `as_completed()` can be iterated as an [asynchronous iterator](https://docs.python.org/3/glossary.html#term-asynchronous-iterator) or a plain [iterator](https://docs.python.org/3/glossary.html#term-iterator). When asynchronous iteration is used, the originally-supplied awaitables are yielded if they are tasks or futures. This makes it easy to correlate previously-scheduled tasks with their results. Example:

```python
async def long_task():
    await asyncio.sleep(3)
    return 'Long Task Complete'


async def another_long_task():
    await asyncio.sleep(1)
    return 'Another Long Task Complete'


async def main():
    t1 = asyncio.create_task(long_task())
    t2 = asyncio.create_task(another_long_task())

    async for completed_task in asyncio.as_completed([t1, t2]):
        result = await completed_task
        print(f'Completed task result: {result}')
```

During asynchronous iteration, implicitly-created tasks will be yielded for supplied awaitables that aren’t tasks or futures:

```text
Completed task result: Another Long Task Complete
Completed task result: Long Task Complete
```

When used as a plain iterator, each iteration yields a new coroutine that returns the result or raises the exception of the next completed awaitable:

```python
async def long_task():
    await asyncio.sleep(3)
    return 'Long Task Complete'


async def another_long_task():
    await asyncio.sleep(1)
    return 'Another Long Task Complete'


async def main():
    t1 = asyncio.create_task(long_task())
    t2 = asyncio.create_task(another_long_task())

    for completed_task in asyncio.as_completed([t1, t2]):
        # completed_task is not one of the original task objects. It must be
        # awaited to obtain the result value or raise the exception of the
        # awaitable that finishes next.
        result = await completed_task
        print(f'Completed task result: {result}')
```

> [!NOTE]
> This pattern is compatible with Python versions older than 3.13

> [!IMPORTANT]
> When using plain iteration, the returned coroutines must be awaited to obtain the result value or raise the exception of the completed awaitable.

A [`TimeoutError`](https://docs.python.org/3/library/exceptions.html#TimeoutError) is raised if the timeout occurs before all awaitables are done. This is raised by the `async for` loop during asynchronous iteration or by the coroutines yielded during plain iteration.

## Running in Threads - [Reference](https://docs.python.org/3/library/asyncio-task.html#running-in-threads)

asyncasyncio.to_thread( *func* ,  */* ,  **args* ,  ***kwargs* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)

Asynchronously run function *func* in a separate thread.

Any *args and **kwargs supplied for this function are directly passed to  *func* . Also, the current [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context) is propagated, allowing context variables from the event loop thread to be accessed in the separate thread.

Return a coroutine that can be awaited to get the eventual result of  *func* .

This coroutine function is primarily intended to be used for executing IO-bound functions/methods that would otherwise block the event loop if they were run in the main thread. For example:

```
defblocking_io():
    print(f"start blocking_io at {time.strftime('%X')}")
    # Note that time.sleep() can be replaced with any blocking
    # IO-bound operation, such as file operations.
    time.sleep(1)
    print(f"blocking_io complete at {time.strftime('%X')}")

async defmain():
    print(f"started main at {time.strftime('%X')}")

    await asyncio.gather(
        asyncio.to_thread(blocking_io),
        asyncio.sleep(1))

    print(f"finished main at {time.strftime('%X')}")


asyncio.run(main())

# Expected output:
#
# started main at 19:50:53
# start blocking_io at 19:50:53
# blocking_io complete at 19:50:54
# finished main at 19:50:54
```

Directly calling `blocking_io()` in any coroutine would block the event loop for its duration, resulting in an additional 1 second of run time. Instead, by using `asyncio.to_thread()`, we can run it in a separate thread without blocking the event loop.

Note

Due to the [GIL](https://docs.python.org/3/glossary.html#term-GIL), `asyncio.to_thread()` can typically only be used to make IO-bound functions non-blocking. However, for extension modules that release the GIL or alternative Python implementations that don’t have one, `asyncio.to_thread()` can also be used for CPU-bound functions.

Added in version 3.9.

### Scheduling From Other Threads

asyncio.run_coroutine_threadsafe( *coroutine* ,  *loop* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.run_coroutine_threadsafe)

Submit a coroutine to the given event loop. Thread-safe.

Return a [`concurrent.futures.Future`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future "concurrent.futures.Future") to wait for the result from another OS thread.

This function is meant to be called from a different OS thread than the one where the event loop is running. Example:

```python
defin_thread(loop: asyncio.AbstractEventLoop) -> None:
    # Run some blocking IO
    pathlib.Path("example.txt").write_text("hello world", encoding="utf8")

    # Create a coroutine
    coro = asyncio.sleep(1, result=3)

    # Submit the coroutine to a given loop
    future = asyncio.run_coroutine_threadsafe(coro, loop)

    # Wait for the result with an optional timeout argument
    assert future.result(timeout=2) == 3

async defamain() -> None:
    # Get the running loop
    loop = asyncio.get_running_loop()

    # Run something in a thread
    await asyncio.to_thread(in_thread, loop)
```

It’s also possible to run the other way around. Example:

```python
@contextlib.contextmanager
defloop_in_thread() -> Generator[asyncio.AbstractEventLoop]:
    loop_fut = concurrent.futures.Future[asyncio.AbstractEventLoop]()
    stop_event = asyncio.Event()

    async defmain() -> None:
        loop_fut.set_result(asyncio.get_running_loop())
        await stop_event.wait()

    with concurrent.futures.ThreadPoolExecutor(1) as tpe:
        complete_fut = tpe.submit(asyncio.run, main())
        for fut in concurrent.futures.as_completed((loop_fut, complete_fut)):
            if fut is loop_fut:
                loop = loop_fut.result()
                try:
                    yield loop
                finally:
                    loop.call_soon_threadsafe(stop_event.set)
            else:
                fut.result()

# Create a loop in another thread
with loop_in_thread() as loop:
    # Create a coroutine
    coro = asyncio.sleep(1, result=3)

    # Submit the coroutine to a given loop
    future = asyncio.run_coroutine_threadsafe(coro, loop)

    # Wait for the result with an optional timeout argument
    assert future.result(timeout=2) == 3
```

If an exception is raised in the coroutine, the returned Future will be notified. It can also be used to cancel the task in the event loop:

```python
try:
    result = future.result(timeout)
except TimeoutError:
    print('The coroutine took too long, cancelling the task...')
    future.cancel()
except Exception as exc:
    print(f'The coroutine raised an exception: {exc!r}')
else:
    print(f'The coroutine returned: {result!r}')
```

See the [concurrency and multithreading](https://docs.python.org/3/library/asyncio-dev.html#asyncio-multithreading) section of the documentation.

Unlike other asyncio functions this function requires the *loop* argument to be passed explicitly.

Added in version 3.5.1.

## Introspection - [Reference](https://docs.python.org/3/library/asyncio-task.html#introspection)

asyncio.current_task( *loop=None* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.current_task)

Return the currently running [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) instance, or `None` if no task is running.

If *loop* is `None` [`get_running_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.get_running_loop) is used to get the current loop.

Added in version 3.7.

asyncio.all_tasks( *loop=None* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.all_tasks)

Return a set of not yet finished [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) objects run by the loop.

If *loop* is `None`, [`get_running_loop()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.get_running_loop) is used for getting current loop.

Added in version 3.7.

asyncio.iscoroutine( *obj* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.iscoroutine)

Return `True` if *obj* is a coroutine object.

Added in version 3.4.

## Task Object

classasyncio.Task( *coroutine* ,  *** ,  *loop=None* ,  *name=None* ,  *context=None* ,  *eager_start=False* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task)

A [`Future-like`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future) object that runs a Python [coroutine](https://docs.python.org/3/library/asyncio-task.html#coroutine). Not thread-safe.

Tasks are used to run coroutines in event loops. If a coroutine awaits on a Future, the Task suspends the execution of the coroutine and waits for the completion of the Future. When the Future is  *done* , the execution of the wrapped coroutine resumes.

Event loops use cooperative scheduling: an event loop runs one Task at a time. While a Task awaits for the completion of a Future, the event loop runs other Tasks, callbacks, or performs IO operations.

Use the high-level [`asyncio.create_task()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) function to create Tasks, or the low-level [`loop.create_task()`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.create_task "asyncio.loop.create_task") or [`ensure_future()`](https://docs.python.org/3/library/asyncio-future.html#asyncio.ensure_future "asyncio.ensure_future") functions. Manual instantiation of Tasks is discouraged.

To cancel a running Task use the [`cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) method. Calling it will cause the Task to throw a [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) exception into the wrapped coroutine. If a coroutine is awaiting on a Future object during cancellation, the Future object will be cancelled.

[`cancelled()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancelled "asyncio.Task.cancelled") can be used to check if the Task was cancelled. The method returns `True` if the wrapped coroutine did not suppress the [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) exception and was actually cancelled.

[`asyncio.Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) inherits from [`Future`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future) all of its APIs except [`Future.set_result()`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future.set_result "asyncio.Future.set_result") and [`Future.set_exception()`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future.set_exception "asyncio.Future.set_exception").

An optional keyword-only *context* argument allows specifying a custom [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context) for the *coroutine* to run in. If no *context* is provided, the Task copies the current context and later runs its coroutine in the copied context.

An optional keyword-only *eager_start* argument allows eagerly starting the execution of the [`asyncio.Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task) at task creation time. If set to `True` and the event loop is running, the task will start executing the coroutine immediately, until the first time the coroutine blocks. If the coroutine returns or raises without blocking, the task will be finished eagerly and will skip scheduling to the event loop.

Changed in version 3.7: Added support for the [`contextvars`](https://docs.python.org/3/library/contextvars.html#module-contextvars "contextvars: Context Variables") module.

Changed in version 3.8: Added the *name* parameter.

Deprecated since version 3.10: Deprecation warning is emitted if *loop* is not specified and there is no running event loop.

Changed in version 3.11: Added the *context* parameter.

Changed in version 3.12: Added the *eager_start* parameter.

done() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.done)

Return `True` if the Task is  *done* .

A Task is *done* when the wrapped coroutine either returned a value, raised an exception, or the Task was cancelled.

result() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.result)

Return the result of the Task.

If the Task is  *done* , the result of the wrapped coroutine is returned (or if the coroutine raised an exception, that exception is re-raised.)

If the Task has been  *cancelled* , this method raises a [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) exception.

If the Task’s result isn’t yet available, this method raises an [`InvalidStateError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.InvalidStateError "asyncio.InvalidStateError") exception.

exception() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.exception)

Return the exception of the Task.

If the wrapped coroutine raised an exception that exception is returned. If the wrapped coroutine returned normally this method returns `None`.

If the Task has been  *cancelled* , this method raises a [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) exception.

If the Task isn’t *done* yet, this method raises an [`InvalidStateError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.InvalidStateError "asyncio.InvalidStateError") exception.

add_done_callback( *callback* ,  *** ,  *context=None* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.add_done_callback)

Add a callback to be run when the Task is  *done* .

This method should only be used in low-level callback-based code.

See the documentation of [`Future.add_done_callback()`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future.add_done_callback "asyncio.Future.add_done_callback") for more details.

remove_done_callback( *callback* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.remove_done_callback)

Remove *callback* from the callbacks list.

This method should only be used in low-level callback-based code.

See the documentation of [`Future.remove_done_callback()`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future.remove_done_callback "asyncio.Future.remove_done_callback") for more details.

get_stack( *** ,  *limit=None* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.get_stack)

Return the list of stack frames for this Task.

If the wrapped coroutine is not done, this returns the stack where it is suspended. If the coroutine has completed successfully or was cancelled, this returns an empty list. If the coroutine was terminated by an exception, this returns the list of traceback frames.

The frames are always ordered from oldest to newest.

Only one stack frame is returned for a suspended coroutine.

The optional *limit* argument sets the maximum number of frames to return; by default all available frames are returned. The ordering of the returned list differs depending on whether a stack or a traceback is returned: the newest frames of a stack are returned, but the oldest frames of a traceback are returned. (This matches the behavior of the traceback module.)

print_stack( *** ,  *limit=None* ,  *file=None* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.print_stack)

Print the stack or traceback for this Task.

This produces output similar to that of the traceback module for the frames retrieved by [`get_stack()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.get_stack "asyncio.Task.get_stack").

The *limit* argument is passed to [`get_stack()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.get_stack "asyncio.Task.get_stack") directly.

The *file* argument is an I/O stream to which the output is written; by default output is written to [`sys.stdout`](https://docs.python.org/3/library/sys.html#sys.stdout "sys.stdout").

get_coro() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.get_coro)

Return the coroutine object wrapped by the [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task).

Note

This will return `None` for Tasks which have already completed eagerly. See the [Eager Task Factory](https://docs.python.org/3/library/asyncio-task.html#eager-task-factory).

Added in version 3.8.

Changed in version 3.12: Newly added eager task execution means result may be `None`.

get_context() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.get_context)

Return the [`contextvars.Context`](https://docs.python.org/3/library/contextvars.html#contextvars.Context) object associated with the task.

Added in version 3.12.

get_name() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.get_name)

Return the name of the Task.

If no name has been explicitly assigned to the Task, the default asyncio Task implementation generates a default name during instantiation.

Added in version 3.8.

set_name( *value* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.set_name)

Set the name of the Task.

The *value* argument can be any object, which is then converted to a string.

In the default Task implementation, the name will be visible in the [`repr()`](https://docs.python.org/3/library/functions.html#repr "repr") output of a task object.

Added in version 3.8.

cancel( *msg=None* ) - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel)

Request the Task to be cancelled.

If the Task is already *done* or  *cancelled* , return `False`, otherwise, return `True`.

The method arranges for a [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) exception to be thrown into the wrapped coroutine on the next cycle of the event loop.

The coroutine then has a chance to clean up or even deny the request by suppressing the exception with a [`try`](https://docs.python.org/3/reference/compound_stmts.html#try) … … `except CancelledError` … [`finally`](https://docs.python.org/3/reference/compound_stmts.html#finally) block. Therefore, unlike [`Future.cancel()`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future.cancel "asyncio.Future.cancel"), [`Task.cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) does not guarantee that the Task will be cancelled, although suppressing cancellation completely is not common and is actively discouraged. Should the coroutine nevertheless decide to suppress the cancellation, it needs to call [`Task.uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel) in addition to catching the exception.

Changed in version 3.9: Added the *msg* parameter.

Changed in version 3.11: The `msg` parameter is propagated from cancelled task to its awaiter.

The following example illustrates how coroutines can intercept the cancellation request:

```
async defcancel_me():
    print('cancel_me(): before sleep')

    try:
        # Wait for 1 hour
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print('cancel_me(): cancel sleep')
        raise
    finally:
        print('cancel_me(): after sleep')

async defmain():
    # Create a "cancel_me" Task
    task = asyncio.create_task(cancel_me())

    # Wait for 1 second
    await asyncio.sleep(1)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("main(): cancel_me is cancelled now")

asyncio.run(main())

# Expected output:
#
#     cancel_me(): before sleep
#     cancel_me(): cancel sleep
#     cancel_me(): after sleep
#     main(): cancel_me is cancelled now
```

cancelled() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancelled)

Return `True` if the Task is  *cancelled* .

The Task is *cancelled* when the cancellation was requested with [`cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) and the wrapped coroutine propagated the [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) exception thrown into it.

uncancel() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel)

Decrement the count of cancellation requests to this Task.

Returns the remaining number of cancellation requests.

Note that once execution of a cancelled task completed, further calls to [`uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel) are ineffective.

Added in version 3.11.

This method is used by asyncio’s internals and isn’t expected to be used by end-user code. In particular, if a Task gets successfully uncancelled, this allows for elements of structured concurrency like [Task Groups](https://docs.python.org/3/library/asyncio-task.html#taskgroups) and [`asyncio.timeout()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.timeout) to continue running, isolating cancellation to the respective structured block. For example:

```
async defmake_request_with_timeout():
    try:
        async with asyncio.timeout(1):
            # Structured block affected by the timeout:
            await make_request()
            await make_another_request()
    except TimeoutError:
        log("There was a timeout")
    # Outer code not affected by the timeout:
    await unrelated_code()
```

While the block with `make_request()` and `make_another_request()` might get cancelled due to the timeout, `unrelated_code()` should continue running even in case of the timeout. This is implemented with [`uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel). [`TaskGroup`](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup) context managers use [`uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel) in a similar fashion.

If end-user code is, for some reason, suppressing cancellation by catching [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError), it needs to call this method to remove the cancellation state.

When this method decrements the cancellation count to zero, the method checks if a previous [`cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) call had arranged for [`CancelledError`](https://docs.python.org/3/library/asyncio-exceptions.html#asyncio.CancelledError) to be thrown into the task. If it hasn’t been thrown yet, that arrangement will be rescinded (by resetting the internal `_must_cancel` flag).

Changed in version 3.13: Changed to rescind pending cancellation requests upon reaching zero.

cancelling() - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancelling)

Return the number of pending cancellation requests to this Task, i.e., the number of calls to [`cancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel) less the number of [`uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel) calls.

Note that if this number is greater than zero but the Task is still executing, [`cancelled()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancelled "asyncio.Task.cancelled") will still return `False`. This is because this number can be lowered by calling [`uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel), which can lead to the task not being cancelled after all if the cancellation requests go down to zero.

This method is used by asyncio’s internals and isn’t expected to be used by end-user code. See [`uncancel()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.uncancel) for more details.

Added in version 3.11.

## Sleeping

_`asyncio.sleep(delay, result=None)`_ - [Reference](https://docs.python.org/3/library/asyncio-task.html#asyncio.sleep)

Block for *delay* seconds.

If *result* is provided, it is returned to the caller when the coroutine completes.

```python
async def waiting_to_print():
    return 'Waited and printed!'


async def main():
    print('Starting wait...')
    # The coroutine will sleep for 3 seconds before proceeding and
    # will return the result of waiting_to_print() after the sleep
    value = await asyncio.sleep(3, result=await waiting_to_print())
    print('Finished waiting:', value)
```

The result parameter in the sleep function can be

`sleep()` always suspends the current task, allowing other tasks to run.

Setting the delay to 0 provides an optimized path to allow other tasks to run. This can be used by long-running functions to avoid blocking the event loop for the full duration of the function call.

Example of coroutine displaying the current date every second for 5 seconds:

```python
import asyncio
import datetime


async def display_date():
    loop = asyncio.get_running_loop()

    end_time = loop.time()+5.0

    while True:
        print(datetime.datetime.now())

        if(loop.time()+1.0)>= end_time:
            break
            await asyncio.sleep(1)

asyncio.run(display_date())
```
