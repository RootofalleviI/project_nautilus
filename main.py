import cmd
from trackers import *
from lscat import *
from config import *
from tracker.start import start
from tracker.stop import stop


class Interpreter(cmd.Cmd):

    # Hide EOF from showing up in man page
    __hidden_methods = ('do_EOF',)

    intro = "Welcome to Project Nautilus! Type help or ? to list commands."
    prompt = "(project nautilus) "

    # noinspection PyMethodMayBeStatic
    def do_start(self, args):
        """`start <task_name>`: start the timer. `<task_name>` must be registered already."""
        if not args:
            print("ERROR: missing argument: <task_name>.",
                  "`start <task_name>`: start timer. `<task_name>` must be registered already.", sep='\n')
        elif args not in task_keys:
            print(f"ERROR: `{args}` is not registered. You can register it with `add_task {args}`")
        else:
            start(args)

    # noinspection PyMethodMayBeStatic
    def do_stop(self, args):
        """`stop <message>`: stop the tracker and write relevant data to database."""
        if not args:
            print("ERROR: missing argument: <message>.",
                  "`stop <message>`: stop the tracker and write relevant data to database.", sep='\n')
        else:
            stop(args)

    # noinspection PyMethodMayBeStatic
    def do_tasks(self, _):
        """`tasks`: list all registered tasks."""
        print("You have saved the following tasks:")
        print(task_keys)

    # noinspection PyMethodMayBeStatic
    def do_add_task(self, args):
        """`add_task <task_name>`: register a new task."""
        add_task(args.strip())

    # noinspection PyMethodMayBeStatic
    def do_rm_task(self, args):
        """`rm_task <task_name>`: unregister an existing task."""
        rm_task(args.strip())

    # noinspection PyMethodMayBeStatic
    def do_cat(self, args):
        """`cat [<task_name>] [--today|--week|--month|--year]`: see summary on a task in a time period."""
        lscat('cat', args)

    # noinspection PyMethodMayBeStatic
    def do_ls(self, args):
        """`ls [<task_name>] [--today|--week|--month|--year]`: list all records on a task in a time period."""
        lscat('ls', args)

    # noinspection PyMethodMayBeStatic
    def do_add_record(self, args):
        """`add_record [<task_name>]`: add a record."""
        add_record(args)

    # noinspection PyMethodMayBeStatic
    def default(self, _):
        print("Sorry, I don't understand. Please try again.")

    # noinspection PyMethodMayBeStatic
    def do_bye(self, _):
        """`bye`: quit the application."""
        print("Bye")
        return True

    # noinspection PyMethodMayBeStatic
    # noinspection PyPep8Naming
    def do_EOF(self, _):
        print("Bye")
        return True

    def emptyline(self):
        pass

    def get_names(self):
        return [n for n in dir(self.__class__) if n not in self.__hidden_methods]


if __name__ == '__main__':
    Interpreter().cmdloop()
