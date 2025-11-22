from src.shell import Shell


def main():
    shell = Shell()
    while True:
        try:
            line = input(f"{shell.pwd}$ ")
            if line.strip().lower() == "exit":
                break
            tokens = line.strip().split()
            shell.execute_command(tokens)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
            continue


if __name__ == "__main__":
    main()
