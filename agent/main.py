import argparse
import sys

from agent.loop import run_agent


def main() -> None:
    parser = argparse.ArgumentParser(prog="webact", description="Vision-guided browser agent")
    parser.add_argument("task", help="Plain-English task for the agent")
    parser.add_argument("--max-steps", type=int, default=20, metavar="N",
                        help="Maximum agent steps before giving up (default: 20)")
    args = parser.parse_args()
    result = run_agent(args.task, max_steps=args.max_steps)
    print(result)


if __name__ == "__main__":
    main()
