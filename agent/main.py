import sys


def main(task: str) -> None:
    raise NotImplementedError("Agent loop implemented in M2")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agent.main '<task>'")
        sys.exit(1)
    main(sys.argv[1])
