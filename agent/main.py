import sys

from agent.loop import run_agent


def main(task: str) -> None:
    result = run_agent(task)
    print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m agent.main '<task>'")
        sys.exit(1)
    main(sys.argv[1])
