from sys import exit as system_exit

def handle_exception(args, exception_type, exception, stack_trace=None):
    exception_dict = {
        "EnvironmentError": f'Environment variable "{exception}" is not set.',
        "SSLError": f'SSL verification failed. IGNORE_SSL_ERRORS is {exception}. Set IGNORE_SSL_ERRORS to True if you want to ignore this error. EXITING.',
        "GitCommandError": f'The repo "{exception}" is not a valid git repo.',
        "GitInvalidRepositoryError": f'The repo "{exception}" is not a valid git repo.',
        "Exception": f'An unknown error occurred: "{exception}"'
    }
    print(args)
    if args.verbose and stack_trace:
        print(stack_trace)
    print(exception_dict[exception_type])
    system_exit(1)