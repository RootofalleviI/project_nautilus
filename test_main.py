import cmd
from tracker import *
from summary import *

class Interpreter(cmd.Cmd):
    intro = "Welcome to Project Nautilus!"
    prompt = "(project nautilus) "

    def do_start(self, args):
        start(args)

    def do_stop(self, args):
        stop(args)

    def do_tasks(self, args):
        print("You have saved the following tasks:")
        print(task_keys)

    def do_summary(self, args):
        if args in ['', 'today', 'week', 'month', 'year']:
            summary(args)
        else:
            print("Sorry, I don't understand. Please try again.",
                  "Available options for summary: today, week, month, year.",
                  "If no option is provided, it starts from the beginning of your data center.",
                  sep='\n')

    def default(self, args):
        print("Sorry, I don't understand. Please try again.")

    def do_bye(self, args):
        print("Bye")
        return True

    def do_EOF(self, arg):
        print("Bye")
        return True


if __name__ == '__main__':
    Interpreter().cmdloop()
